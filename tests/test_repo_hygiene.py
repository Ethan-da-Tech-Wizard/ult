"""Fix 8: licence holder, NOTICE, and no committed PyInstaller build output.
Run: python3 tests/test_repo_hygiene.py
"""
import os
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class Hygiene(unittest.TestCase):
    def test_license_holder_is_github_handle(self):
        self.assertIn("Copyright (c) 2026 Ethan-da-Tech-Wizard", read("LICENSE"))

    def test_notice_lists_third_party_licences(self):
        text = read("NOTICE")
        for needle in ("tauri", "serde", "fastapi", "uvicorn", "pydantic", "numpy", "SIL Open Font License"):
            self.assertIn(needle, text)

    def test_no_tracked_build_artifacts(self):
        try:
            out = subprocess.run(["git", "ls-files", "build", "dist"], cwd=ROOT, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("not a git checkout")
        self.assertEqual(out.strip(), "")

    def test_gitignore_covers_build_output_but_keeps_spec(self):
        text = read(".gitignore")
        self.assertIn("build/", text)
        self.assertIn("dist/", text)
        self.assertIn("!Zeus_Assistant.spec", text)


if __name__ == "__main__":
    unittest.main()
