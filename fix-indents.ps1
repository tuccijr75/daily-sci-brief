# --- fix-indents.ps1 ---
$ErrorActionPreference = 'Stop'
$Path = "scripts/gather.py"

if (!(Test-Path $Path)) { throw "File not found: $Path (run from repo root)" }

# 1) Backup
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Path "$Path.bak.$stamp"

# 2) Load content
$lines = Get-Content $Path -Encoding UTF8

# 3) Walk through file and insert "pass" after block headers if needed
$new = New-Object System.Collections.Generic.List[string]
for ($i=0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $new.Add($line)

    # If line ends with ":" (block header) and next line is not indented -> insert "pass"
    if ($line -match ':\s*(#.*)?$') {
        $next = if ($i -lt $lines.Count-1) { $lines[$i+1] } else { "" }
        if (-not $next -or $next -notmatch '^\s+') {
            $indent = 0
            if ($line -match '^( +)') { $indent = $matches[1].Length }
            $passLine = (" " * ($indent + 4)) + "pass"
            $new.Add($passLine)
        }
    }
}

# 4) Save back
Set-Content -Path $Path -Value ($new -join "`r`n") -Encoding UTF8

# 5) Syntax check
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

# 6) Commit & push
git add $Path | Out-Null
if (git diff --cached --name-only) {
    git commit -m "fix(gather.py): auto-insert missing 'pass' under block headers to fix IndentationError" | Out-Null
    git push origin main
    Write-Host "🚀 Fix committed and pushed."
} else {
    Write-Host "ℹ️ No changes to commit."
}
