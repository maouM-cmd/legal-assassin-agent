# Legal Assassin Agent 一括ブートストラップ (冪等)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Pip = Join-Path $Root ".venv\Scripts\pip.exe"

Write-Host "=== Legal Assassin Agent Bootstrap ===" -ForegroundColor Cyan
Write-Host "Root: $Root"

if (-not (Test-Path $Python)) {
    Write-Host "[1/9] Creating venv..."
    $SystemPython = $null
    foreach ($candidate in @(
        "C:\Users\admin\.local\bin\python3.12.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )) {
        if (Test-Path $candidate) { $SystemPython = $candidate; break }
    }
    if (-not $SystemPython) {
        $SystemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
    }
    if (-not $SystemPython) {
        Write-Error "Python not found. Install Python 3.12+ and re-run."
    }
    & $SystemPython -m venv .venv
} else {
    Write-Host "[1/9] venv OK"
}

Write-Host "[2/9] Installing dependencies..."
& $Pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($env:INSTALL_DEV -eq "1") {
    Write-Host "  Installing dev dependencies (pytest)..."
    & $Pip install -r requirements-dev.txt -q
}

Write-Host "[3/9] Creating demo clip if needed..."
& $Python -m scripts.create_demo_clip

Write-Host "[4/9] Indexing reference clips..."
& $Python -m scripts.index_reference
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (skipped — add data/reference_clips/*.mp4 and re-run)"
}

Write-Host "[5/9] Generating evasion samples..."
& $Python -m scripts.generate_evasion_samples
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (skipped — needs reference clip)"
}

Write-Host "[6/9] Installing Playwright Chromium..."
& $Python -m playwright install chromium 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "  (playwright install skipped)" }

function Test-ElasticConfigured {
    $envFile = Join-Path $Root ".env"
    if (-not (Test-Path $envFile)) { return $false }
    $lines = Get-Content $envFile -Encoding UTF8
    $apiKey = ""
    $cloudId = ""
    $elasticUrl = ""
    foreach ($line in $lines) {
        if ($line -match "^ELASTIC_API_KEY=(.*)$") { $apiKey = $Matches[1].Trim() }
        if ($line -match "^ELASTIC_CLOUD_ID=(.*)$") { $cloudId = $Matches[1].Trim() }
        if ($line -match "^ELASTIC_URL=(.*)$") { $elasticUrl = $Matches[1].Trim() }
    }
    return ($apiKey -and ($cloudId -or $elasticUrl))
}

if (Test-ElasticConfigured) {
    Write-Host "[7/9] Creating Elasticsearch indices..."
    & $Python -m scripts.index_elasticsearch
} else {
    Write-Host "[7/9] Elasticsearch not configured — skipping indices (demo mode OK)"
}

Write-Host "[8/9] Generating Kibana screenshot placeholders..."
& $Python scripts\generate_screenshot_placeholders.py

Write-Host "[9/9] Verifying setup..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "  Start:  .\start.bat"
Write-Host "  Smoke:  .\.venv\Scripts\python.exe scripts\smoke_test.py"
