# PowerShell script to install the DCO sign-off git hook
# This script copies the prepare-commit-msg hook to your .git/hooks directory

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$HookSource = Join-Path $RepoRoot "scripts\prepare-commit-msg"
$HookDest = Join-Path $RepoRoot ".git\hooks\prepare-commit-msg"

if (-not (Test-Path $HookSource)) {
  Write-Host "Error: prepare-commit-msg hook not found at $HookSource" -ForegroundColor Red
  exit 1
}

# Copy the hook
Copy-Item $HookSource $HookDest -Force

Write-Host "✅ DCO sign-off hook installed successfully!" -ForegroundColor Green
Write-Host "The hook will automatically append DCO sign-off to your commit messages."

