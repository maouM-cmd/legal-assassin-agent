# Devpost / Hackathon Portal — Copy-Paste Fields

Paste into the submission portal. Update `YOUR_USER` and video URL after upload.

Related: [PORTAL_CHECKLIST.md](PORTAL_CHECKLIST.md) | [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)

---

## Project Title

```
Legal Assassin Agent
```

## Tagline (one line)

```
24/7 copyright patrol for VOD — fingerprint, detect evasion, auto DMCA via Elasticsearch.
```

## Description

```
VOD businesses lose revenue to illegal re-uploads: flipped clips, pitch shifts, speed changes, crops, and split-screen "fast movie" edits on YouTube, TikTok, and X.

Legal Assassin Agent learns fingerprints of your owned content, stores them in Elasticsearch, patrols platforms 24/7, detects sophisticated evasion, and automates DMCA takedown workflows.

**How it works**
1. Index reference clips (pHash + Chromaprint audio + Gemini embeddings) into `reference_fingerprints`
2. Patrol candidates → hybrid kNN + full fingerprint match → evasion badges (flip, pitch, speed, crop, split-screen)
3. Approval queue or auto-strike → DMCA notice generation → Playwright form submit → log to `takedown_requests`
4. Kibana dashboard for platform detections, evasion breakdown, takedown success, and audit CSV export

**Elasticsearch**
- `reference_fingerprints` — owned content fingerprints
- `infringement_hits` — detection events with scores and evasion types
- `takedown_requests` — DMCA submission audit trail

**Try it locally**
```powershell
.\scripts\bootstrap.ps1
copy .env.example .env
python scripts\verify_setup.py
.\start.bat
```
Open http://localhost:8001 → RUN ALL PATROLS → COMPARE thumbnails → EXPORT AUDIT CSV

Demo works without Elastic Cloud (in-memory fallback). Kibana NDJSON and screenshots included.
```

## Built With

```
Python, FastAPI, Elasticsearch, Google Gemini, Playwright, APScheduler, WebSocket, Kibana
```

## GitHub Repository

```
https://github.com/YOUR_USER/legal-assassin-agent
```

## Demo Video URL

```
(upload recording per DEMO_VIDEO_SCRIPT.md and paste URL here)
```

## Elastic Hackathon Highlights

- Dense-vector kNN candidate narrowing on `reference_fingerprints`
- Three-index observability: references, hits, takedowns
- Importable Kibana dashboard: `docs/kibana/dashboard.ndjson`
- Compliance CSV: `GET /api/audit/export`
