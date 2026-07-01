"""Platform backend selection for YouTube, TikTok, and X."""
from __future__ import annotations

import os

from backend.dmca.submitters.base import BaseSubmitter
from backend.platforms.tiktok_partner import PartnerTikTokScanner, PartnerTikTokSubmitter
from backend.platforms.tiktok_playwright import PlaywrightTikTokScanner, PlaywrightTikTokSubmitter
from backend.platforms.x_api import ApiXScanner
from backend.platforms.x_partner import PartnerXScanner, PartnerXSubmitter
from backend.platforms.x_playwright import PlaywrightXSubmitter
from backend.platforms.youtube_api import ApiYouTubeScanner
from backend.platforms.youtube_partner import PartnerYouTubeScanner, PartnerYouTubeSubmitter
from backend.platforms.youtube_playwright import PlaywrightYouTubeSubmitter
from backend.scanners.base import BaseScanner


def _backend(env_name: str, default: str) -> str:
    return os.getenv(env_name, default).strip().lower() or default


def _partner_configured(url_env: str, key_env: str) -> bool:
    url = os.getenv(url_env, "").strip()
    key = os.getenv(key_env, "").strip()
    return bool(url and key)


def tiktok_backend() -> str:
    return _backend("TIKTOK_BACKEND", "playwright")


def youtube_backend() -> str:
    return _backend("YOUTUBE_BACKEND", "api")


def x_backend() -> str:
    return _backend("X_BACKEND", "api")


def partner_api_configured() -> bool:
    return tiktok_partner_configured()


def tiktok_partner_configured() -> bool:
    return _partner_configured("TIKTOK_PARTNER_API_URL", "TIKTOK_PARTNER_API_KEY")


def youtube_partner_configured() -> bool:
    return _partner_configured("YOUTUBE_PARTNER_API_URL", "YOUTUBE_PARTNER_API_KEY")


def x_partner_configured() -> bool:
    return _partner_configured("X_PARTNER_API_URL", "X_PARTNER_API_KEY")


def get_tiktok_scanner() -> BaseScanner:
    if tiktok_backend() == "partner":
        return PartnerTikTokScanner()
    return PlaywrightTikTokScanner()


def get_tiktok_submitter() -> BaseSubmitter:
    if tiktok_backend() == "partner":
        return PartnerTikTokSubmitter()
    return PlaywrightTikTokSubmitter()


def get_youtube_scanner() -> BaseScanner:
    if youtube_backend() == "partner":
        return PartnerYouTubeScanner()
    return ApiYouTubeScanner()


def get_youtube_submitter() -> BaseSubmitter:
    if youtube_backend() == "partner":
        return PartnerYouTubeSubmitter()
    return PlaywrightYouTubeSubmitter()


def get_x_scanner() -> BaseScanner:
    if x_backend() == "partner":
        return PartnerXScanner()
    return ApiXScanner()


def get_x_submitter() -> BaseSubmitter:
    if x_backend() == "partner":
        return PartnerXSubmitter()
    return PlaywrightXSubmitter()
