# How this file fits the app: thin PowerShell wrapper around setup/install_all.py (the real installer). It
# only checks that a Python interpreter exists (`python`, else the `py` launcher) and forwards the
# -Minimal / -Full switches as --minimal / --full. With no switch the installer asks questions
# interactively.
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

# Translate PowerShell switches into the Python installer's command-line flags; passing both is not
# blocked here (the Python side rejects the combination because the flags are mutually exclusive).
# Translate switches to CLI args
$argsList = @()
if ($Minimal) { $argsList += "--minimal" }
if ($Full) { $argsList += "--full" }

& $pythonCmd $PythonScript $argsList
