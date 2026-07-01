# Legal Assassin Agent — Final submission gate
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

Write-Host "=== Legal Assassin Final Submit Check ===" -ForegroundColor Cyan
$failed = $false

Write-Host "`n[1/4] verify_setup..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) { $failed = $true }

Write-Host "`n[2/4] pytest..."
& $Python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { $failed = $true }

Write-Host "`n[3/4] Kibana screenshots..."
& $Python scripts\generate_screenshot_placeholders.py
$shots = @(
    "docs\screenshots\dashboard-overview.png",
    "docs\screenshots\platform-detections.png"
)
foreach ($shot in $shots) {
    if (-not (Test-Path (Join-Path $Root $shot))) {
        Write-Host "  MISSING: $shot" -ForegroundColor Red
        $failed = $true
    } else {
        Write-Host "  OK: $shot"
    }
}

Write-Host "`n[4/4] git status..."
if (Get-Command git -ErrorAction SilentlyContinue) {
    $stagedEnv = git diff --cached --name-only 2>$null | Where-Object { $_ -eq ".env" }
    if ($stagedEnv) {
        Write-Host "  WARNING: .env is staged for commit!" -ForegroundColor Red
        $failed = $true
    }
    $dirty = git status --porcelain 2>$null
    if ($dirty) {
        Write-Host "  WARNING: uncommitted changes:" -ForegroundColor Yellow
        $dirty | ForEach-Object { Write-Host "    $_" }
    } else {
        Write-Host "  Working tree clean"
    }
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Host "  Remote: $remote"
    } else {
        Write-Host "  No git remote configured yet"
    }
} else {
    Write-Host "  git not found (skipped)"
}

Write-Host ""
if ($failed) {
    Write-Host "FAILED — fix errors above before submitting." -ForegroundColor Red
    exit 1
}

Write-Host "All automated checks passed." -ForegroundColor Green
Write-Host ""
Write-Host "Manual steps remaining:"
Write-Host "  1. .\scripts\publish_github.ps1   (or push manually)"
Write-Host "  2. Confirm GitHub Actions CI is green"
Write-Host "  3. Record demo video — docs\DEMO_VIDEO_SCRIPT.md"
Write-Host "  4. Fill Devpost — docs\DEVPOST_COPY.md"
Write-Host ""
Write-Host "See also: scripts\rehearsal_checklist.md | Phase 9: scripts\rehearse_demo.ps1"
