# Legal Assassin — Rehearsal Checklist

## ZIP 展開後の再現手順（審査員向け）

提出 ZIP には MP4 が含まれません。必ず以下を実行:

```powershell
.\scripts\bootstrap.ps1
python scripts\verify_setup.py
.\start.bat
```

## Pre-demo (15 min before)

- [ ] `.env` loaded; `DEMO_MODE=true` for safe demo (or `false` for approval queue demo)
- [ ] Server running: `.\start.bat` → http://localhost:8001
- [ ] Dashboard shows **ONLINE** badge
- [ ] Reference library has indexed fingerprints (`data/references/` or prior patrol)
- [ ] Evasion samples exist: `data/evasion_samples/*.mp4` (5 types including speed/crop)
- [ ] Optional: Kibana dashboard imported from `docs/kibana/dashboard.ndjson`

## Demo flow (see `docs/DEMO_SCRIPT.md`)

1. [ ] Show stats grid (hits, takedowns, pending approval)
2. [ ] Run patrol → explain kNN + hybrid match in health badge
3. [ ] Show hit with evasion badges (`speed_changed`, `cropped`, etc.)
4. [ ] Open **COMPARE** modal — reference vs suspect thumbnails
5. [ ] Approval queue: approve/reject (if `DEMO_MODE=false`)
6. [ ] DMCA preview dialog
7. [ ] Failed takedowns + **RETRY FAILED** (backoff explained)
8. [ ] Optional: Webhook notification (`WEBHOOK_ENABLED=true`)
9. [ ] Audit CSV: **EXPORT AUDIT CSV** ボタン（ヘッダー）または `GET /api/audit/export`

## Backup plans

- [ ] If patrol slow: use pre-seeded hits from prior run
- [ ] If ES unavailable: in-memory mode still works for demo
- [ ] If platform API keys missing: local `evasion_samples` + `/api/analyze`

## Post-demo

- [ ] Stop server (Ctrl+C)
- [ ] Export compliance CSV if reviewers request audit trail
