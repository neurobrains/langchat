# PowerShell script to clean up project cache and temporary files

Write-Host "Cleaning up project..." -ForegroundColor Cyan

# Remove cache directories
Write-Host "Removing cache directories..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter ".mypy_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter ".ruff_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Remove compiled Python files
Write-Host "Removing compiled Python files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyd" -ErrorAction SilentlyContinue | Remove-Item -Force

# Remove build artifacts
Write-Host "Removing build artifacts..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Filter "*.egg-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter "build" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Directory -Filter "dist" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Remove OS-specific files
Write-Host "Removing OS-specific files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter ".DS_Store" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "Thumbs.db" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Directory -Filter "__MACOSX" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Remove temporary files
Write-Host "Removing temporary files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "*.tmp" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.bak" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.backup" -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green

