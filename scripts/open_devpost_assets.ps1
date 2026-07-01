# Legal Assassin Agent — Open Devpost submission assets for copy-paste
param(
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$ZipName = "legal-assassin-agent-submission.zip"
$ZipPath = Join-Path $Root $ZipName
$DashboardUrl = "http://localhost:8001"

$Docs = @(
    "docs\DEVPOST_COPY.md",
    "docs\DEVPOST_EXTENDED.md",
    "docs\DEVPOST_SUBMIT_WALKTHROUGH.md"
)

Write-Host "=== Open Devpost Assets ===" -ForegroundColor Cyan

if (Test-Path $ZipPath) {
    Write-Host "  Opening ZIP in Explorer: $ZipPath"
    explorer.exe "/select,$ZipPath"
} else {
    Write-Host "  WARNING: ZIP not found — run .\scripts\submit_portal_check.ps1 first" -ForegroundColor Yellow
}

foreach ($rel in $Docs) {
    $full = Join-Path $Root $rel
    if (Test-Path $full) {
        Write-Host "  Opening: $rel"
        Start-Process $full
    } else {
        Write-Host "  MISSING: $rel" -ForegroundColor Yellow
    }
}

if (-not $SkipBrowser) {
    $serverUp = $false
    try {
        $resp = Invoke-WebRequest -Uri "$DashboardUrl/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $serverUp = $true }
    } catch {
        $serverUp = $false
    }

    if ($serverUp) {
        Write-Host "  Opening dashboard: $DashboardUrl"
        Start-Process $DashboardUrl
    } else {
        Write-Host "  Dashboard not running at $DashboardUrl (start with .\start.bat for live demo)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Paste from DEVPOST_COPY.md + DEVPOST_EXTENDED.md into Devpost fields." -ForegroundColor Green
