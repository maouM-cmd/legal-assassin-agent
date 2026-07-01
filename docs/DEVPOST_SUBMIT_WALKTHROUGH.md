# Devpost Submit Walkthrough

Step-by-step guide to complete the Elastic Hackathon submission on Devpost.

Related: [DEVPOST_COPY.md](DEVPOST_COPY.md) | [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md) | [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md)

## Before you start

```powershell
.\scripts\submit_portal_check.ps1
```

Confirms tests pass, ZIP exists, and lists pending STATUS items.

## End-to-end flow

| Step | Action | Tool / doc |
|------|--------|------------|
| 1 | Automated prep + ZIP | `submit_portal_check.ps1` |
| 2 | Record demo video | `rehearse_demo.ps1` + [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md) |
| 3 | Upload video (YouTube unlisted / Loom / Drive) | — |
| 4 | Fill Devpost form | This walkthrough |
| 5 | Update tracked URLs | `update_submission_status.ps1` |
| 6 | Verify all done | `submit_closure_check.ps1` |

---

## Field mapping

Copy from the docs below into the matching Devpost fields.

| Devpost field (typical) | Source |
|-------------------------|--------|
| Project name | [DEVPOST_COPY.md](DEVPOST_COPY.md) → Project Title |
| Tagline / Short description | DEVPOST_COPY → Tagline |
| About / Description | DEVPOST_COPY → Description |
| Built with / Technologies | DEVPOST_COPY → Built With |
| GitHub / Source code link | DEVPOST_COPY → GitHub Repository |
| Demo video link | Your uploaded URL (after recording) |
| Inspiration | DEVPOST_EXTENDED → Inspiration |
| What it does | DEVPOST_EXTENDED → What it does |
| How we built it | DEVPOST_EXTENDED → How we built it |
| Challenges | DEVPOST_EXTENDED → Challenges we ran into |
| Accomplishments | DEVPOST_EXTENDED → Accomplishments that we're proud of |
| What we learned | DEVPOST_EXTENDED → What we learned |
| What's next | DEVPOST_EXTENDED → What's next for Legal Assassin Agent |

---

## Screenshots and attachments

| Asset | Path |
|-------|------|
| Dashboard screenshot | `docs/screenshots/dashboard-overview.png` |
| Platform detections | `docs/screenshots/platform-detections.png` |
| Submission ZIP (if required) | `legal-assassin-agent-submission.zip` (project root) |

Judges extracting the ZIP must run `.\scripts\bootstrap.ps1` — MP4s are not included.

---

## Devpost form tips

1. Open [DEVPOST_COPY.md](DEVPOST_COPY.md) and [DEVPOST_EXTENDED.md](DEVPOST_EXTENDED.md) in split view with Devpost.
2. Paste each fenced code block (between triple backticks) without the backticks.
3. Set **GitHub URL** to `https://github.com/maouM-cmd/legal-assassin-agent`.
4. Upload **demo video URL** after recording — do not leave the placeholder.
5. Mention **Elasticsearch** in description: three indices + Kibana NDJSON import.
6. Click **Submit** only after reviewing all fields.

---

## After submit

Run the status updater (interactive):

```powershell
.\scripts\update_submission_status.ps1
```

Enter when prompted:

- Demo video URL
- Devpost project URL (from browser after submit)
- ZIP uploaded (y/n)
- Submitted date (YYYY-MM-DD, or Enter for today)

Then verify closure:

```powershell
.\scripts\submit_closure_check.ps1
```

Commit updated `docs/SUBMISSION_STATUS.md` and `docs/DEVPOST_COPY.md` if desired.

---

## Optional: live Kibana in video

Before recording segment 3:45–4:30:

```powershell
.\scripts\verify_elastic_cloud.ps1
```

If Elastic Cloud is not configured, use `docs/screenshots/dashboard-overview.png` — acceptable for submission.
