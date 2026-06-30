# Legal Assassin Agent — Publish to GitHub (public) and check CI
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$RepoName = if ($env:GITHUB_REPO_NAME) { $env:GITHUB_REPO_NAME } else { "legal-assassin-agent" }

Write-Host "=== Legal Assassin GitHub Publish ===" -ForegroundColor Cyan

Write-Host "Running final submit check..."
& (Join-Path $Root "scripts\final_submit_check.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is required. See docs\GITHUB_PUBLISH.md"
}

$stagedEnv = git diff --cached --name-only 2>$null | Where-Object { $_ -eq ".env" }
if ($stagedEnv) {
    Write-Error ".env is staged. Unstage before pushing."
}

$hasRemote = $false
try {
    $null = git remote get-url origin 2>$null
    $hasRemote = $true
} catch {
    $hasRemote = $false
}

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "`nChecking gh auth..."
    gh auth status
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Run: gh auth login" -ForegroundColor Yellow
        exit 1
    }

    if (-not $hasRemote) {
        Write-Host "`nCreating public repo and pushing..."
        gh repo create $RepoName --public --source=. --remote=origin --push
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } else {
        Write-Host "`nPushing to existing remote..."
        git branch -M main 2>$null
        git push -u origin main
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    $repoUrl = gh repo view --json url -q .url 2>$null
    if ($repoUrl) {
        Write-Host "`nRepository: $repoUrl" -ForegroundColor Green
    }

    Write-Host "`nWaiting for CI workflow..."
    Start-Sleep -Seconds 5
    $run = gh run list --workflow=ci.yml --limit 1 --json databaseId,status,conclusion,url 2>$null | ConvertFrom-Json
    if ($run) {
        $r = $run[0]
        Write-Host "CI run: $($r.status) $($r.conclusion) — $($r.url)"
        if ($r.status -eq "in_progress" -or $r.status -eq "queued") {
            Write-Host "Watching CI (timeout 10 min)..."
            gh run watch $r.databaseId --exit-status
        } elseif ($r.conclusion -ne "success") {
            Write-Host "CI did not succeed. Check: $($r.url)" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "No CI run found yet. Check Actions tab on GitHub." -ForegroundColor Yellow
    }
} else {
    Write-Host "`ngh CLI not found. Manual steps:" -ForegroundColor Yellow
    Write-Host "  1. docs\GITHUB_PUBLISH.md"
    Write-Host "  2. git remote add origin https://github.com/YOUR_USER/$RepoName.git"
    Write-Host "  3. git push -u origin main"
    exit 0
}

Write-Host "`nPublish complete. Next: docs\DEVPOST_COPY.md" -ForegroundColor Green
