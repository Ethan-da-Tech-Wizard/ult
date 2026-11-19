# How this file fits the app: PyInstaller build recipe for the single-file executable "Zeus_Assistant". It
# is a generated file (PyInstaller writes it when server/build_desktop.py runs) and then committed.
# Caveat: the paths below are absolute and point to /home/user/Ult_Gaming/, which exists only on the
# machine that generated it. server/build_desktop.py does not use this spec (it calls PyInstaller with
# command-line arguments), so the spec is informational unless the paths are rewritten for your checkout.
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    # Analysis entry point and what to bundle: the server's main.py is the program; `datas` copies the
    # client and sandbox folders into the executable's temporary extraction directory (sys._MEIPASS),
    # where main.py and sandbox_manager.py look for them.
    ['/home/user/Ult_Gaming/server/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/user/Ult_Gaming/client', 'client'), ('/home/user/Ult_Gaming/sandbox', 'sandbox')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PYZ = compressed archive of the pure-Python modules.
pyz = PYZ(a.pure)

# EXE options: console=True keeps a terminal window so server logs are visible; upx=True compresses the
# binary if UPX is installed; the other flags are PyInstaller defaults.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Zeus_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
