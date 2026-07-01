"""X (Twitter) scanner — delegates to platform adapter factory."""
from __future__ import annotations

from backend.platforms.factory import get_x_scanner
from backend.scanners.base import BaseScanner, ScanResult


class TwitterScanner(BaseScanner):
    platform = "twitter"

    def __init__(self) -> None:
        self._delegate = get_x_scanner()

    async def scan(self, keywords: list[str]) -> ScanResult:
        return await self._delegate.scan(keywords)
