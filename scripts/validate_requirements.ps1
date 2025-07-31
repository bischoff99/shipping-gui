# PowerShell script to validate requirements.txt
python -m pip check
if ($LASTEXITCODE -eq 0) {
    Write-Host "All requirements satisfied."
}
else {
    Write-Host "Some dependencies are missing or incompatible. Run 'pip install -r requirements.txt'."
}
