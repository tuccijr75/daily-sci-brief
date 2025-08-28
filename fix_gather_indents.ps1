# fix_gather_indents.ps1
$ErrorActionPreference = 'Stop'
$Path = "scripts/gather.py"
if (!(Test-Path $Path)) { throw "File not found: $Path (run from repo root)" }

function Get-PrevSigIndex([string[]]$lines, [int]$startIdx) {
  for ($j=$startIdx; $j -ge 0; $j--) {
    $t = $lines[$j].Trim()
    if ($t -ne '' -and -not $t.StartsWith('#')) { return $j }
  }
  return -1
}
function Get-IndentCount([string]$line) { return ([regex]::Match($line,'^( +)')).Length }

# Choose Python
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
if (-not $py -and (Get-Command python -ErrorAction SilentlyContinue)) { $py = "python" }
if (-not $py) { throw "Python not found in PATH." }

# Backup
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Path "$Path.bak.$stamp"

# Normalize & clean simple debris
$content = Get-Content $Path -Raw -Encoding UTF8
$content = $content -replace "`t","    "
$content = $content -replace "[\u200B-\u200D\u2060]",""
$content = $content -replace '^\s*True\s+pass\s*$','pass' -replace 'True\s+pass','pass'
Set-Content -Path $Path -Value $content -Encoding UTF8

$maxPasses = 60
for ($n=1; $n -le $maxPasses; $n++) {
  # Compile and capture stderr
  $tmp = New-TemporaryFile
  & $py -m py_compile $Path 2> $tmp.FullName
  $err = Get-Content $tmp.FullName -Raw -ErrorAction SilentlyContinue
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue

  if ($LASTEXITCODE -eq 0 -or -not $err) { Write-Host "✅ Syntax OK after pass $n."; break }

  # Try to extract the failing line
  $ln = $null
  if ($err -match 'IndentationError:.*\(.*?, line (\d+)\)') { $ln = [int]$matches[1] }
  elseif ($err -match 'expected an indented block.*line (\d+)') { $ln = [int]$matches[1] }
  elseif ($err -match 'line\s+(\d+)\s*\)') { $ln = [int]$matches[1] }
  if (-not $ln) { throw "Unfixed error (no line parsed):`n$err" }

  Write-Host "⚠️  Fixing indentation at line $ln (pass $n)..." -ForegroundColor Yellow

  $lines = Get-Content $Path -Encoding UTF8
  $idx = $ln - 1
  if ($idx -lt 0 -or $idx -ge $lines.Count) { throw "Parsed bad line index $ln" }

  # Compute target indent from previous significant line (+4 if that line ends with ':')
  $prevIdx = Get-PrevSigIndex $lines ($idx-1)
  $target = 0
  if ($prevIdx -ge 0) {
    $prev = $lines[$prevIdx]
    $target = Get-IndentCount $prev
    if ($prev.Trim().EndsWith(':')) { $target += 4 }
  }

  $thisIsHeader = $lines[$idx].Trim().EndsWith(':')

  if ($thisIsHeader) {
    # Align header to target
    $trim = $lines[$idx].TrimStart()
    $lines[$idx] = (' ' * $target) + $trim

    # Ensure body exists and is more indented than header
    $k = $idx + 1
    while ($k -lt $lines.Count -and ($lines[$k].Trim() -eq '' -or $lines[$k].Trim().StartsWith('#'))) { $k++ }
    $needPass = $false
    if ($k -ge $lines.Count) {
      $needPass = $true
    } else {
      $nextIndent = Get-IndentCount $lines[$k]
      $hdrIndent  = Get-IndentCount $lines[$idx]
      if ( ($nextIndent -le $hdrIndent) ) { $needPass = $true }
    }
    if ($needPass) {
      $passLine = (' ' * ((Get-IndentCount $lines[$idx]) + 4)) + 'pass'
      if ($idx -eq $lines.Count-1) {
        $lines += $passLine
      } else {
        $before = @()
        if ($idx -ge 0) { $before = $lines[0..$idx] }
        $after = @()
        if ($idx + 1 -le $lines.Count - 1) { $after = $lines[($idx+1)..($lines.Count-1)] }
        $lines = $before + $passLine + $after
      }
    }
  } else {
    # Regular line: align to target
    $trim = ($lines[$idx] -replace '^\s*','')
    $lines[$idx] = (' ' * $target) + $trim
  }

  Set-Content -Path $Path -Value ($lines -join "`r`n") -Encoding UTF8
}

if ($LASTEXITCODE -ne 0) { throw "❌ Still failing to compile after $maxPasses passes. See the last compiler output above." }

# Commit & push if changed
git add $Path | Out-Null
if (git diff --cached --name-only) {
  git commit -m "fix(gather.py): auto-correct indentation; insert pass where required; normalize whitespace; remove 'True pass' debris" | Out-Null
  git push origin main
  Write-Host "✅ Fix committed and pushed."
} else {
  Write-Host "ℹ️  No changes to commit."
}
