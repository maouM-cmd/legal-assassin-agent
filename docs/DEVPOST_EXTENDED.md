# Devpost Extended Fields — Copy-Paste

Use with [DEVPOST_COPY.md](DEVPOST_COPY.md) for basic fields.  
Track progress: [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md)

---

## Inspiration

```
VOD and streaming businesses lose revenue when pirates re-upload full movies and clips with subtle edits — horizontal flips, pitch shifts, speed changes, crops, and split-screen "fast movie" overlays. Manual monitoring cannot scale across YouTube, TikTok, and X. We built an agent that fingerprints owned content in Elasticsearch and strikes back automatically.
```

## What it does

```
Legal Assassin Agent patrols video platforms 24/7, matches suspect uploads against a reference fingerprint library, detects evasion techniques, and generates DMCA takedown notices. A dark-theme dashboard shows real-time hits, approval queues, thumbnail comparison, and compliance CSV export. Kibana visualizes detections and takedown success across three Elasticsearch indices.
```

## How we built it

```
Pipeline: scan -> download -> fingerprint -> hybrid kNN match -> evasion detection -> DMCA generate -> submit -> log

- Video: pHash frame sequences with flip/speed/crop normalization
- Audio: Chromaprint fingerprints with pitch normalization
- AI: Gemini Vision for split-screen detection; embedding kNN on reference_fingerprints
- Backend: Python 3.12, FastAPI, APScheduler, WebSocket events
- DMCA: Jinja2 notices + Playwright form submitters (YouTube, TikTok, X)
- Observability: Elasticsearch indices + importable Kibana dashboard NDJSON
- Ops: exponential backoff retry, webhook alerts, audit CSV, API key gate
```

## Challenges we ran into

```
- Evasion samples required separate normalization paths for speed and crop before pHash alignment
- Hybrid matching needed ES dense-vector kNN to avoid linear scans over large reference libraries
- Playwright DMCA submission hits CAPTCHA — we queue pending_manual and log for human follow-up
- CI smoke test exposed timezone-naive vs aware datetime bugs in audit CSV date filters
- Submission ZIP excludes MP4s — judges must run bootstrap.ps1 after extract
```

## Accomplishments that we're proud of

```
- Five evasion types detected in demo: flip, pitch, speed, crop, split-screen
- End-to-end demo: patrol -> TARGET ACQUIRED -> COMPARE thumbnails -> EXPORT AUDIT CSV
- Full Kibana dashboard (4 lenses) importable from docs/kibana/dashboard.ndjson
- Production gate: approval queue, API key on destructive endpoints, compliance export
- GitHub Actions CI: pytest + bootstrap + smoke test on every push
```

## What we learned

```
Elasticsearch is a strong fit for both candidate narrowing (kNN) and operational audit trails (hits + takedowns). Combining classical fingerprints with Gemini secondary review reduces false positives in the review band. Automating DMCA is technically feasible but legally sensitive — human approval gates are essential.
```

## What's next for Legal Assassin Agent

```
- Elastic Cloud always-on deployment with live Kibana  [setup: scripts/setup_elastic_cloud.ps1 — Phase 10]
- API key header support in the dashboard UI  [done — Phase 10 SETTINGS]
- Official platform partner APIs instead of Playwright for TikTok
- Real Chromaprint (fpcalc) in Docker images  [done — Phase 10 Dockerfile]
- Counter-notification workflow and legal hold integration
```
