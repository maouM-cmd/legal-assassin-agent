# Compliance Workflow

Counter-notification handling and legal holds for DMCA operations.

Related: [SUBMISSION.md](../SUBMISSION.md) | [elastic_cloud_setup.md](elastic_cloud_setup.md)

## Counter-notification flow

1. Platform or uploader sends a counter-notification disputing your DMCA
2. Record it in the dashboard **Takedown Log** → **RECORD COUNTER**
3. Set status:
   - `received` — initial intake
   - `under_review` — legal team reviewing
   - `restored` — content restored on platform
   - `dismissed` — claim upheld, no restore
4. Optional notes are stored on the takedown record and included in audit CSV

## Legal hold

**LEGAL HOLD** blocks automatic DMCA submission and retry for that suspect URL.

Use when:
- Counter-notification is under review
- Counsel requests a pause before further strikes
- False-positive investigation is in progress

**RELEASE HOLD** clears the flag and allows patrol / approve / retry again.

## API

```http
GET /api/compliance/overview
GET /api/compliance/counter-notifications
GET /api/compliance/legal-holds

POST /api/compliance/counter-notification
X-API-Key: <key when API_KEY is set>
{"suspect_url": "https://...", "status": "received", "notes": "..."}

POST /api/compliance/legal-hold
X-API-Key: <key when API_KEY is set>
{"suspect_url": "https://...", "legal_hold": true, "notes": "..."}
```

## Dashboard

1. Open http://localhost:8001
2. If `API_KEY` is set in `.env`, click **SETTINGS** and save your key
3. Use **Compliance** panel to monitor holds and counter-notifications
4. **EXPORT AUDIT CSV** includes `legal_hold` and `counter_notification_status` columns

## Webhook

When `WEBHOOK_ENABLED=true`, `COUNTER_NOTIFICATION` and `LEGAL_HOLD` events post to `WEBHOOK_URL` (Slack/Teams compatible).
