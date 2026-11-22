"""Tests for the /ws/shell access control (server/shell_guard.py and server/main.py ws_shell).

Bug being pinned: /ws/shell used to give ANY connecting page a real shell (host bash when Docker was down) with
no token and no Origin check; WebSockets are exempt from CORS, so any website open in the same browser could
drive it. These tests need neither fastapi nor Docker: main.py is imported against tiny stand-in fastapi/
pydantic/uvicorn modules, the WebSocket is a fake object, and subprocess creation is replaced by a recorder, so
"a shell was started" is directly observable.

Run: python3 tests/test_shell_guard.py   (exit code 0 = all pass)
"""

import asyncio
import importlib
import logging
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
# The handler logs rejections (warning) and, in the "spawn recorded" tests, a deliberate stop error; silence
# them so a green run prints no scary-looking lines.
logging.disable(logging.CRITICAL)
# main.py runs init_db() at import; keep it away from the real save database.
_TMP = tempfile.TemporaryDirectory(prefix="shell-guard-test-")
os.environ["ZEUS_SAVE_DB_PATH"] = os.path.join(_TMP.name, "save_state.db")
os.environ.pop("ZEUS_ALLOW_HOST_SHELL", None)


def install_stub_modules():
    """Registers minimal fastapi/pydantic/uvicorn replacements (only if the real ones are not installed)."""
    try:
        import fastapi  # noqa: F401
        return False
    except ImportError:
        pass

    class HTTPException(Exception):
        def __init__(self, status_code=500, detail=""):
            super().__init__(detail)
            self.status_code, self.detail = status_code, detail

    class WebSocketDisconnect(Exception):
        pass

    class FastAPI:
        """Decorators return the function unchanged so the endpoint can be called directly."""

        def __init__(self, *a, **k):
            pass

        def add_middleware(self, *a, **k):
            pass

        def mount(self, *a, **k):
            pass

        def _decorator(self, *a, **k):
            return lambda fn: fn

        get = post = put = delete = websocket = _decorator

    class JSONResponse:
        def __init__(self, content, headers=None):
            self.content, self.headers = content, headers or {}

    mods = {
        "fastapi": types.ModuleType("fastapi"),
        "fastapi.middleware": types.ModuleType("fastapi.middleware"),
        "fastapi.middleware.cors": types.ModuleType("fastapi.middleware.cors"),
        "fastapi.staticfiles": types.ModuleType("fastapi.staticfiles"),
        "fastapi.responses": types.ModuleType("fastapi.responses"),
        "pydantic": types.ModuleType("pydantic"),
        "uvicorn": types.ModuleType("uvicorn"),
    }
    mods["fastapi"].FastAPI = FastAPI
    mods["fastapi"].HTTPException = HTTPException
    mods["fastapi"].Request = object
    mods["fastapi"].WebSocket = object
    mods["fastapi"].WebSocketDisconnect = WebSocketDisconnect
    mods["fastapi.middleware.cors"].CORSMiddleware = object
    mods["fastapi.staticfiles"].StaticFiles = lambda *a, **k: None
    mods["fastapi.responses"].JSONResponse = JSONResponse
    mods["pydantic"].BaseModel = object
    mods["uvicorn"].run = lambda *a, **k: None
    sys.modules.update(mods)
    return True


install_stub_modules()
main = importlib.import_module("server.main")
guard = main.shell_guard


class FakeWebSocket:
    """Just enough of Starlette's WebSocket for ws_shell: headers, peer, accept/receive/send/close."""

    def __init__(self, origin=None, host="127.0.0.1:8000", client="127.0.0.1", frames=()):
        self.headers = {"host": host}
        if origin is not None:
            self.headers["origin"] = origin
        self.client = types.SimpleNamespace(host=client) if client else None
        self.frames = list(frames)
        self.accepted = False
        self.closed_code = None
        self.sent = []

    async def accept(self):
        self.accepted = True

    async def receive_text(self):
        if not self.frames:
            await asyncio.sleep(60)  # a silent peer: the server's 5 s timeout must end this
        return self.frames.pop(0)

    async def send_text(self, text):
        self.sent.append(text)

    async def close(self, code=1000):
        self.closed_code = code


class ShellGuardUnit(unittest.TestCase):
    def test_origin_rules(self):
        # Pins which pages may talk to the shell: loopback web pages and clients that send no Origin.
        ok = ["http://127.0.0.1:8000", "http://localhost:5173", "https://localhost", "http://[::1]:8000", None]
        bad = ["http://evil.example", "http://127.0.0.1.evil.example", "null", "", "file://localhost/x",
               "http://localhost.evil.example", "chrome-extension://127.0.0.1", "http://evil.example/@127.0.0.1"]
        for origin in ok:
            self.assertTrue(guard.is_local_origin(origin), origin)
        for origin in bad:
            self.assertFalse(guard.is_local_origin(origin), origin)

    def test_host_header_rebinding(self):
        # A rebinding attacker's request carries Host: evil.example; it must be refused.
        self.assertTrue(guard.is_loopback_host("127.0.0.1:8000"))
        self.assertTrue(guard.is_loopback_host("localhost:8000"))
        self.assertTrue(guard.is_loopback_host("[::1]:8000"))
        self.assertFalse(guard.is_loopback_host("evil.example:8000"))
        self.assertFalse(guard.is_loopback_host(None))

    def test_token_compare(self):
        self.assertTrue(guard.token_matches(guard.SHELL_TOKEN))
        self.assertFalse(guard.token_matches("wrong"))
        self.assertFalse(guard.token_matches(""))
        self.assertFalse(guard.token_matches(None))
        self.assertFalse(guard.token_matches(b"bytes"))
        self.assertGreaterEqual(len(guard.SHELL_TOKEN), 32)

    def test_short_env_token_ignored(self):
        # A guessable operator-supplied token must not be adopted.
        with mock.patch.dict(os.environ, {"ZEUS_SHELL_TOKEN": "short"}):
            self.assertNotEqual(guard._load_token(), "short")
        with mock.patch.dict(os.environ, {"ZEUS_SHELL_TOKEN": "x" * 20}):
            self.assertEqual(guard._load_token(), "x" * 20)

    def test_host_shell_is_opt_in(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ZEUS_ALLOW_HOST_SHELL", None)
            self.assertFalse(guard.host_shell_allowed())
        for value, expected in (("1", True), ("true", False), ("0", False), ("", False)):
            with mock.patch.dict(os.environ, {"ZEUS_ALLOW_HOST_SHELL": value}):
                self.assertEqual(guard.host_shell_allowed(), expected, value)


class WsShellFlow(unittest.TestCase):
    """Drives the real ws_shell coroutine and records whether a shell process would have been started."""

    def run_shell(self, ws, docker_running=False, allow_host=False):
        spawned = []

        async def fake_spawn(*cmd, **kwargs):
            spawned.append(list(cmd))
            raise RuntimeError("stop: spawn recorded")  # ends the handler right after the spawn decision

        class FakePopen:
            def read(self_inner):
                return "abc123\n" if docker_running else ""

        env = {"ZEUS_ALLOW_HOST_SHELL": "1"} if allow_host else {}
        with mock.patch.dict(os.environ, env), \
                mock.patch.object(main.os, "popen", lambda *_: FakePopen()), \
                mock.patch.object(main.asyncio, "create_subprocess_exec", fake_spawn), \
                mock.patch.object(main.asyncio, "wait_for", self._fast_wait_for):
            if not allow_host:
                os.environ.pop("ZEUS_ALLOW_HOST_SHELL", None)
            asyncio.run(main.ws_shell(ws))
        return spawned

    @staticmethod
    async def _fast_wait_for(awaitable, timeout):
        # Keep the production 5 s timeout out of the test's runtime but still exercise the timeout path.
        return await _real_wait_for(awaitable, 0.05)

    def test_foreign_origin_rejected_before_accept(self):
        ws = FakeWebSocket(origin="http://evil.example", frames=[guard.SHELL_TOKEN])
        self.assertEqual(self.run_shell(ws, allow_host=True), [])
        self.assertFalse(ws.accepted, "must be refused during the handshake")
        self.assertEqual(ws.closed_code, 1008)

    def test_rebinding_host_rejected(self):
        ws = FakeWebSocket(origin="http://evil.example:8000", host="evil.example:8000", frames=[guard.SHELL_TOKEN])
        self.assertEqual(self.run_shell(ws, allow_host=True), [])
        self.assertFalse(ws.accepted)

    def test_non_loopback_peer_rejected(self):
        ws = FakeWebSocket(client="192.168.1.20", frames=[guard.SHELL_TOKEN])
        self.assertEqual(self.run_shell(ws, allow_host=True), [])
        self.assertFalse(ws.accepted)

    def test_missing_token_rejected(self):
        ws = FakeWebSocket(origin="http://127.0.0.1:8000", frames=[])  # connects, then says nothing
        self.assertEqual(self.run_shell(ws, allow_host=True), [])
        self.assertEqual(ws.closed_code, 1008)

    def test_wrong_token_rejected(self):
        ws = FakeWebSocket(origin="http://127.0.0.1:8000", frames=["guess"])
        self.assertEqual(self.run_shell(ws, allow_host=True), [])
        self.assertEqual(ws.closed_code, 1008)

    def test_host_bash_refused_by_default(self):
        ws = FakeWebSocket(origin="http://127.0.0.1:8000", frames=[guard.SHELL_TOKEN])
        self.assertEqual(self.run_shell(ws, docker_running=False, allow_host=False), [])
        self.assertEqual(ws.closed_code, 1008)
        self.assertTrue(any("ZEUS_ALLOW_HOST_SHELL" in text for text in ws.sent))

    def test_host_bash_when_opted_in(self):
        ws = FakeWebSocket(origin="http://localhost:5173", frames=[guard.SHELL_TOKEN])
        self.assertEqual(self.run_shell(ws, docker_running=False, allow_host=True), [["bash"]])

    def test_docker_shell_with_valid_token(self):
        ws = FakeWebSocket(origin="http://127.0.0.1:8000", frames=[guard.SHELL_TOKEN])
        spawned = self.run_shell(ws, docker_running=True, allow_host=False)
        self.assertEqual(spawned, [["docker", "exec", "-it", "zeus-sandbox", "bash"]])

    def test_token_endpoint_local_only(self):
        def req(**headers):
            return types.SimpleNamespace(headers=headers)

        ok = main.shell_token(req(host="127.0.0.1:8000"))
        self.assertEqual(ok.content, {"token": guard.SHELL_TOKEN})
        self.assertEqual(ok.headers.get("Cache-Control"), "no-store")
        for headers in ({"host": "evil.example"}, {"host": "127.0.0.1:8000", "origin": "http://evil.example"},
                        {"host": "127.0.0.1:8000", "sec-fetch-site": "cross-site"}):
            with self.assertRaises(main.HTTPException) as ctx:
                main.shell_token(req(**headers))
            self.assertEqual(ctx.exception.status_code, 403)


_real_wait_for = asyncio.wait_for

def tearDownModule():
    logging.disable(logging.NOTSET)


if __name__ == "__main__":
    unittest.main(verbosity=1)
