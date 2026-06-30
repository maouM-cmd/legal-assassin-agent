# Legal Assassin Agent — Devpost portal submission (one-stop)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$ZipName = "legal-assassin-agent-submission.zip"
$ZipPath = Join-Path $Root $ZipName
$StatusFile = Join-Path $Root "docs\SUBMISSION_STATUS.md"

Write-Host "=== Legal Assassin Devpost Portal Check ===" -ForegroundColor Cyan

Write-Host "`n[1/2] Running final submit check..."
& (Join-Path $Root "scripts\final_submit_check.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n[2/2] Building submission ZIP..."
& (Join-Path $Root "scripts\package_submission.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$repoUrl = "https://github.com/maouM-cmd/legal-assassin-agent"
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghUrl = gh repo view --json url -q .url 2>$null
    if ($ghUrl) { $repoUrl = $ghUrl }
}

$zipSize = "(not found)"
if (Test-Path $ZipPath) {
    $zipSize = "{0:N2} MB" -f ((Get-Item $ZipPath).Length / 1MB)
}

Write-Host ""
Write-Host "=== Submission assets ===" -ForegroundColor Green
Write-Host "  GitHub:  $repoUrl"
Write-Host "  ZIP:     $ZipPath ($zipSize)"
Write-Host ""
Write-Host "=== Copy-paste docs ===" -ForegroundColor Cyan
Write-Host "  Basic fields:    docs\DEVPOST_COPY.md"
Write-Host "  Extended fields: docs\DEVPOST_EXTENDED.md"
Write-Host "  Video script:    docs\DEMO_VIDEO_SCRIPT.md"
Write-Host "  Checklist:       docs\PORTAL_CHECKLIST.md"
Write-Host ""

if (Test-Path $StatusFile) {
    $status = Get-Content $StatusFile -Raw
    $pending = @()
    if ($status -match '\|\s*Demo video URL\s*\|\s*\|\s*pending') {
        $pending += "Demo video URL (record per DEMO_VIDEO_SCRIPT.md)"
    }
    if ($status -match '\|\s*Devpost project URL\s*\|\s*\|\s*pending') {
        $pending += "Devpost project URL"
    }
    if ($status -match '\|\s*ZIP uploaded\s*\|[^|]*\|\s*pending') {
        $pending += "Upload $ZipName to Devpost (if required)"
    }
    if ($status -match '\|\s*Submitted date\s*\|\s*\|\s*pending') {
        $pending += "Submitted date — update docs\SUBMISSION_STATUS.md after submit"
    }
    if ($pending.Count -gt 0) {
        Write-Host "=== Pending in SUBMISSION_STATUS.md ===" -ForegroundColor Yellow
        foreach ($item in $pending) {
            Write-Host "  - $item"
        }
    } else {
        Write-Host "SUBMISSION_STATUS.md: all tracked items marked done." -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: docs\SUBMISSION_STATUS.md not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Record demo video -> paste URL into DEVPOST_COPY.md + SUBMISSION_STATUS.md"
Write-Host "  2. Open Devpost -> paste from DEVPOST_COPY.md + DEVPOST_EXTENDED.md"
Write-Host "  3. Upload ZIP if portal requires attachment"
Write-Host "  4. Submit -> update docs\SUBMISSION_STATUS.md"
Write-Host ""
Write-Host "Portal check complete." -ForegroundColor Green
