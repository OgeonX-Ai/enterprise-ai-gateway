<#
.SYNOPSIS
  Run Ruff lint checks equivalent to CI.
#>

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  Write-Error "Python not found on this machine. Install Python 3.11+ and ensure it is on PATH."
  exit 1
}

python --version
python -m pip --version

python -m pip install --upgrade pip
python -m pip install ruff

Write-Host "Running Ruff lint checks..."
python -m ruff check backend
