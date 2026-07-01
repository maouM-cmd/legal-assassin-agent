# Legal Assassin Agent — One-stop Devpost submission execution
param(
    [switch]$SkipRehearse,
    [string]$VideoUrl,
    [string]$DevpostUrl,
    [switch]$ZipUploaded,
    [string]$SubmittedDate
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$StatusFile = Join-Path $Root "docs\SUBMISSION_STATUS.md"
$finishMode = $PSBoundParameters.ContainsKey("VideoUrl") -or
    $PSBoundParameters.ContainsKey("DevpostUrl") -or
    $ZipUploaded.IsPresent -or
    $PSBoundParameters.ContainsKey("SubmittedDate")

Write-Host "=== Legal Assassin — Execute Submission (Phase 14) ===" -ForegroundColor Cyan

if ($finishMode) {
    Write-Host "`n[Finish] Updating submission status from CLI params..."
    $updateArgs = @{}
    if ($VideoUrl) { $updateArgs["VideoUrl"] = $VideoUrl }
    if ($DevpostUrl) { $updateArgs["DevpostUrl"] = $DevpostUrl }
    if ($ZipUploaded) { $updateArgs["ZipUploaded"] = $true }
    if ($SubmittedDate) { $updateArgs["SubmittedDate"] = $SubmittedDate }
    & (Join-Path $Root "scripts\update_submission_status.ps1") @updateArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "`n[Closure] Running submit_closure_check..."
    & (Join-Path $Root "scripts\submit_closure_check.ps1")
    exit $LASTEXITCODE
}

Write-Host "`n[1/4] Portal check + ZIP build..."
& (Join-Path $Root "scripts\submit_portal_check.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/4] Pending items..."
if (Test-Path $StatusFile) {
    $status = Get-Content $StatusFile -Raw
    $pending = @()
    if ($status -match '\|\s*Demo video URL\s*\|\s*[^|]*\|\s*pending\s*\|') { $pending += "Demo video URL" }
    if ($status -match '\|\s*Devpost project URL\s*\|\s*[^|]*\|\s*pending\s*\|') { $pending += "Devpost project URL" }
    if ($status -match '\|\s*ZIP uploaded\s*\|[^|]*\|\s*pending\s*\|') { $pending += "ZIP uploaded" }
    if ($status -match '\|\s*Submitted date\s*\|\s*[^|]*\|\s*pending\s*\|') { $pending += "Submitted date" }
    if ($pending.Count -gt 0) {
        foreach ($item in $pending) {
            Write-Host "  - $item" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  All tracked items already done." -ForegroundColor Green
    }
}

if (-not $SkipRehearse) {
    Write-Host "`n[3/4] Demo rehearsal (teleprompter + server)..."
    & (Join-Path $Root "scripts\rehearse_demo.ps1") -SkipElastic
} else {
    Write-Host "`n[3/4] Rehearsal skipped (-SkipRehearse)"
}

Write-Host "`n[4/4] Opening Devpost assets..."
& (Join-Path $Root "scripts\open_devpost_assets.ps1")

Write-Host ""
Write-Host "=== Manual checklist ===" -ForegroundColor Cyan
Write-Host "  [ ] Record demo video (OBS / Game Bar)"
Write-Host "  [ ] Upload video -> copy URL"
Write-Host "  [ ] Fill Devpost from DEVPOST_COPY.md + DEVPOST_EXTENDED.md"
Write-Host "  [ ] Upload legal-assassin-agent-submission.zip if required"
Write-Host "  [ ] Click Submit on Devpost"
Write-Host ""
Write-Host "When done, run ONE of:" -ForegroundColor Green
Write-Host '  .\scripts\execute_submission.ps1 -VideoUrl "https://..." -DevpostUrl "https://devpost.com/..." -ZipUploaded'
Write-Host "  .\scripts\update_submission_status.ps1"
Write-Host ""
Write-Host "Then verify: .\scripts\submit_closure_check.ps1"
