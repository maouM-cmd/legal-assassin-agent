# Submission Closure Checklist

One-page guide to complete the Elastic Hackathon Devpost submission.

Related: [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md) | [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md)

## One-stop entry (Phase 14)

```powershell
.\scripts\execute_submission.ps1
```

Runs portal check, rehearsal teleprompter, opens copy docs + ZIP, then shows the manual checklist.

Skip rehearsal if server already running:

```powershell
.\scripts\execute_submission.ps1 -SkipRehearse
```

## After Devpost submit (non-interactive)

```powershell
.\scripts\execute_submission.ps1 `
  -VideoUrl "https://youtube.com/watch?v=..." `
  -DevpostUrl "https://devpost.com/software/legal-assassin-agent" `
  -ZipUploaded `
  -SubmittedDate "2026-07-01"
```

Or update status interactively:

```powershell
.\scripts\update_submission_status.ps1
.\scripts\submit_closure_check.ps1
```

## Manual steps

| Step | Action | Tool / doc |
|------|--------|------------|
| 1 | Automated prep + open assets | `execute_submission.ps1` |
| 2 | Record demo video | [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) |
| 3 | Upload video (YouTube unlisted / Loom / Drive) | — |
| 4 | Fill Devpost form | [DEVPOST_COPY.md](DEVPOST_COPY.md) + [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md) |
| 5 | Upload ZIP if required | `legal-assassin-agent-submission.zip` |
| 6 | Click Submit on Devpost | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md) |

## Completion criteria

All rows in [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) must show `done`:

| Item | Status |
|------|--------|
| Demo video URL | done |
| Devpost project URL | done |
| ZIP uploaded | done |
| Submitted date | done |

Then commit:

```powershell
git add docs/SUBMISSION_STATUS.md docs/DEVPOST_COPY.md
git commit -m "Phase 14: mark Devpost submission complete."
git push
```

## Demo highlights to show in video

- RUN ALL PATROLS → TARGET ACQUIRED
- COMPARE thumbnails
- Compliance panel (counter-notification, legal hold)
- Mode badge: `YouTube: api | TikTok: playwright | X: api`
- EXPORT AUDIT CSV
