"""Smoke tests for Legal Assassin Agent API."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.getenv("LEGAL_ASSASSIN_BASE", "http://127.0.0.1:8001")


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as resp:
        return json.loads(resp.read().decode())


def _post(path: str, body: dict | None = None) -> dict:
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    errors: list[str] = []

    try:
        health = _get("/api/health")
        assert health.get("status") == "ok", health
        assert "hybrid_match" in health, health
        print("[OK] /api/health")
    except Exception as e:
        errors.append(f"health: {e}")

    try:
        stats = _get("/api/stats")
        assert "pending_approval" in stats, stats
        print("[OK] /api/stats")
    except Exception as e:
        errors.append(f"stats: {e}")

    try:
        queue = _get("/api/review-queue")
        assert "items" in queue, queue
        print("[OK] /api/review-queue")
    except Exception as e:
        errors.append(f"review-queue: {e}")

    root = Path(__file__).resolve().parents[1]
    evasion = root / "data" / "evasion_samples"
    sample = next(evasion.glob("*.mp4"), None) if evasion.exists() else None

    if sample:
        try:
            result = _post("/api/analyze", {
                "video_path": str(sample),
                "platform": "demo",
                "suspect_url": f"file://{sample}",
            })
            print(f"[OK] /api/analyze - {len(result.get('matches', []))} match(es)")
        except Exception as e:
            errors.append(f"analyze: {e}")
    else:
        print("[SKIP] /api/analyze — no evasion samples")

    try:
        patrol = _post("/api/patrol")
        assert "platforms" in patrol, patrol
        print("[OK] /api/patrol")
    except Exception as e:
        errors.append(f"patrol: {e}")

    try:
        retry = _post("/api/takedowns/retry")
        assert "retried" in retry, retry
        print("[OK] /api/takedowns/retry")
    except Exception as e:
        errors.append(f"takedowns-retry: {e}")

    try:
        req = urllib.request.Request(f"{BASE}/api/audit/export", method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            disposition = resp.headers.get("Content-Disposition", "")
            assert "timestamp" in body
            assert "legal_assassin" in disposition.lower() or "attachment" in disposition.lower()
        print("[OK] /api/audit/export")
    except Exception as e:
        errors.append(f"audit-export: {e}")

    try:
        req = urllib.request.Request(f"{BASE}/api/audit/export?from=2020-01-01&to=2030-01-01", method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            assert "timestamp" in body
        print("[OK] /api/audit/export?from=&to=")
    except Exception as e:
        errors.append(f"audit-export-alias: {e}")

    try:
        hits = _get("/api/hits?limit=1")
        items = hits.get("items") or []
        if items:
            hit_id = items[0].get("hit_id")
            thumb = _get(f"/api/hits/{hit_id}/thumbnails")
            assert thumb.get("hit_id") == hit_id
            print("[OK] /api/hits/{id}/thumbnails")
        else:
            print("[SKIP] /api/hits/{id}/thumbnails — no hits yet")
    except Exception as e:
        errors.append(f"thumbnails: {e}")

    if errors:
        print("\nFAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nAll smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
