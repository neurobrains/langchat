# PowerShell script to run all code quality checks

Write-Host "Running Ruff linting..." -ForegroundColor Cyan
python -m ruff check src/ tests/

Write-Host ""
Write-Host "Running ty type checking..." -ForegroundColor Cyan
python -m ty check src/

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
python -m pytest tests/ -v

Write-Host ""
Write-Host "All checks completed!" -ForegroundColor Green

