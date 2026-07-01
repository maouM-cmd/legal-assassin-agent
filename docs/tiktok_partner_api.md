# TikTok Partner API Migration

Switch TikTok patrol and DMCA from Playwright to an official partner HTTP API.

**Common schema and multi-platform guide:** [platform_partner_api.md](platform_partner_api.md)

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

See [platform_partner_api.md](platform_partner_api.md) for full request/response format.

If `TIKTOK_BACKEND=partner` but URL/key are unset:

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
