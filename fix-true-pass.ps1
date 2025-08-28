# --- fix-true-pass.ps1 ---
$ErrorActionPreference = 'Stop'
$Path = "scripts/gather.py"

if (!(Test-Path $Path)) { throw "File not found: $Path (run from repo root)" }

# 1) Backup
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Path "$Path.bak.$stamp"

# 2) Clean up any "True    pass" or "True pass"
$content = Get-Content $Path -Raw -Encoding UTF8
$content = $content -replace 'True\s+pass', 'pass'
Set-Content -Path $Path -Value $content -Encoding UTF8

# 3) Syntax check with Python
$python = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $python = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }
if (-not $python) { throw "Python not found in PATH." }

Write-Host "🔎 Running syntax check..."
& $python -m py_compile $Path
if ($LASTEXITCODE -ne 0) {
    throw "❌ Python syntax check failed. Please check the file."
} else {
    Write-Host "✅ Python syntax looks good."
}

# 4) Commit & push
git add $Path | Out-Null
if (git diff --cached --name-only) {
    git commit -m "fix(gather.py): replace stray 'True pass' with 'pass' to fix syntax error" | Out-Null
    git push origin main
    Write-Host "🚀 Fix committed and pushed."
} else {
    Write-Host "ℹ️ No changes to commit."
}
