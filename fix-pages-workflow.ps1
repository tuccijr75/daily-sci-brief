$ErrorActionPreference = "Stop"
$wf = ".github/workflows/pages.yml"
if (-not (Test-Path $wf)) { throw "Workflow file not found: $wf" }

# Load & remove any run-name
$yml = Get-Content $wf -Raw -Encoding UTF8
$yml = $yml -replace "(?m)^\s*run-name:.*\r?\n", ""

# Step-dedupe for 'run:'
$lines = $yml -split "`r?`n"
$fixed  = New-Object System.Collections.Generic.List[string]
function Get-Indent([string]$s){ ([regex]::Match($s,'^( +)')).Length }
$inStep = $false; $runSeen = $false

for ($i=0; $i -lt $lines.Count; $i++){
  $L = $lines[$i]

  if ($L -match '^\s*-\s+name:'){
    $inStep = $true; $runSeen = $false
    $fixed.Add($L); continue
  }
  if ($inStep -and $L -match '^\s*-\s'){
    $inStep = $false; $runSeen = $false
  }

  if ($inStep -and $L -match '^\s*run\s*:'){
    if (-not $runSeen){
      $runSeen = $true
      $fixed.Add($L)
    } else {
      $indent = Get-Indent $L
      $fixed.Add((' ' * $indent) + "# DUPLICATE run: (commented out)")
      # If the duplicate had a block scalar, comment the following more-indented lines
      if ($L.TrimEnd() -like "run:*|"){
        $j = $i + 1
        while ($j -lt $lines.Count){
          $Ln = $lines[$j]; $indN = Get-Indent $Ln
          if ($Ln.Trim() -eq '' -or $indN -gt $indent){
            $fixed.Add((' ' * $indN) + "# " + $Ln.TrimStart()); $j++
          } else { break }
        }
        $i = $j - 1
      }
    }
    continue
  }

  $fixed.Add($L)
}
$yml = $fixed -join "`r`n"

# Insert Quick syntax gate if missing
if ($yml -notmatch "Quick syntax gate \(py_compile\)"){
  $m = [regex]::Match($yml, '(?m)^( +)-\s+name:\s*Generate site data')
  if ($m.Success){
    $indent = $m.Groups[1].Value
    $gate = @"
$indent- name: Quick syntax gate (py_compile)
$indent  run: |
$indent    python - <<'PY'
$indent    import py_compile, sys
$indent    try:
$indent        py_compile.compile("scripts/gather.py", doraise=True)
$indent    except Exception as e:
$indent        print(e)
$indent        sys.exit(1)
$indent    PY
"@
    $yml = $yml -replace '(?m)^( +)-\s+name:\s*Generate site data', $gate + '$0'
  } else {
    $m2 = [regex]::Match($yml, '(?m)^( +)steps:\s*$')
    if ($m2.Success){
      $indent = $m2.Groups[1].Value + '  '
      $gate = @"
$indent- name: Quick syntax gate (py_compile)
$indent  run: |
$indent    python - <<'PY'
$indent    import py_compile, sys
$indent    try:
$indent        py_compile.compile("scripts/gather.py", doraise=True)
$indent    except Exception as e:
$indent        print(e)
$indent        sys.exit(1)
$indent    PY
"@
      $yml = $yml -replace '(?m)^( +)steps:\s*$', '$0' + "`r`n" + $gate
    }
  }
}

Set-Content -Path $wf -Value $yml -Encoding UTF8
Write-Host "✅ pages.yml sanitized."
