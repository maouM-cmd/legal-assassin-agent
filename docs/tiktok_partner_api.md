# TikTok Partner API Migration

Switch TikTok patrol and DMCA from Playwright to an official partner HTTP API.

Related: [SUBMISSION.md](../SUBMISSION.md) | [compliance_workflow.md](compliance_workflow.md)

## Backends

| `TIKTOK_BACKEND` | Behavior |
|------------------|----------|
| `playwright` (default) | Playwright search + copyright form (demo-safe) |
| `partner` | HTTP calls to `TIKTOK_PARTNER_API_URL` |

```env
TIKTOK_BACKEND=playwright
TIKTOK_PARTNER_API_URL=
TIKTOK_PARTNER_API_KEY=
```

## Partner API schema (expected)

### Search — `GET /v1/search?q={keyword}`

Request headers:

```
Authorization: Bearer {TIKTOK_PARTNER_API_KEY}
```

Response:

```json
{
  "videos": [
    { "url": "https://www.tiktok.com/@user/video/123", "title": "clip title" }
  ]
}
```

### DMCA — `POST /v1/dmca`

Request body:

```json
{
  "suspect_url": "https://www.tiktok.com/@user/video/123",
  "body": "DMCA notice text...",
  "platform": "tiktok"
}
```

Response:

```json
{ "status": "submitted" }
```

If `TIKTOK_BACKEND=partner` but URL/key are unset, scan returns an error and submit returns `failed` with message:

`TIKTOK_PARTNER_API not configured — set TIKTOK_BACKEND=playwright`

## Migration checklist

1. Obtain TikTok partner API credentials from your platform partner program
2. Set `TIKTOK_PARTNER_API_URL` and `TIKTOK_PARTNER_API_KEY` in `.env`
3. Set `TIKTOK_BACKEND=partner`
4. Restart server — `/api/health` shows `tiktok_backend: partner` and `tiktok_partner_configured: true`
5. Run patrol and verify candidates arrive via API (not Playwright)
6. Test DMCA submit in staging before production
7. Keep Playwright as fallback by setting `TIKTOK_BACKEND=playwright` if CAPTCHA or partner outage occurs

## Health check

```http
GET /api/health
```

Fields:

- `tiktok_backend` — `playwright` or `partner`
- `tiktok_partner_configured` — `true` when URL + key are set

Dashboard mode badge shows `TikTok: playwright` or `TikTok: partner`.
