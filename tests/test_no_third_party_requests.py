"""Fix 6: the client must not make third-party requests on load (no remote @import / link / script / img).
Run: python3 tests/test_no_third_party_requests.py
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLIENT = os.path.join(ROOT, "client")
REMOTE = r"(?:https?:)?//(?!127\.0\.0\.1|localhost)"


def read(name):
    with open(os.path.join(CLIENT, name), encoding="utf-8") as f:
        return f.read()


class NoThirdParty(unittest.TestCase):
    def test_css_has_no_remote_urls(self):
        css = read("style.css")
        self.assertIsNone(re.search(r"@import\s+(?:url\()?['\"]?" + REMOTE, css))
        self.assertIsNone(re.search(r"url\(\s*['\"]?" + REMOTE, css))

    def test_html_loads_nothing_remote(self):
        html = read("index.html")
        for tag, attr in (("link", "href"), ("script", "src"), ("img", "src"), ("iframe", "src")):
            for m in re.finditer(r"<%s\b[^>]*\b%s\s*=\s*[\"'](%s[^\"']*)" % (tag, attr, REMOTE), html, re.I):
                self.fail("remote %s %s: %s" % (tag, attr, m.group(1)))

    def test_font_stacks_have_system_fallbacks_and_local_hook(self):
        css = read("style.css")
        self.assertRegex(css, r"--retro-font:[^;]*monospace")
        self.assertTrue(os.path.exists(os.path.join(CLIENT, "fonts", "local-fonts.css")))
        self.assertIn("fonts/local-fonts.css", read("index.html"))


if __name__ == "__main__":
    unittest.main()
