# Submission Closure Checklist

One-page guide to complete the Elastic Hackathon Devpost submission after Phase 13.

Related: [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md) | [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md)

## Automated prep

```powershell
.\scripts\submit_portal_check.ps1
```

Expects: verify_setup pass, pytest 45+ passed, submission ZIP built, Phase 12/13 artifacts present.

## Manual steps

| Step | Action | Tool / doc |
|------|--------|------------|
| 1 | Record demo video | `rehearse_demo.ps1` + [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) |
| 2 | Upload video (YouTube unlisted / Loom / Drive) | — |
| 3 | Fill Devpost form | [DEVPOST_COPY.md](DEVPOST_COPY.md) + [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md) |
| 4 | Upload ZIP if required | `legal-assassin-agent-submission.zip` |
| 5 | Click Submit on Devpost | [DEVPOST_SUBMIT_WALKTHROUGH.md](DEVPOST_SUBMIT_WALKTHROUGH.md) |

## After submit

```powershell
.\scripts\update_submission_status.ps1
.\scripts\submit_closure_check.ps1
```

Enter when prompted:

- Demo video URL
- Devpost project URL
- ZIP uploaded (y/n)
- Submitted date (YYYY-MM-DD)

## Completion criteria

All rows in [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) must show `done`:

| Item | Status |
|------|--------|
| Demo video URL | done |
| Devpost project URL | done |
| ZIP uploaded | done |
| Submitted date | done |

Then commit updated status files:

```powershell
git add docs/SUBMISSION_STATUS.md docs/DEVPOST_COPY.md
git commit -m "Phase 13: mark Devpost submission complete."
git push
```

## Demo highlights to show in video

- RUN ALL PATROLS → TARGET ACQUIRED
- COMPARE thumbnails
- Compliance panel (counter-notification, legal hold)
- Mode badge: `YouTube: api | TikTok: playwright | X: api`
- EXPORT AUDIT CSV
