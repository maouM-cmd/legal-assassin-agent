"""X DMCA submitter via Playwright."""
from __future__ import annotations

import os
from typing import Any

from backend.dmca import selectors
from backend.dmca.submitters.base import BaseSubmitter

FORM_URL = "https://help.twitter.com/forms/dmca"


class PlaywrightXSubmitter(BaseSubmitter):
    platform = "twitter"

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        if os.getenv("DMCA_AUTO_SUBMIT", "true").lower() != "true":
            return {"status": "skipped", "platform": self.platform, "reason": "DMCA_AUTO_SUBMIT=false"}

        if os.getenv("DEMO_MODE", "true").lower() == "true":
            return {
                "status": "submitted",
                "platform": self.platform,
                "suspect_url": notice.get("suspect_url"),
                "mode": "demo_simulated",
                "message": "DEMO_MODE: simulated X DMCA submission",
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

                await self._fill_common_fields(page, notice, selectors.TWITTER)
                submit = page.locator(selectors.TWITTER["submit"]).first
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
