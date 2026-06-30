"""Index reference clips into Elasticsearch / memory store."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.reference.indexer import index_directory, index_video


def main() -> int:
    clips_dir = ROOT / "data" / "reference_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    mp4s = list(clips_dir.glob("*.mp4"))
    if not mp4s:
        print(f"No MP4 files in {clips_dir}")
        print("Place owned reference videos there, then re-run.")
        return 1

    results = index_directory(clips_dir)
    print(f"Indexed {len(results)} reference(s):")
    for doc in results:
        print(f"  - {doc['content_id']}: {len(doc.get('frame_hashes', []))} frame hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
