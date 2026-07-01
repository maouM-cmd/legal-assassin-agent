# Legal Assassin Agent — Elastic Cloud preflight (optional, for demo video)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$EnvFile = Join-Path $Root ".env"
$cloudId = ""
$apiKey = ""

if (Test-Path $EnvFile) {
    foreach ($line in Get-Content $EnvFile) {
        if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
        if ($line -match '^ELASTIC_CLOUD_ID=(.*)$') { $cloudId = $Matches[1].Trim().Trim('"').Trim("'") }
        if ($line -match '^ELASTIC_API_KEY=(.*)$') { $apiKey = $Matches[1].Trim().Trim('"').Trim("'") }
    }
}

Write-Host "=== Elastic Cloud Preflight ===" -ForegroundColor Cyan

if (-not $cloudId -or -not $apiKey) {
    Write-Host "  ELASTIC_CLOUD_ID / ELASTIC_API_KEY: not configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Demo works in in-memory mode. Placeholder Kibana PNGs in docs\screenshots\ are fine for submission."
    Write-Host "  For a live Kibana segment in your demo video, see:"
    Write-Host "    docs\elastic_cloud_setup.md"
    Write-Host ""
    exit 0
}

Write-Host "  ELASTIC_CLOUD_ID: configured"
Write-Host "  ELASTIC_API_KEY: configured"
Write-Host ""

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Error "Python not found. Run .\scripts\bootstrap.ps1 first."
}

Write-Host "Running verify_setup to confirm Elasticsearch connection..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Elastic Cloud preflight OK — you can show live Kibana in the demo video." -ForegroundColor Green
Write-Host "  Import dashboard: docs\kibana\dashboard.ndjson"
