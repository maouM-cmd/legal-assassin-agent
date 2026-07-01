# Legal Assassin Agent — Demo video rehearsal (teleprompter + server prep)
param(
    [switch]$SkipElastic
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Error "Python not found. Run .\scripts\bootstrap.ps1 first."
}

$DashboardUrl = "http://localhost:8001"
$HealthUrl = "$DashboardUrl/api/health"

Write-Host "=== Legal Assassin Demo Rehearsal ===" -ForegroundColor Cyan

Write-Host "`n[1/4] verify_setup..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipElastic) {
    Write-Host "`n[2/4] Elastic Cloud preflight (optional)..."
    & (Join-Path $Root "scripts\verify_elastic_cloud.ps1")
} else {
    Write-Host "`n[2/4] Elastic Cloud preflight skipped (-SkipElastic)"
}

Write-Host "`n[3/4] Server check..."
$serverUp = $false
try {
    $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($resp.StatusCode -eq 200) { $serverUp = $true }
} catch {
    $serverUp = $false
}

if (-not $serverUp) {
    Write-Host "  Starting server in background (start.bat)..."
    $startBat = Join-Path $Root "start.bat"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$startBat`"" -WorkingDirectory $Root -WindowStyle Minimized
    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $serverUp = $true
                break
            }
        } catch {
            continue
        }
    }
    if (-not $serverUp) {
        Write-Error "Server did not respond at $HealthUrl within 30s. Start manually: .\start.bat"
    }
    Write-Host "  Server ONLINE at $DashboardUrl" -ForegroundColor Green
} else {
    Write-Host "  Server already running at $DashboardUrl" -ForegroundColor Green
}

Write-Host "`n[4/4] Opening browser..."
Start-Process $DashboardUrl

Write-Host ""
Write-Host "=== Teleprompter (docs\DEMO_VIDEO_SCRIPT.md) ===" -ForegroundColor Cyan
Write-Host "Start OBS / Game Bar recording, then follow each segment.`n"

$segments = @(
    @{
        Time = "0:00-0:30"
        Screen = "Title + dashboard overview"
        Action = "Show full dashboard; ONLINE badge visible"
        Narration = "Legal Assassin is a 24/7 copyright patrol agent for VOD. It fingerprints owned content in Elasticsearch, detects evasion, and automates DMCA."
    },
    @{
        Time = "0:30-1:00"
        Screen = "Reference Library + DEMO / kNN badges"
        Action = "Scroll reference section; point at mode badges"
        Narration = "pHash and audio fingerprints in the reference library. kNN narrows candidates before full hybrid match."
    },
    @{
        Time = "1:00-2:30"
        Screen = "RUN ALL PATROLS -> hit list"
        Action = "Click RUN ALL PATROLS; wait for TARGET ACQUIRED toast"
        Narration = "Five evasion types: flip, pitch, speed, crop, split-screen. Watch detections appear in Recent Hits."
    },
    @{
        Time = "2:30-3:15"
        Screen = "COMPARE modal"
        Action = "Click COMPARE on a hit row; show both thumbnails"
        Narration = "Side-by-side reference vs suspect thumbnails for legal review."
    },
    @{
        Time = "3:15-3:45"
        Screen = "EXPORT AUDIT CSV"
        Action = "Click header EXPORT AUDIT CSV; confirm download"
        Narration = "Compliance export of hits and takedowns as CSV."
    },
    @{
        Time = "3:45-4:30"
        Screen = "Kibana dashboard or docs/screenshots"
        Action = "Show live Kibana OR docs/screenshots/dashboard-overview.png"
        Narration = "Three Elasticsearch indices visualized: platform detections and evasion breakdown."
    },
    @{
        Time = "4:30-5:00"
        Screen = "Ending / tech stack"
        Action = "Return to dashboard or show SUBMISSION.md stack slide"
        Narration = "FastAPI, Gemini, Playwright DMCA, Elastic 8.8 — 24/7 copyright patrol."
    }
)

foreach ($seg in $segments) {
    Write-Host "--- $($seg.Time) ---" -ForegroundColor Yellow
    Write-Host "  Screen:     $($seg.Screen)"
    Write-Host "  Action:     $($seg.Action)"
    Write-Host "  Narration:  $($seg.Narration)"
    Write-Host ""
}

Write-Host "=== Recording checklist ===" -ForegroundColor Cyan
Write-Host "  [ ] Browser zoom 100%; dark theme visible"
Write-Host "  [ ] COMPARE shows both thumbnails"
Write-Host "  [ ] CSV download starts in browser"
Write-Host "  [ ] No API keys or .env secrets on screen"
Write-Host ""
Write-Host "After recording: upload video, then run:"
Write-Host "  .\scripts\update_submission_status.ps1"
Write-Host ""
Write-Host "Full checklist: scripts\rehearsal_checklist.md"
Write-Host "Video script:   docs\DEMO_VIDEO_SCRIPT.md"
Write-Host ""
Write-Host "Rehearsal ready. Press Ctrl+C in the server window when done." -ForegroundColor Green
