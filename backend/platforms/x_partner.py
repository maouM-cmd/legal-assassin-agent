"""X scanner and submitter via partner HTTP API."""
from __future__ import annotations

from backend.platforms.partner_client import PartnerPlatformScanner, PartnerPlatformSubmitter


class PartnerXScanner(PartnerPlatformScanner):
    def __init__(self) -> None:
        super().__init__("twitter", "X_PARTNER_API_URL", "X_PARTNER_API_KEY")


class PartnerXSubmitter(PartnerPlatformSubmitter):
    def __init__(self) -> None:
        super().__init__("twitter", "X_PARTNER_API_URL", "X_PARTNER_API_KEY")
