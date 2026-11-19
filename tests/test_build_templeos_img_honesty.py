"""Regression test: setup/build_templeos_img.sh must say plainly that it only creates a BLANK disk.

Before the fix the banner said it "builds a headless TempleOS serial console image" and the last line said
the game server "will mount this disk", although the script only downloads the ISO and runs `qemu-img create`
(no OS is installed, the ISO is not attached), so the disk cannot boot. The test copies the script into a
temp tree, puts fake qemu-img / qemu-system-x86_64 / curl first on PATH (no network, no QEMU needed) and
checks the text it prints.

Run: python3 tests/test_build_templeos_img_honesty.py
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def write_exe(path, body):
    """Writes a small shell script and marks it executable."""
    with open(path, "w") as f:
        f.write("#!/usr/bin/env bash\n" + body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


def main():
    with tempfile.TemporaryDirectory(prefix="templeos-honesty-") as tmp:
        # Script location decides SAVE_DIR (<root>/save_data), so mirror the repo layout.
        os.makedirs(os.path.join(tmp, "setup"))
        script = os.path.join(tmp, "setup", "build_templeos_img.sh")
        shutil.copy(os.path.join(ROOT, "setup", "build_templeos_img.sh"), script)

        bindir = os.path.join(tmp, "bin")
        os.makedirs(bindir)
        write_exe(os.path.join(bindir, "qemu-system-x86_64"), 'echo "QEMU emulator version 0.0 (fake)"\n')
        # qemu-img create -f raw <path> <size>: create an empty file at <path>.
        write_exe(os.path.join(bindir, "qemu-img"), 'touch "$4"\n')
        # curl -L --fail --progress-bar <url> -o <path>: write a dummy ISO.
        write_exe(os.path.join(bindir, "curl"), 'for last; do :; done; echo fake > "$last"\n')

        env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"])
        env.pop("TEMPLEOS_ISO_URL", None)
        run = subprocess.run(["bash", script], env=env, capture_output=True, text=True, timeout=60)
        out = run.stdout + run.stderr
        assert run.returncode == 0, out
        assert os.path.exists(os.path.join(tmp, "save_data", "templeos_core.img"))

    assert "BLANK" in out, "output must state the disk is blank"
    assert "NOT installed" in out or "not installed" in out, "output must say no OS is installed"
    for phrase in ("builds a headless TempleOS serial console image", "game server will mount this disk"):
        assert phrase not in out, f"misleading claim still printed: {phrase!r}"
    print("PASS test_build_templeos_img_honesty")


if __name__ == "__main__":
    sys.exit(main())
