"""Create Elasticsearch indices for Legal Assassin."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def main() -> int:
    from backend.es_client import get_es, hits_index, reference_index, takedowns_index

    es = get_es()
    if es is None:
        print("Elasticsearch not configured — skipping index creation")
        return 0

    dims = int(os.getenv("EMBEDDING_DIMS", "768"))
    ref_mapping = {
        "mappings": {
            "properties": {
                "content_id": {"type": "keyword"},
                "title": {"type": "text"},
                "frame_hashes": {"type": "keyword"},
                "audio_fingerprint": {"type": "keyword"},
                "duration_sec": {"type": "float"},
                "frame_embedding": {
                    "type": "dense_vector",
                    "dims": dims,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        }
    }
    event_mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "hit_id": {"type": "keyword"},
                "platform": {"type": "keyword"},
                "content_id": {"type": "keyword"},
                "final_score": {"type": "float"},
                "evasion_types": {"type": "keyword"},
                "status": {"type": "keyword"},
                "workflow_status": {"type": "keyword"},
                "suspect_url": {"type": "keyword"},
                "legal_hold": {"type": "boolean"},
                "counter_notification_status": {"type": "keyword"},
                "counter_notification_at": {"type": "date"},
                "counter_notification_notes": {"type": "text"},
            }
        }
    }

    takedown_mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "hit_id": {"type": "keyword"},
                "platform": {"type": "keyword"},
                "content_id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "suspect_url": {"type": "keyword"},
                "legal_hold": {"type": "boolean"},
                "counter_notification_status": {"type": "keyword"},
                "counter_notification_at": {"type": "date"},
                "counter_notification_notes": {"type": "text"},
                "legal_hold_notes": {"type": "text"},
                "retry_count": {"type": "integer"},
            }
        }
    }

    for name, mapping in [
        (reference_index(), ref_mapping),
        (hits_index(), event_mapping),
        (takedowns_index(), takedown_mapping),
    ]:
        if not es.indices.exists(index=name):
            es.indices.create(index=name, body=mapping)
            print(f"Created index: {name}")
        else:
            print(f"Index exists: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
