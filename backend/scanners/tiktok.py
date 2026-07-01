"""TikTok scanner — delegates to platform adapter factory."""
from __future__ import annotations

from backend.platforms.factory import get_tiktok_scanner
from backend.scanners.base import BaseScanner, ScanResult


class TikTokScanner(BaseScanner):
    platform = "tiktok"

    def __init__(self) -> None:
        self._delegate = get_tiktok_scanner()

    async def scan(self, keywords: list[str]) -> ScanResult:
        return await self._delegate.scan(keywords)
