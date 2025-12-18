<#
.SYNOPSIS
  Auto-fix Ruff issues and format the backend codebase.
#>

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  Write-Error "Python not found on this machine. Install Python 3.11+ and ensure it is on PATH."
  exit 1
}

python --version
python -m pip --version

python -m pip install --upgrade pip
python -m pip install ruff pytest

Write-Host "Running Ruff auto-fix..."
python -m ruff check backend --fix

Write-Host "Running Ruff formatter (best-effort)..."
try {
  python -m ruff format backend
} catch {
  Write-Warning "Ruff formatter not available; skipping format."
}

Write-Host "Lint fix completed. Review changes, then run .\\scripts\\lint-check.ps1 and .\\scripts\\test.ps1 to confirm."
