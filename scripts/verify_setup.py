"""Verify Legal Assassin Agent setup (submission gate)."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MIN_REFERENCE_CLIPS = 1
MIN_EVASION_SAMPLES = 5


def _mask(val: str) -> str:
    if not val:
        return "(not set)"
    if len(val) <= 8:
        return "***"
    return val[:4] + "..." + val[-4:]


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def main() -> int:
    print("=== Legal Assassin Setup Verification ===\n")
    errors: list[str] = []

    checks = [
        ("ELASTIC_API_KEY", os.getenv("ELASTIC_API_KEY", "")),
        ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")),
        ("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY", "")),
        ("X_BEARER_TOKEN", os.getenv("X_BEARER_TOKEN", "")),
        ("DEMO_MODE", os.getenv("DEMO_MODE", "true")),
        ("WEBHOOK_ENABLED", os.getenv("WEBHOOK_ENABLED", "false")),
        ("API_KEY", os.getenv("API_KEY", "")),
    ]
    for name, val in checks:
        display = val if name == "DEMO_MODE" or name == "WEBHOOK_ENABLED" else _mask(val)
        print(f"  {name}: {display}")

    ref_dir = ROOT / "data" / "reference_clips"
    evasion_dir = ROOT / "data" / "evasion_samples"
    ref_count = len(list(ref_dir.glob("*.mp4"))) if ref_dir.exists() else 0
    evasion_count = len(list(evasion_dir.glob("*.mp4"))) if evasion_dir.exists() else 0
    print(f"\n  Reference clips: {ref_count} (required >= {MIN_REFERENCE_CLIPS})")
    print(f"  Evasion samples: {evasion_count} (required >= {MIN_EVASION_SAMPLES})")

    if ref_count < MIN_REFERENCE_CLIPS:
        errors.append(
            f"Need at least {MIN_REFERENCE_CLIPS} reference clip - run .\\scripts\\bootstrap.ps1"
        )
    if evasion_count < MIN_EVASION_SAMPLES:
        errors.append(
            f"Need at least {MIN_EVASION_SAMPLES} evasion samples - run .\\scripts\\bootstrap.ps1"
        )

    print("\n  Optional tools:")
    for tool in ("ffmpeg", "fpcalc"):
        ok = _tool_available(tool)
        print(f"    {tool}: {'OK' if ok else 'not found (degraded mode)'}")
    try:
        import playwright  # noqa: F401

        print("    playwright: OK")
    except ImportError:
        print("    playwright: not installed")

    try:
        from backend.es_client import get_es

        es = get_es()
        print(f"\n  Elasticsearch: {'connected' if es else 'demo mode (in-memory)'}")
    except Exception as e:
        print(f"\n  Elasticsearch: error — {e}")

    if errors:
        print("\nFAILED:")
        for err in errors:
            print(f"  - {err}")
        print("\nFix: .\\scripts\\bootstrap.ps1")
        return 1

    print("\nSetup OK - ready for demo.")
    print("  .\\start.bat  ->  http://localhost:8001")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
