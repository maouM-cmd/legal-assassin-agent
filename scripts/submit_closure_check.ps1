# Legal Assassin Agent — Submission closure gate (all STATUS items done)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$StatusFile = Join-Path $Root "docs\SUBMISSION_STATUS.md"

Write-Host "=== Legal Assassin Submission Closure Check ===" -ForegroundColor Cyan

if (-not (Test-Path $StatusFile)) {
    Write-Error "Missing docs\SUBMISSION_STATUS.md"
}

$status = Get-Content $StatusFile -Raw
$pending = @()

if ($status -match '\|\s*Demo video URL\s*\|\s*[^|]*\|\s*pending\s*\|') {
    $pending += "Demo video URL"
}
if ($status -match '\|\s*Devpost project URL\s*\|\s*[^|]*\|\s*pending\s*\|') {
    $pending += "Devpost project URL"
}
if ($status -match '\|\s*ZIP uploaded\s*\|[^|]*\|\s*pending\s*\|') {
    $pending += "ZIP uploaded"
}
if ($status -match '\|\s*Submitted date\s*\|\s*[^|]*\|\s*pending\s*\|') {
    $pending += "Submitted date"
}

if ($pending.Count -gt 0) {
    Write-Host ""
    Write-Host "FAILED — pending items in SUBMISSION_STATUS.md:" -ForegroundColor Red
    foreach ($item in $pending) {
        Write-Host "  - $item"
    }
    Write-Host ""
    Write-Host "Run: .\scripts\update_submission_status.ps1"
    Write-Host "Guide: docs\DEVPOST_SUBMIT_WALKTHROUGH.md"
    exit 1
}

Write-Host "All SUBMISSION_STATUS items marked done." -ForegroundColor Green
Write-Host ""
Write-Host "Running final portal check..."
& (Join-Path $Root "scripts\submit_portal_check.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$devpostUrl = ""
if ($status -match '\|\s*Devpost project URL\s*\|\s*([^|]+)\s*\|\s*done\s*\|') {
    $devpostUrl = $Matches[1].Trim()
}

Write-Host ""
Write-Host "=== Submission complete ===" -ForegroundColor Green
if ($devpostUrl) {
    Write-Host "  Devpost: $devpostUrl"
}
Write-Host "  GitHub:  https://github.com/maouM-cmd/legal-assassin-agent"
Write-Host ""
Write-Host "Consider committing updated SUBMISSION_STATUS.md and DEVPOST_COPY.md."
