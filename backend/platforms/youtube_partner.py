"""YouTube scanner and submitter via partner HTTP API."""
from __future__ import annotations

from backend.platforms.partner_client import PartnerPlatformScanner, PartnerPlatformSubmitter


class PartnerYouTubeScanner(PartnerPlatformScanner):
    def __init__(self) -> None:
        super().__init__("youtube", "YOUTUBE_PARTNER_API_URL", "YOUTUBE_PARTNER_API_KEY")


class PartnerYouTubeSubmitter(PartnerPlatformSubmitter):
    def __init__(self) -> None:
        super().__init__("youtube", "YOUTUBE_PARTNER_API_URL", "YOUTUBE_PARTNER_API_KEY")
