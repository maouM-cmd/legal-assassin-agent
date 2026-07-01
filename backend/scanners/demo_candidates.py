"""Demo scan candidates from local evasion sample files."""
from __future__ import annotations

from pathlib import Path

from backend.scanners.base import ScanCandidate


def demo_candidates(keywords: list[str], platform: str = "youtube") -> list[ScanCandidate]:
    root = Path(__file__).resolve().parents[2]
    evasion_dir = root / "data" / "evasion_samples"
    out: list[ScanCandidate] = []
    if evasion_dir.exists():
        for mp4 in sorted(evasion_dir.glob("*.mp4")):
            out.append(
                ScanCandidate(
                    platform=platform,
                    url=mp4.resolve().as_uri(),
                    title=mp4.stem,
                    metadata={"demo": True, "keyword": keywords[0] if keywords else ""},
                )
            )
    return out
