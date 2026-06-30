"""X (Twitter) scanner via API v2."""
from __future__ import annotations

import asyncio
import os

from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult
from backend.scanners.youtube import _demo_candidates


class TwitterScanner(BaseScanner):
    platform = "twitter"

    async def scan(self, keywords: list[str]) -> ScanResult:
        bearer = os.getenv("X_BEARER_TOKEN", "").strip()
        if not bearer:
            candidates = [
                ScanCandidate(
                    platform=self.platform,
                    url=c.url,
                    title=f"[X] {c.title}",
                    metadata={**c.metadata, "platform": "twitter"},
                )
                for c in _demo_candidates(keywords)
            ]
            return ScanResult(
                platform=self.platform,
                candidates=candidates,
                error="X_BEARER_TOKEN not set — using demo candidates",
            )

        try:
            import tweepy

            client = tweepy.Client(bearer_token=bearer)
            candidates: list[ScanCandidate] = []
            for kw in keywords[:3]:
                resp = client.search_recent_tweets(
                    query=f"{kw} has:videos -is:retweet",
                    max_results=10,
                    tweet_fields=["created_at"],
                    expansions=["attachments.media_keys"],
                    media_fields=["url", "preview_image_url"],
                )
                if not resp.data:
                    continue
                media_map = {}
                if resp.includes and "media" in resp.includes:
                    for m in resp.includes["media"]:
                        media_map[m.media_key] = m

                for tweet in resp.data:
                    media_keys = []
                    if tweet.attachments:
                        media_keys = tweet.attachments.get("media_keys", [])
                    for mk in media_keys:
                        media = media_map.get(mk)
                        if media and getattr(media, "url", None):
                            candidates.append(
                                ScanCandidate(
                                    platform=self.platform,
                                    url=media.url,
                                    title=kw,
                                    metadata={"tweet_id": str(tweet.id), "keyword": kw},
                                )
                            )
                await asyncio.sleep(float(os.getenv("X_SCAN_DELAY_SEC", "1.5")))
            return ScanResult(platform=self.platform, candidates=candidates)
        except Exception as e:
            return ScanResult(
                platform=self.platform,
                candidates=_demo_candidates(keywords),
                error=str(e),
            )
