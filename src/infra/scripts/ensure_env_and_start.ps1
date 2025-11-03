#!/usr/bin/env pwsh
Param(
  [Parameter(Mandatory=$false, ValueFromRemainingArguments=$true)]
  [string[]] $Cmd
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Load .env if present (simple parser, ignores comments and empty lines)
$envFile = Join-Path (Get-Location) ".env"
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
      $parts = $line -split "=", 2
      if ($parts.Length -eq 2) {
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim("'`"")
        if (-not [string]::IsNullOrEmpty($name)) {
          if (-not $env:$name) { $env:$name = $value }
        }
      }
    }
  }
}

# Required variables
$required = @("POSTGRES_HOST","POSTGRES_PORT","POSTGRES_USER","POSTGRES_PASSWORD","POSTGRES_DB","SECRET_KEY")
$missing = @()
foreach ($v in $required) {
  if (-not $env:$v) { $missing += $v }
}

if ($missing.Count -gt 0) {
  Write-Error "Missing required environment variables: $($missing -join ', ')"
  exit 1
}

# SECRET_KEY length
if ($env:SECRET_KEY.Length -lt 16) {
  Write-Error "SECRET_KEY must be at least 16 characters (current: $($env:SECRET_KEY.Length))"
  exit 2
}

# Validate port
if (-not ($env:POSTGRES_PORT -match '^\d+$')) {
  Write-Error "POSTGRES_PORT must be an integer, got '$($env:POSTGRES_PORT)'"
  exit 3
}
$port = [int]$env:POSTGRES_PORT
if ($port -le 0 -or $port -ge 65536) {
  Write-Error "POSTGRES_PORT must be between 1 and 65535, got $port"
  exit 4
}

# Build DATABASE_URL if missing (URL-encode password)
if (-not $env:DATABASE_URL) {
  $enc = [System.Uri]::EscapeDataString($env:POSTGRES_PASSWORD)
  $env:DATABASE_URL = "postgresql://$($env:POSTGRES_USER):$enc@$($env:POSTGRES_HOST):$($env:POSTGRES_PORT)/$($env:POSTGRES_DB)"
  Write-Host "Built DATABASE_URL from components."
}

# Ensure attachments dir exists and writable (if set)
if ($env:ATTACHMENTS_DIR) {
  try {
    New-Item -ItemType Directory -Force -Path $env:ATTACHMENTS_DIR | Out-Null
    $testFile = Join-Path $env:ATTACHMENTS_DIR ([Guid]::NewGuid().ToString() + ".tmp")
    Set-Content -Path $testFile -Value "ok" -ErrorAction Stop
    Remove-Item $testFile -Force
  } catch {
    Write-Error "ATTACHMENTS_DIR '$($env:ATTACHMENTS_DIR)' is not writable or cannot be created: $_"
    exit 5
  }
}

if (-not $Cmd -or $Cmd.Count -eq 0) {
  Write-Error "No command provided to start. Pass the command and args to this script."
  exit 6
}

Write-Host "Environment validated. Executing: $($Cmd -join ' ')"
# Use Start-Process to respect argument array; wait for process then exit with its code
$proc = Start-Process -FilePath $Cmd[0] -ArgumentList $Cmd[1..($Cmd.Count-1)] -NoNewWindow -PassThru -Wait
exit $proc.ExitCode
