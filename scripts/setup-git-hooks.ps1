# PowerShell script to set up git hooks for code quality checks

Write-Host "Setting up git hooks..." -ForegroundColor Cyan

# Run Python setup script
python scripts/setup-git-hooks.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Git hooks setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Hooks installed:" -ForegroundColor Cyan
    Write-Host "  - pre-commit: Runs Ruff linting and formatting (auto-fixes issues)" -ForegroundColor White
    Write-Host "  - pre-push: Runs MyPy type checking on entire project" -ForegroundColor White
    Write-Host "  - prepare-commit-msg: Automatically adds DCO sign-off" -ForegroundColor White
    Write-Host ""
    Write-Host "To test:" -ForegroundColor Yellow
    Write-Host "  - Make a commit to trigger Ruff checks and auto sign-off" -ForegroundColor White
    Write-Host "  - Push to trigger MyPy checks" -ForegroundColor White
} else {
    Write-Host "❌ Failed to setup git hooks" -ForegroundColor Red
    exit 1
}

