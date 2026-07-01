"""TikTok scanner and submitter via Playwright."""
from __future__ import annotations

import asyncio
import os
from typing import Any

from backend.dmca import selectors
from backend.dmca.submitters.base import BaseSubmitter
from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult
from backend.scanners.demo_candidates import demo_candidates as _demo_candidates

FORM_URL = "https://www.tiktok.com/legal/report/Copyright"


class PlaywrightTikTokScanner(BaseScanner):
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


class PlaywrightTikTokSubmitter(BaseSubmitter):
    platform = "tiktok"

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        if os.getenv("DMCA_AUTO_SUBMIT", "true").lower() != "true":
            return {"status": "skipped", "platform": self.platform, "reason": "DMCA_AUTO_SUBMIT=false"}

        if os.getenv("DEMO_MODE", "true").lower() == "true":
            return {
                "status": "submitted",
                "platform": self.platform,
                "suspect_url": notice.get("suspect_url"),
                "mode": "demo_simulated",
                "message": "DEMO_MODE: simulated TikTok DMCA submission",
            }

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await self._new_context(browser)
                page = await context.new_page()
                await page.goto(FORM_URL, wait_until="domcontentloaded", timeout=60000)

                if await self._check_captcha(page):
                    await browser.close()
                    return {"status": "pending_manual", "platform": self.platform, "reason": "CAPTCHA"}

                await self._fill_common_fields(page, notice, selectors.TIKTOK)
                submit = page.locator(selectors.TIKTOK["submit"]).first
                if await submit.count() > 0:
                    await submit.click()
                    await page.wait_for_timeout(2000)

                await self._save_context(context)
                await browser.close()
                return {
                    "status": "submitted",
                    "platform": self.platform,
                    "suspect_url": notice.get("suspect_url"),
                    "mode": "playwright",
                }
        except Exception as e:
            return {"status": "failed", "platform": self.platform, "error": str(e)}
