$ErrorActionPreference = "Stop"
$path = "scripts/gather.py"
if (!(Test-Path $path)) { throw "Not found: $path" }

# pick python
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
if (-not $py -and (Get-Command python -ErrorAction SilentlyContinue)) { $py = "python" }
if (-not $py) { throw "Python not found in PATH." }

$tmp = New-TemporaryFile
& $py -m py_compile $path 2> $tmp.FullName
$err = Get-Content $tmp.FullName -Raw -ErrorAction SilentlyContinue
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0 -or -not $err) {
  Write-Host "✅ Python syntax OK"
  exit 0
}

Write-Warning "❌ Python syntax error:"
Write-Host $err

$ln = $null
if ($err -match 'line (\d+)') { $ln = [int]$matches[1] }
if ($ln) {
  $lines = Get-Content $path -Encoding UTF8
  $start = [Math]::Max(1, $ln - 5)
  $end   = [Math]::Min($lines.Count, $ln + 5)
  Write-Host "`n-- context $start..$end --"
  for ($i=$start; $i -le $end; $i++) {
    $mark = '  '; if ($i -eq $ln) { $mark = '>>' }
    Write-Host ("{0} {1,4}: {2}" -f $mark, $i, $lines[$i-1].Replace("`t","    "))
  }
}
throw "Stop: fix the syntax shown above, then re-run."
