# Legal Assassin Agent — Update submission status after manual Devpost steps
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$StatusFile = Join-Path $Root "docs\SUBMISSION_STATUS.md"
$CopyFile = Join-Path $Root "docs\DEVPOST_COPY.md"

if (-not (Test-Path $StatusFile)) {
    Write-Error "Missing $StatusFile"
}
if (-not (Test-Path $CopyFile)) {
    Write-Error "Missing $CopyFile"
}

function Update-StatusRow {
    param(
        [string]$Content,
        [string]$ItemLabel,
        [string]$Value,
        [string]$Status = "done"
    )
    $escaped = [regex]::Escape($ItemLabel)
    $pattern = "\|\s*$escaped\s*\|\s*[^|]*\|\s*(?:pending|done)\s*\|"
    $replacement = "| $ItemLabel | $Value | $Status |"
    $newContent = [regex]::Replace($Content, $pattern, $replacement)
    if ($newContent -eq $Content) {
        Write-Warning "Could not update row: $ItemLabel"
    }
    return $newContent
}

Write-Host "=== Update Submission Status ===" -ForegroundColor Cyan
Write-Host "Press Enter to skip a field (leave unchanged).`n"

$videoUrl = Read-Host "Demo video URL"
$devpostUrl = Read-Host "Devpost project URL"
$zipAnswer = Read-Host "ZIP uploaded to Devpost? (y/n)"
$submitDate = Read-Host "Submitted date (YYYY-MM-DD, blank = today)"

$statusContent = Get-Content $StatusFile -Raw
$copyContent = Get-Content $CopyFile -Raw
$changed = $false

if ($videoUrl) {
    $statusContent = Update-StatusRow -Content $statusContent -ItemLabel "Demo video URL" -Value $videoUrl
    $copyContent = [regex]::Replace(
        $copyContent,
        '(?s)(## Demo Video URL\s*\r?\n\s*\r?\n```\r?\n)(.*?)(\r?\n```)',
        "`${1}$videoUrl`${3}"
    )
    $changed = $true
    Write-Host "  Updated Demo video URL" -ForegroundColor Green
}

if ($devpostUrl) {
    $statusContent = Update-StatusRow -Content $statusContent -ItemLabel "Devpost project URL" -Value $devpostUrl
    $changed = $true
    Write-Host "  Updated Devpost project URL" -ForegroundColor Green
}

if ($zipAnswer -match '^[Yy]') {
    $statusContent = Update-StatusRow -Content $statusContent -ItemLabel "ZIP uploaded" -Value "legal-assassin-agent-submission.zip"
    $changed = $true
    Write-Host "  Marked ZIP uploaded" -ForegroundColor Green
} elseif ($zipAnswer -match '^[Nn]') {
    Write-Host "  ZIP uploaded left unchanged"
}

if ($submitDate -or $devpostUrl) {
    if (-not $submitDate) {
        $submitDate = (Get-Date).ToString("yyyy-MM-dd")
    }
    $statusContent = Update-StatusRow -Content $statusContent -ItemLabel "Submitted date" -Value $submitDate
    $changed = $true
    Write-Host "  Updated Submitted date: $submitDate" -ForegroundColor Green
}

if (-not $changed) {
    Write-Host "`nNo changes made." -ForegroundColor Yellow
    exit 0
}

Set-Content -Path $StatusFile -Value $statusContent -NoNewline
Set-Content -Path $CopyFile -Value $copyContent -NoNewline

Write-Host ""
Write-Host "Updated:" -ForegroundColor Green
Write-Host "  docs\SUBMISSION_STATUS.md"
Write-Host "  docs\DEVPOST_COPY.md (if video URL provided)"
Write-Host ""
Write-Host "Next: .\scripts\submit_closure_check.ps1"
