"""YouTube scanner — delegates to platform adapter factory."""
from __future__ import annotations

from backend.platforms.factory import get_youtube_scanner
from backend.scanners.base import BaseScanner, ScanResult
from backend.scanners.demo_candidates import demo_candidates as _demo_candidates

__all__ = ["YouTubeScanner", "_demo_candidates"]


class YouTubeScanner(BaseScanner):
    platform = "youtube"

    def __init__(self) -> None:
        self._delegate = get_youtube_scanner()

    async def scan(self, keywords: list[str]) -> ScanResult:
        return await self._delegate.scan(keywords)
