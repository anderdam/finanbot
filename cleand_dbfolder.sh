# run from repo root (PowerShell)
$root = Resolve-Path .
# Move migration init SQL to top-level db folder
$src1 = 'src/finanbot/db/migrations/init_finances.sql'
$dst1 = 'src/finanbot/db/init_finances.sql'
if (Test-Path $src1) { git mv $src1 $dst1 } else { Write-Host "$src1 not found" }

# Rename shell wrapper to run first
$src2 = 'src/finanbot/db/init_finances_run.sh'
$dst2 = 'src/finanbot/db/00_init_finances.sh'
if (Test-Path $src2) { git mv $src2 $dst2 } else { Write-Host "$src2 not found" }

# Keep manual bootstrap in migrations (rename)
$src3 = 'src/finanbot/db/migrations/schema_generate.sql'
$dst3 = 'src/finanbot/db/migrations/bootstrap_finances.sql'
if (Test-Path $src3) { git mv $src3 $dst3 } else { Write-Host "$src3 not found" }

# Remove stray file if present
$rm = 'src/finanbot/db/init_finances_run.sql'
if (Test-Path $rm) { git rm -f $rm } else { Write-Host "$rm not found" }

# Ensure wrapper is marked executable in git (sets the executable bit)
$wrapper = 'src/finanbot/db/00_init_finances.sh'
if (Test-Path $wrapper) { git update-index --add --chmod=+x $wrapper }

git add src/finanbot/db
git add -A
git commit -m "db: consolidate init scripts; add 00_init_finances.sh wrapper; move bootstrap to migrations"