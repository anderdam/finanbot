<#
Idempotent cleaner for src/finanbot/db.
Run from repo root in PowerShell:
  powershell -ExecutionPolicy RemoteSigned -File .\cleand_dbfolder.ps1

Supports: -WhatIf (dry-run) and -Verbose
#>

param(
  [switch]$WhatIf
)

function Exec([string]$cmd) {
  if ($WhatIf) { Write-Host "[DRY-RUN] $cmd"; return }
  Write-Host "[RUN] $cmd"
  iex $cmd
}

# ensure we are at repository root
if (-not (Test-Path -Path ".git")) {
  Write-Error "No .git directory found. Run this from the repository root."
  exit 1
}

# mapping list: source -> destination
$moves = @(
  @{ src = 'src/finanbot/db/migrations/init_finances.sql'; dst = 'src/finanbot/db/init_finances.sql' },
  @{ src = 'src/finanbot/db/init_finances_run.sh';            dst = 'src/finanbot/db/00_init_finances.sh' },
  @{ src = 'src/finanbot/db/migrations/schema_generate.sql'; dst = 'src/finanbot/db/migrations/bootstrap_finances.sql' }
)

foreach ($m in $moves) {
  if (Test-Path $m.src) {
    Exec "git mv `"$($m.src)`" `"$($m.dst)`""
  } else {
    Write-Host "Skipped: $($m.src) not found"
  }
}

# remove stray file if present
$rm = 'src/finanbot/db/init_finances_run.sql'
if (Test-Path $rm) {
  Exec "git rm -f `"$rm`""
} else {
  Write-Host "No stray file to remove: $rm"
}

# mark wrapper executable in git index (safe on Windows; sets 100755)
$wrapper = 'src/finanbot/db/00_init_finances.sh'
if (Test-Path $wrapper) {
  Exec "git update-index --add --chmod=+x `"$wrapper`""
} else {
  Write-Host "Wrapper not present, skip chmod: $wrapper"
}

# stage and commit
Exec "git add src/finanbot/db"
Exec "git add -A"
Exec "git commit -m `"db: consolidate init scripts; add 00_init_finances.sh wrapper; move bootstrap to migrations`""
Write-Host "Done."