"""Fix 1: player code must never run on the host unless ULT_ALLOW_HOST_EXEC=1 is set explicitly.

Needs neither Docker nor fastapi: sandbox_manager is stdlib-only and subprocess.run is replaced by a recorder.
Run: python3 tests/test_compile_no_host_exec.py
"""
import logging
import os
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from server import sandbox_manager as sm  # noqa: E402


class Recorder:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, *a, **k):
        self.calls.append(list(argv))
        return mock.Mock(returncode=0, stdout="ok", stderr="")


class NoHostExec(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.NOTSET)
        os.environ.pop("ULT_ALLOW_HOST_EXEC", None)

    def test_docker_absent_refuses_by_default(self):
        rec = Recorder()
        with mock.patch.object(sm, "docker_available", lambda: False), \
                mock.patch.object(sm.subprocess, "run", rec):
            with self.assertRaises(sm.SandboxUnavailable) as ctx:
                sm.execute_test(2)
        self.assertEqual(rec.calls, [], "no process may be started")
        self.assertIn("ULT_ALLOW_HOST_EXEC", str(ctx.exception))
        self.assertIn("Docker", str(ctx.exception))

    def test_only_exact_1_enables_host_exec(self):
        for value, expected in (("1", True), ("true", False), ("0", False), ("", False), ("yes", False)):
            with mock.patch.dict(os.environ, {"ULT_ALLOW_HOST_EXEC": value}):
                self.assertEqual(sm.host_exec_allowed(), expected, value)

    def test_opt_in_runs_on_host_and_warns_loudly(self):
        rec = Recorder()
        with mock.patch.dict(os.environ, {"ULT_ALLOW_HOST_EXEC": "1"}), \
                mock.patch.object(sm, "docker_available", lambda: False), \
                mock.patch.object(sm.subprocess, "run", rec), \
                self.assertLogs("ZeusSandbox", level=logging.WARNING) as logs:
            res = sm.execute_test(2)
        self.assertEqual(len(rec.calls), 1)
        self.assertEqual(rec.calls[0][0], sys.executable)
        self.assertTrue(any("UNSAFE" in line for line in logs.output))
        self.assertTrue(res["success"])


if __name__ == "__main__":
    unittest.main()
