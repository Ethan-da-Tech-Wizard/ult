"""Fix 5: the Tauri wrapper must not enable the `all` allowlist and must ship a real CSP.
Run: python3 tests/test_tauri_config.py
"""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TAURI = os.path.join(ROOT, "client", "src-tauri")


class TauriConfig(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(TAURI, "tauri.conf.json"), encoding="utf-8") as f:
            self.conf = json.load(f)["tauri"]

    def test_no_all_allowlist(self):
        allow = self.conf.get("allowlist", {})
        self.assertNotEqual(allow.get("all"), True)
        for key, value in allow.items():
            if isinstance(value, dict):
                self.assertNotEqual(value.get("all"), True, key)

    def test_real_csp(self):
        csp = self.conf.get("security", {}).get("csp")
        self.assertIsInstance(csp, str)
        self.assertIn("default-src 'self'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertNotRegex(csp, r"script-src[^;]*'unsafe-(inline|eval)'")
        self.assertNotRegex(csp, r"https?://(?!127\.0\.0\.1|localhost)")  # no third-party origins

    def test_cargo_features_not_api_all(self):
        with open(os.path.join(TAURI, "Cargo.toml"), encoding="utf-8") as f:
            text = f.read()
        self.assertIsNone(re.search(r'features\s*=\s*\[[^\]]*"api-all"', text))


if __name__ == "__main__":
    unittest.main()
