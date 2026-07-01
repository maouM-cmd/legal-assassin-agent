"""TikTok scanner and submitter via partner HTTP API."""
from __future__ import annotations

import os
from typing import Any

import httpx

from backend.dmca.submitters.base import BaseSubmitter
from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult

_PARTNER_NOT_CONFIGURED = (
    "TIKTOK_PARTNER_API not configured — set TIKTOK_BACKEND=playwright"
)


def _partner_config() -> tuple[str, str] | None:
    url = os.getenv("TIKTOK_PARTNER_API_URL", "").strip().rstrip("/")
    key = os.getenv("TIKTOK_PARTNER_API_KEY", "").strip()
    if not url or not key:
        return None
    return url, key


class PartnerTikTokScanner(BaseScanner):
    platform = "tiktok"

    async def scan(self, keywords: list[str]) -> ScanResult:
        config = _partner_config()
        if not config:
            return ScanResult(
                platform=self.platform,
                candidates=[],
                error=_PARTNER_NOT_CONFIGURED,
            )

        base_url, api_key = config
        candidates: list[ScanCandidate] = []
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for kw in keywords[:3]:
                    resp = await client.get(
                        f"{base_url}/v1/search",
                        params={"q": kw},
                        headers=headers,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    for video in data.get("videos", [])[:5]:
                        url = video.get("url", "")
                        if not url:
                            continue
                        candidates.append(
                            ScanCandidate(
                                platform=self.platform,
                                url=url,
                                title=video.get("title", kw),
                                metadata={"keyword": kw, "backend": "partner"},
                            )
                        )
            return ScanResult(platform=self.platform, candidates=candidates, error=None)
        except Exception as e:
            return ScanResult(platform=self.platform, candidates=[], error=str(e))


class PartnerTikTokSubmitter(BaseSubmitter):
    platform = "tiktok"

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        if os.getenv("DMCA_AUTO_SUBMIT", "true").lower() != "true":
            return {"status": "skipped", "platform": self.platform, "reason": "DMCA_AUTO_SUBMIT=false"}

        config = _partner_config()
        if not config:
            return {
                "status": "failed",
                "platform": self.platform,
                "error": _PARTNER_NOT_CONFIGURED,
            }

        base_url, api_key = config
        payload = {
            "suspect_url": notice.get("suspect_url", ""),
            "body": notice.get("body", ""),
            "platform": self.platform,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{base_url}/v1/dmca",
                    json=payload,
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
            return {
                "status": data.get("status", "submitted"),
                "platform": self.platform,
                "suspect_url": notice.get("suspect_url"),
                "mode": "partner_api",
            }
        except Exception as e:
            return {"status": "failed", "platform": self.platform, "error": str(e)}
