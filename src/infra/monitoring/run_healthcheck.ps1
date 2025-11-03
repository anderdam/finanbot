$scriptPath = Join-Path $PSScriptRoot "healthcheck.py"
$sendMail = Join-Path $PSScriptRoot "..\..\services\send_email.py"

Write-Host "Running healthcheck..."
$health = python $scriptPath
$status = $LASTEXITCODE

if ($status -eq 0) {
    Write-Host "✅ All systems healthy"
    python $sendMail "Finanbot Healthcheck Passed" "All checks passed in healthcheck.py"
} else {
    Write-Host "❌ Healthcheck failed, sending alert..."
    python $sendMail "Finanbot Healthcheck Failed" "One or more checks failed in healthcheck.py"
}
