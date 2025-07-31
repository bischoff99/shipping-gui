# PowerShell script to activate the virtual environment
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
}
else {
    Write-Host "Virtual environment not found. Run 'python -m venv .venv' first."
}
