"""Shared HTTP client for platform partner API stubs."""
from __future__ import annotations

import os
from typing import Any

import httpx

from backend.dmca.submitters.base import BaseSubmitter
from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult

_ENV_PREFIX = {
    "tiktok": "TIKTOK",
    "youtube": "YOUTUBE",
    "twitter": "X",
}

_FALLBACK_BACKEND = {
    "tiktok": "playwright",
    "youtube": "api",
    "twitter": "api",
}


def partner_not_configured_message(platform: str) -> str:
    prefix = _ENV_PREFIX[platform]
    fallback = _FALLBACK_BACKEND[platform]
    return f"{prefix}_PARTNER_API not configured — set {prefix}_BACKEND={fallback}"


def get_partner_config(url_env: str, key_env: str) -> tuple[str, str] | None:
    url = os.getenv(url_env, "").strip().rstrip("/")
    key = os.getenv(key_env, "").strip()
    if not url or not key:
        return None
    return url, key


async def partner_scan(
    platform: str,
    keywords: list[str],
    url_env: str,
    key_env: str,
) -> ScanResult:
    config = get_partner_config(url_env, key_env)
    if not config:
        return ScanResult(
            platform=platform,
            candidates=[],
            error=partner_not_configured_message(platform),
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
                            platform=platform,
                            url=url,
                            title=video.get("title", kw),
                            metadata={"keyword": kw, "backend": "partner"},
                        )
                    )
        return ScanResult(platform=platform, candidates=candidates, error=None)
    except Exception as e:
        return ScanResult(platform=platform, candidates=[], error=str(e))


async def partner_submit(
    platform: str,
    notice: dict[str, Any],
    url_env: str,
    key_env: str,
) -> dict[str, Any]:
    if os.getenv("DMCA_AUTO_SUBMIT", "true").lower() != "true":
        return {"status": "skipped", "platform": platform, "reason": "DMCA_AUTO_SUBMIT=false"}

    config = get_partner_config(url_env, key_env)
    if not config:
        return {
            "status": "failed",
            "platform": platform,
            "error": partner_not_configured_message(platform),
        }

    base_url, api_key = config
    payload = {
        "suspect_url": notice.get("suspect_url", ""),
        "body": notice.get("body", ""),
        "platform": platform,
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
            "platform": platform,
            "suspect_url": notice.get("suspect_url"),
            "mode": "partner_api",
        }
    except Exception as e:
        return {"status": "failed", "platform": platform, "error": str(e)}


class PartnerPlatformScanner(BaseScanner):
    def __init__(self, platform: str, url_env: str, key_env: str) -> None:
        self.platform = platform
        self._url_env = url_env
        self._key_env = key_env

    async def scan(self, keywords: list[str]) -> ScanResult:
        return await partner_scan(self.platform, keywords, self._url_env, self._key_env)


class PartnerPlatformSubmitter(BaseSubmitter):
    def __init__(self, platform: str, url_env: str, key_env: str) -> None:
        self.platform = platform
        self._url_env = url_env
        self._key_env = key_env

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        return await partner_submit(self.platform, notice, self._url_env, self._key_env)
