"""TikTok platform backend selection."""
from __future__ import annotations

import os

from backend.dmca.submitters.base import BaseSubmitter
from backend.platforms.tiktok_partner import PartnerTikTokScanner, PartnerTikTokSubmitter
from backend.platforms.tiktok_playwright import PlaywrightTikTokScanner, PlaywrightTikTokSubmitter
from backend.scanners.base import BaseScanner


def tiktok_backend() -> str:
    return os.getenv("TIKTOK_BACKEND", "playwright").strip().lower() or "playwright"


def partner_api_configured() -> bool:
    url = os.getenv("TIKTOK_PARTNER_API_URL", "").strip()
    key = os.getenv("TIKTOK_PARTNER_API_KEY", "").strip()
    return bool(url and key)


def get_tiktok_scanner() -> BaseScanner:
    if tiktok_backend() == "partner":
        return PartnerTikTokScanner()
    return PlaywrightTikTokScanner()


def get_tiktok_submitter() -> BaseSubmitter:
    if tiktok_backend() == "partner":
        return PartnerTikTokSubmitter()
    return PlaywrightTikTokSubmitter()
