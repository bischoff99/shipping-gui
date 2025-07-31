# Complete project initialization script
# 1. Create venv if missing
# 2. Activate venv
# 3. Install requirements
# 4. Create .env if missing

if (!(Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created."
}

$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Virtual environment activated."
}
else {
    Write-Host "Virtual environment not found."
    exit 1
}

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "Requirements installed."
}
else {
    Write-Host "requirements.txt not found."
}

if (!(Test-Path ".env")) {
    Copy-Item ".env.template" ".env"
    Write-Host ".env file created from template."
}
else {
    Write-Host ".env file already exists."
}
