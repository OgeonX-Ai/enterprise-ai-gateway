<#
.SYNOPSIS
  Run pytest similar to CI with dependency installation and friendly skip when tests are absent.
#>

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  Write-Error "Python not found on this machine. Install Python 3.11+ and ensure it is on PATH."
  exit 1
}

python --version
python -m pip --version

python -m pip install --upgrade pip

if (Test-Path "backend/requirements.txt") {
  Write-Host "Installing backend requirements..."
  python -m pip install -r backend/requirements.txt
} elseif (Test-Path "requirements.txt") {
  Write-Host "Installing root requirements..."
  python -m pip install -r requirements.txt
} else {
  Write-Host "No requirements.txt found. Skipping app deps."
}

python -m pip install pytest

$patterns = @("test_*.py", "*_test.py")
$testFiles = @()
if (Test-Path "backend") {
  $testFiles += Get-ChildItem -Path backend -Recurse -Include $patterns -File
}
$testFiles += Get-ChildItem -Path . -Recurse -Include $patterns -File
$testFiles = $testFiles | Select-Object -Unique

if (-not $testFiles) {
  Write-Host "No tests found. Skipping pytest."
  exit 0
}

Write-Host "Running pytest..."
if (Test-Path "backend") {
  python -m pytest -q backend
} else {
  python -m pytest -q
}
