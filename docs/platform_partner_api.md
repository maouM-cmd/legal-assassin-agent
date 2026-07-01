# Platform Partner API Migration

Unified partner HTTP backend for YouTube, TikTok, and X patrol and DMCA submission.

Platform-specific notes: [tiktok_partner_api.md](tiktok_partner_api.md)

Related: [compliance_workflow.md](compliance_workflow.md) | [SUBMISSION_CLOSURE.md](SUBMISSION_CLOSURE.md)

## Backends

| Platform | Env var | Default | Partner env |
|----------|---------|---------|-------------|
| YouTube | `YOUTUBE_BACKEND` | `api` | `YOUTUBE_PARTNER_API_URL` + `YOUTUBE_PARTNER_API_KEY` |
| TikTok | `TIKTOK_BACKEND` | `playwright` | `TIKTOK_PARTNER_API_URL` + `TIKTOK_PARTNER_API_KEY` |
| X | `X_BACKEND` | `api` | `X_PARTNER_API_URL` + `X_PARTNER_API_KEY` |

```env
YOUTUBE_BACKEND=api
YOUTUBE_PARTNER_API_URL=
YOUTUBE_PARTNER_API_KEY=

TIKTOK_BACKEND=playwright
TIKTOK_PARTNER_API_URL=
TIKTOK_PARTNER_API_KEY=

X_BACKEND=api
X_PARTNER_API_URL=
X_PARTNER_API_KEY=
```

Default backends preserve existing demo behavior (YouTube Data API, TikTok Playwright, X API v2).

## Partner API schema (all platforms)

### Search — `GET /v1/search?q={keyword}`

```
Authorization: Bearer {PARTNER_API_KEY}
```

```json
{
  "videos": [
    { "url": "https://example.com/video/123", "title": "clip title" }
  ]
}
```

### DMCA — `POST /v1/dmca`

```json
{
  "suspect_url": "https://example.com/video/123",
  "body": "DMCA notice text...",
  "platform": "youtube"
}
```

Response:

```json
{ "status": "submitted" }
```

If `*_BACKEND=partner` but URL/key are unset, scan returns an error and submit returns `failed` with an explicit message (no fallback to API/Playwright).

## Architecture

```
backend/platforms/
  factory.py          — backend selection per platform
  partner_client.py   — shared HTTP scan/submit
  youtube_api.py      — YouTube Data API scanner
  youtube_playwright.py — Playwright DMCA submitter
  youtube_partner.py  — partner stub
  tiktok_playwright.py / tiktok_partner.py
  x_api.py / x_playwright.py / x_partner.py
```

## Migration checklist

1. Obtain partner API credentials per platform
2. Set `*_PARTNER_API_URL` and `*_PARTNER_API_KEY` in `.env`
3. Set `*_BACKEND=partner` for each platform to migrate
4. Restart server — `/api/health` shows backend and `*_partner_configured` fields
5. Run patrol and verify candidates via HTTP
6. Test DMCA submit in staging
7. Revert to default backend if partner outage or CAPTCHA issues (TikTok: `playwright`)

## Health check

```http
GET /api/health
```

Fields: `youtube_backend`, `youtube_partner_configured`, `tiktok_backend`, `tiktok_partner_configured`, `x_backend`, `x_partner_configured`

Dashboard mode badge shows `YouTube: api|partner`, `TikTok: playwright|partner`, `X: api|partner`.
