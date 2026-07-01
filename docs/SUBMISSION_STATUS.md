# Submission Status

Track hackathon portal progress. Update via `update_submission_status.ps1` or manually, then commit.

Related: [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md) | [DEVPOST_COPY.md](DEVPOST_COPY.md) | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md)

| Item | Value | Status |
|------|-------|--------|
| GitHub | https://github.com/maouM-cmd/legal-assassin-agent | done |
| CI | green | done |
| Demo video URL | | pending |
| Devpost project URL | | pending |
| ZIP uploaded | legal-assassin-agent-submission.zip | pending |
| Submitted date | | pending |

## Phase 9 flow

| Step | Command |
|------|---------|
| 1 Prep | `.\scripts\submit_portal_check.ps1` |
| 2 Rehearse / record | `.\scripts\rehearse_demo.ps1` |
| 3 Devpost submit | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md) |
| 4 Update status | `.\scripts\update_submission_status.ps1` |
| 5 Closure | `.\scripts\submit_closure_check.ps1` |

## After video upload

1. Run `.\scripts\update_submission_status.ps1` and enter the demo video URL
2. Or paste URL into [DEVPOST_COPY.md](DEVPOST_COPY.md) Demo Video section and set Demo video URL row to `done`

## After Devpost submit

1. Run `.\scripts\update_submission_status.ps1` with Devpost URL and submitted date
2. Mark ZIP uploaded if the portal required attachment

Run before submit:

```powershell
.\scripts\submit_portal_check.ps1
```
