# Legal Assassin Agent — ハッカソン提出用 ZIP パッケージ作成
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$ZipName = "legal-assassin-agent-submission.zip"
$ZipPath = Join-Path $Root $ZipName
$Staging = Join-Path $env:TEMP "legal-assassin-agent-submission-$(Get-Random)"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}

Write-Host "=== Legal Assassin Agent Submission Packaging ===" -ForegroundColor Cyan
Write-Host "Root: $Root"

Write-Host "Running verify_setup gate..."
& $Python scripts\verify_setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "verify_setup failed. Run .\scripts\bootstrap.ps1 first."
}

$ExcludeDirs = @(".venv", "__pycache__", ".git", "node_modules", ".pytest_cache")
$ExcludeFiles = @(".env", $ZipName)

function Should-Exclude([string]$RelativePath) {
    $parts = $RelativePath -split "[\\/]"
    foreach ($dir in $ExcludeDirs) {
        if ($parts -contains $dir) { return $true }
    }
    $name = Split-Path -Leaf $RelativePath
    if ($ExcludeFiles -contains $name) { return $true }
    if ($name -like "*.pyc") { return $true }
    if ($name -like "*.mp4") { return $true }
    return $false
}

if (Test-Path $Staging) { Remove-Item $Staging -Recurse -Force }
New-Item -ItemType Directory -Path $Staging | Out-Null

$count = 0
Get-ChildItem -Path $Root -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($Root.Length + 1)
    if (Should-Exclude $rel) { return }
    $dest = Join-Path $Staging $rel
    $destDir = Split-Path -Parent $dest
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item $_.FullName -Destination $dest -Force
    $count++
}

Write-Host "Staged $count files"

if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path (Join-Path $Staging "*") -DestinationPath $ZipPath -CompressionLevel Optimal
Remove-Item $Staging -Recurse -Force

$sizeMb = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
Write-Host ""
Write-Host "Created: $ZipPath ($sizeMb MB)" -ForegroundColor Green
Write-Host "Excluded: .venv, .env, __pycache__, .git, .pytest_cache, *.mp4"
Write-Host ""
Write-Host "Judges must run .\scripts\bootstrap.ps1 after extracting (MP4s not in ZIP)."
