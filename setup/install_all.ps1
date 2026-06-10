# install_all.ps1 — The Sacred Tech setup wrapper for Windows (PowerShell)
#
# Delegates configuration to the unified Python installer setup/install_all.py.

param (
    [switch]$Minimal,
    [switch]$Full
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "install_all.py"

$pythonCmd = "python"
$hasPython = $false
try {
    & python -c "import sys" >$null 2>&1
    if ($LASTEXITCODE -eq 0) { $hasPython = $true }
} catch {}

if (-not $hasPython) {
    try {
        & py -c "import sys" >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "py"
            $hasPython = $true
        }
    } catch {}
}

if (-not $hasPython) {
    Write-Host "❌  Python not found. Please install Python 3.10+ first."
    exit 1
}

# Translate switches to CLI args
$argsList = @()
if ($Minimal) { $argsList += "--minimal" }
if ($Full) { $argsList += "--full" }

& $pythonCmd $PythonScript $argsList
