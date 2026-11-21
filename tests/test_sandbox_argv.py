"""Fix 3: the container argv built for grading is locked down, and a timeout kills the container by name.

No Docker needed: argv is checked as data and subprocess.run is a recorder.
Run: python3 tests/test_sandbox_argv.py
"""
import os
import subprocess
import sys
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from server import sandbox_manager as sm  # noqa: E402


def flag_value(argv, flag):
    i = argv.index(flag)
    return argv[i + 1]


class RunArgv(unittest.TestCase):
    def setUp(self):
        self.argv = sm.build_run_argv(7, "ult-run-test")

    def test_isolation_flags_present(self):
        a = self.argv
        self.assertEqual(a[:2], ["docker", "run"])
        self.assertIn("--rm", a)
        self.assertEqual(flag_value(a, "--network"), "none")
        self.assertTrue(flag_value(a, "--memory").endswith("m"))
        self.assertEqual(flag_value(a, "--memory-swap"), flag_value(a, "--memory"))
        self.assertTrue(float(flag_value(a, "--cpus")) <= 2)
        self.assertTrue(0 < int(flag_value(a, "--pids-limit")) <= 256)
        self.assertIn("--read-only", a)
        self.assertEqual(flag_value(a, "--cap-drop"), "ALL")
        self.assertIn("no-new-privileges", a)
        self.assertEqual(flag_value(a, "--name"), "ult-run-test")

    def test_non_root_user(self):
        user = flag_value(self.argv, "--user")
        uid = user.split(":")[0]
        self.assertTrue(uid.isdigit() and int(uid) != 0, user)

    def test_validators_and_workspace_read_only(self):
        mounts = [self.argv[i + 1] for i, x in enumerate(self.argv) if x == "-v"]
        sandbox_mounts = [m for m in mounts if m.split(":")[1] == "/sandbox"]
        work_mounts = [m for m in mounts if m.split(":")[1] == "/workspace"]
        self.assertEqual(len(sandbox_mounts), 1)
        self.assertTrue(sandbox_mounts[0].endswith(":ro"), sandbox_mounts)
        self.assertTrue(work_mounts[0].endswith(":ro"), work_mounts)

    def test_runs_validator_for_chapter(self):
        self.assertEqual(self.argv[-2:], ["python", "/sandbox/test_frameworks/ch7_test.py"])

    def test_no_privileged_or_host_namespaces(self):
        for bad in ("--privileged", "--net=host", "--pid=host", "--network=host"):
            self.assertNotIn(bad, self.argv)

    def test_shell_container_also_hardened(self):
        a = sm.build_shell_container_argv()
        self.assertEqual(flag_value(a, "--network"), "none")
        self.assertEqual(flag_value(a, "--cap-drop"), "ALL")
        self.assertIn("no-new-privileges", a)
        self.assertIn("--pids-limit", a)
        mounts = [a[i + 1] for i, x in enumerate(a) if x == "-v"]
        self.assertTrue([m for m in mounts if ":/sandbox" in m][0].endswith(":ro"))


class Timeout(unittest.TestCase):
    def test_timeout_kills_container_by_name(self):
        calls = []

        def fake_run(argv, *a, **k):
            calls.append(list(argv))
            if argv[:2] == ["docker", "run"]:
                raise subprocess.TimeoutExpired(argv, 15)
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.object(sm, "docker_available", lambda: True), \
                mock.patch.object(sm.subprocess, "run", fake_run):
            res = sm.execute_test(3)
        run_argv = [c for c in calls if c[:2] == ["docker", "run"]][0]
        name = flag_value(run_argv, "--name")
        self.assertIn(["docker", "kill", name], calls)
        self.assertFalse(res["success"])
        self.assertIn("timed out", res["output"])


if __name__ == "__main__":
    unittest.main()
