# Launches The Sacred Tech on Windows. Self-bootstrapping: if the Python dependencies
# are missing, they are installed into a local .venv automatically.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptDir).Parent.FullName
Set-Location $ProjectRoot

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

& $PY server/main.py
