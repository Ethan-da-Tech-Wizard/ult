# How this file fits the app: the Windows counterpart of scripts/run_dev.sh. Run it from PowerShell as
# .\scripts\run_dev.ps1. It finds a Python interpreter, makes sure the game's packages exist (creating
# .venv on first launch), prints a notice about optional Docker/QEMU, and starts server/main.py, which
# serves the game on http://127.0.0.1:8000.
# Launches The Sacred Tech on Windows. Self-bootstrapping: if the Python dependencies
# are missing, they are installed into a local .venv automatically.

# Resolve the repository root from this script's location so it works from any current directory, then
# work from there (the server and its relative save_data path expect it).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptDir).Parent.FullName
Set-Location $ProjectRoot

# Interpreter discovery: try `python` first, then the Windows launcher `py`. Only the exit code matters;
# the version text is captured but unused. If neither exists the script stops with exit code 1.
$pythonCmd = "python"
$hasPython = $false
try {
    $verString = & python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -eq 0) {
        $hasPython = $true
    }
} catch {}

if (-not $hasPython) {
    try {
        $verString = & py -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' -ErrorAction SilentlyContinue
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "py"
            $hasPython = $true
        }
    } catch {}
}

if (-not $hasPython) {
    Write-Host "❌  Python not found. Install Python 3.10+ (see README.md) and retry."
    exit 1
}

# Choose which interpreter runs the server: the project's .venv if it already has fastapi, uvicorn and
# numpy (numpy is needed by several chapter validators); otherwise the host Python if it already has them;
# otherwise create .venv and install requirements.txt into it (first launch only).
$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PY = $pythonCmd

$venvOk = $false
if (Test-Path $venvPython) {
    try {
        & $venvPython -c "import fastapi, uvicorn, numpy" >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $venvOk = $true
        }
    } catch {}
}

if ($venvOk) {
    $PY = $venvPython
} else {
    # Check if host system python already has the dependencies
    $hostOk = $false
    try {
        & $pythonCmd -c "import fastapi, uvicorn, numpy" >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $hostOk = $true
        }
    } catch {}

    if (-not $hostOk) {
        Write-Host "[bootstrap] First launch: installing game dependencies into .venv ..."
        if (-not (Test-Path ".venv")) {
            & $pythonCmd -m venv .venv
        }
        & $venvPython -m pip install --quiet --upgrade pip
        & $venvPython -m pip install --quiet -r requirements.txt
        $PY = $venvPython
        Write-Host "[bootstrap] Done."
    }
}

# Static notice that Docker and QEMU are optional; without them the game falls back to the host shell and
# the simulated HolyC altar.
Write-Host ""
Write-Host "=========================================================="
Write-Host " ⚠️  SYSTEM REQUIREMENTS & SETUP NOTICE:"
Write-Host " Core game only requires Python (running now)."
Write-Host " To enable optional Arch Sandbox (T2) & TempleOS VM (T3):"
Write-Host "   - Make sure Docker & QEMU are installed on your host."
Write-Host "   - Run: python setup/install_all.py to build them."
Write-Host "   - If missing, the game falls back to host execution."
Write-Host "=========================================================="
Write-Host ""
Write-Host "▶️   The Sacred Tech is starting..."
Write-Host "    Open http://127.0.0.1:8000 in your browser."
Write-Host ""

# Run the server in the foreground; Ctrl+C stops it. Output stays in this console.
& $PY server/main.py
