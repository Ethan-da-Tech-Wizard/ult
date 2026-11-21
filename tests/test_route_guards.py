"""Fix 2: every mutating / code-running / data-returning HTTP route applies the loopback Host + Origin guard.

Uses the same stand-in fastapi modules as tests/test_shell_guard.py when the real fastapi is not installed
(the stub is reused by importing that module); with real fastapi the handlers are plain functions too.
Run: python3 tests/test_route_guards.py
"""
import os
import sys
import types
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_shell_guard as tsg  # noqa: E402  (installs stubs, imports server.main)

main = tsg.main
HTTPException = sys.modules["fastapi"].HTTPException


def req(host="127.0.0.1:8000", origin=None, site=None):
    headers = {"host": host}
    if origin is not None:
        headers["origin"] = origin
    if site is not None:
        headers["sec-fetch-site"] = site
    return types.SimpleNamespace(headers=headers, client=types.SimpleNamespace(host="127.0.0.1"))


CALLS = {
    "save_state": lambda r: main.save_state(types.SimpleNamespace(
        gold=1, compute_tokens=1, unlocked_chapters="0", active_lead="a",
        inventory_json="[]", stats_json="{}", state_json="{}"), r),
    "load_code": lambda r: main.load_code(r, 0, False),
    "compile_code": lambda r: main.compile_code(types.SimpleNamespace(chapter_id=0, code="print(1)"), r),
    "diagnostics": lambda r: main.diagnostics(r),
    "shell_token": lambda r: main.shell_token(r),
    "get_save": lambda r: main.get_save(r),
    "list_saves": lambda r: main.list_saves(r, 10),
    "get_save_by_id": lambda r: main.get_save_by_id(r, 1),
}


class RouteGuards(unittest.TestCase):
    def test_hostile_requests_rejected_everywhere(self):
        hostile = [req(host="evil.example:8000"), req(origin="http://evil.example"),
                   req(origin="null"), req(site="cross-site")]
        for name, call in CALLS.items():
            for r in hostile:
                with self.subTest(route=name, headers=r.headers):
                    with mock.patch.object(main.os, "makedirs", side_effect=AssertionError("ran past guard")):
                        with self.assertRaises(HTTPException) as ctx:
                            call(r)
                    self.assertEqual(ctx.exception.status_code, 403)

    def test_local_request_passes_guard(self):
        r = req(origin="http://127.0.0.1:8000", site="same-origin")
        main.shell_guard.require_local_request(r.headers)  # must not raise

    def test_compile_503_without_docker_and_writes_nothing(self):
        from server import sandbox_manager as sm
        os.environ.pop("ULT_ALLOW_HOST_EXEC", None)
        with mock.patch.object(sm, "docker_available", lambda: False), \
                mock.patch("builtins.open", side_effect=AssertionError("wrote a file")):
            with self.assertRaises(HTTPException) as ctx:
                CALLS["compile_code"](req(origin="http://127.0.0.1:8000"))
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertIn("ULT_ALLOW_HOST_EXEC", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
