# Legal Assassin Agent — Elastic Cloud one-shot setup
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$EnvFile = Join-Path $Root ".env"
$cloudId = ""
$apiKey = ""
$elasticUrl = ""

if (Test-Path $EnvFile) {
    foreach ($line in Get-Content $EnvFile) {
        if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
        if ($line -match '^ELASTIC_CLOUD_ID=(.*)$') { $cloudId = $Matches[1].Trim().Trim('"').Trim("'") }
        if ($line -match '^ELASTIC_API_KEY=(.*)$') { $apiKey = $Matches[1].Trim().Trim('"').Trim("'") }
        if ($line -match '^ELASTIC_URL=(.*)$') { $elasticUrl = $Matches[1].Trim().Trim('"').Trim("'") }
    }
}

Write-Host "=== Elastic Cloud Setup ===" -ForegroundColor Cyan

$hasElastic = ($cloudId -and $apiKey) -or ($elasticUrl -and $apiKey)
if (-not $hasElastic) {
    Write-Host "FAILED: Elasticsearch credentials not configured." -ForegroundColor Red
    Write-Host ""
    Write-Host "Set ELASTIC_CLOUD_ID + ELASTIC_API_KEY (or ELASTIC_URL + ELASTIC_API_KEY) in .env"
    Write-Host "See: docs\elastic_cloud_setup.md"
    exit 1
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Error "Python not found. Run .\scripts\bootstrap.ps1 first."
}

Write-Host "`n[1/4] Preflight..."
& (Join-Path $Root "scripts\verify_elastic_cloud.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/4] Creating Elasticsearch indices..."
& $Python -m scripts.index_elasticsearch
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[3/4] Indexing reference clips..."
& $Python -m scripts.index_reference
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[4/4] Final verify..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Elastic Cloud setup complete." -ForegroundColor Green
Write-Host "  Start app: .\start.bat"
Write-Host "  Kibana import: docs\kibana\dashboard.ndjson"
Write-Host "  Guide: docs\kibana_infringement.md"
