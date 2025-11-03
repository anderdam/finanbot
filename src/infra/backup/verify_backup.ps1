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
$checksumFile = Join-Path $backupDir "checksums.txt"

if (-Not (Test-Path $checksumFile)) {
    Write-Error "Checksum file not found: $checksumFile"
    exit 1
}

Write-Host "Verifying backup integrity..."
Set-Location $backupDir
Get-Content $checksumFile | ForEach-Object {
    $parts = $_ -split "\s+"
    $expectedHash = $parts[0]
    $fileName = $parts[1]

    if (Test-Path $fileName) {
        $actualHash = Get-FileHash $fileName -Algorithm SHA256 | Select-Object -ExpandProperty Hash
        if ($actualHash -eq $expectedHash) {
            Write-Host "✅ $fileName OK"
        } else {
            Write-Host "❌ $fileName FAILED"
        }
    } else {
        Write-Host "⚠️ $fileName not found"
    }
}
