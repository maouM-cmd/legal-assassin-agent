"""TikTok scanner via Playwright search (demo-safe fallback)."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult
from backend.scanners.youtube import _demo_candidates


class TikTokScanner(BaseScanner):
    platform = "tiktok"

    async def scan(self, keywords: list[str]) -> ScanResult:
        if os.getenv("DEMO_MODE", "true").lower() == "true":
            candidates = [
                ScanCandidate(
                    platform=self.platform,
                    url=c.url,
                    title=f"[TikTok] {c.title}",
                    metadata={**c.metadata, "platform": "tiktok"},
                )
                for c in _demo_candidates(keywords)
            ]
            return ScanResult(
                platform=self.platform,
                candidates=candidates,
                error="DEMO_MODE — local evasion samples as TikTok candidates",
            )

        try:
            from playwright.async_api import async_playwright

            candidates: list[ScanCandidate] = []
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                for kw in keywords[:3]:
                    url = f"https://www.tiktok.com/search/video?q={kw}"
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    links = await page.eval_on_selector_all(
                        'a[href*="/video/"]',
                        "els => els.map(e => e.href)",
                    )
                    for link in links[:5]:
                        candidates.append(
                            ScanCandidate(
                                platform=self.platform,
                                url=link,
                                title=kw,
                                metadata={"keyword": kw},
                            )
                        )
                    await asyncio.sleep(float(os.getenv("TIKTOK_SCAN_DELAY_SEC", "2.0")))
                await browser.close()
            return ScanResult(platform=self.platform, candidates=candidates)
        except Exception as e:
            return ScanResult(
                platform=self.platform,
                candidates=_demo_candidates(keywords),
                error=str(e),
            )
