# Load .env variables
$envPath = Join-Path $PSScriptRoot ".env"
if (-Not (Test-Path $envPath)) {
    Write-Error "Missing .env file at $envPath"
    exit 1
}

Get-Content $envPath | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.+)$") {
        $name, $value = $matches[1], $matches[2]
        Set-Item -Path "Env:$name" -Value $value
    }
}

$backupDir = $env:BACKUP_DIR

Write-Host "Available backups:"
Get-ChildItem -Path $backupDir -Filter "db_*.sql.gz" | ForEach-Object {
    $_.Name -replace "^db_", "" -replace "\.sql\.gz$", ""
}
