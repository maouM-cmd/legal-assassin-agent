"""TikTok scanner and submitter via partner HTTP API."""
from __future__ import annotations

from backend.platforms.partner_client import PartnerPlatformScanner, PartnerPlatformSubmitter


class PartnerTikTokScanner(PartnerPlatformScanner):
    def __init__(self) -> None:
        super().__init__("tiktok", "TIKTOK_PARTNER_API_URL", "TIKTOK_PARTNER_API_KEY")


class PartnerTikTokSubmitter(PartnerPlatformSubmitter):
    def __init__(self) -> None:
        super().__init__("tiktok", "TIKTOK_PARTNER_API_URL", "TIKTOK_PARTNER_API_KEY")
