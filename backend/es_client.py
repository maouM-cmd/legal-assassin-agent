"""Elasticsearch client with in-memory fallback for demo mode."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SEED = ROOT / "data" / "reference_seed.jsonl"
EMBEDDING_DIMS = int(os.getenv("EMBEDDING_DIMS", "768"))

_es_client = None
_memory_references: list[dict[str, Any]] | None = None
_memory_hits: list[dict[str, Any]] = []
_memory_takedowns: list[dict[str, Any]] = []


def _load_memory_references() -> list[dict[str, Any]]:
    global _memory_references
    if _memory_references is not None:
        return _memory_references
    items: list[dict[str, Any]] = []
    if REFERENCE_SEED.exists():
        for line in REFERENCE_SEED.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                items.append(json.loads(line))
    _memory_references = items
    return items


def get_es():
    global _es_client
    if _es_client is not None:
        return _es_client
    api_key = os.getenv("ELASTIC_API_KEY", "").strip()
    if not api_key:
        return None
    cloud_id = os.getenv("ELASTIC_CLOUD_ID", "").strip()
    elastic_url = os.getenv("ELASTIC_URL", "").strip()
    if not cloud_id and not elastic_url:
        return None
    try:
        from elasticsearch import Elasticsearch

        if cloud_id:
            _es_client = Elasticsearch(cloud_id=cloud_id, api_key=api_key)
        else:
            _es_client = Elasticsearch(hosts=[elastic_url], api_key=api_key)
        if not _es_client.ping():
            _es_client = None
    except Exception:
        _es_client = None
    return _es_client


def reference_index() -> str:
    return os.getenv("ELASTIC_INDEX_REFERENCE", "reference_fingerprints")


def hits_index() -> str:
    return os.getenv("ELASTIC_INDEX_HITS", "infringement_hits")


def takedowns_index() -> str:
    return os.getenv("ELASTIC_INDEX_TAKEDOWNS", "takedown_requests")


def list_references() -> list[dict[str, Any]]:
    es = get_es()
    if es is None:
        return _load_memory_references()
    try:
        resp = es.search(index=reference_index(), query={"match_all": {}}, size=100)
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    except Exception:
        return _load_memory_references()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def knn_search_references(query_vector: list[float], k: int = 5) -> list[dict[str, Any]]:
    """Return top-K references by frame_embedding cosine similarity."""
    if not query_vector or not any(v != 0.0 for v in query_vector):
        return list_references()

    es = get_es()
    if es is None:
        refs = _load_memory_references()
        scored = []
        for ref in refs:
            emb = ref.get("frame_embedding")
            if emb and len(emb) == len(query_vector):
                scored.append((_cosine_similarity(query_vector, emb), ref))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:k]] or refs[:k]

    try:
        resp = es.search(
            index=reference_index(),
            knn={
                "field": "frame_embedding",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": max(k * 10, 20),
            },
            size=k,
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    except Exception:
        return list_references()[:k]


def index_reference(doc: dict[str, Any]) -> None:
    es = get_es()
    content_id = doc.get("content_id", "")
    if es is None:
        refs = _load_memory_references()
        refs[:] = [r for r in refs if r.get("content_id") != content_id]
        refs.append(doc)
        REFERENCE_SEED.parent.mkdir(parents=True, exist_ok=True)
        with REFERENCE_SEED.open("w", encoding="utf-8") as f:
            for item in refs:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return
    es.index(index=reference_index(), id=content_id, document=doc)


def _ensure_hit_id(hit: dict[str, Any]) -> str:
    hit_id = hit.get("hit_id")
    if not hit_id:
        hit_id = str(uuid.uuid4())
        hit["hit_id"] = hit_id
    return hit_id


def log_infringement_hit(hit: dict[str, Any]) -> str:
    hit.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    hit_id = _ensure_hit_id(hit)
    es = get_es()
    if es is None:
        _memory_hits.append(hit)
        if len(_memory_hits) > 500:
            _memory_hits.pop(0)
        return hit_id
    try:
        es.index(index=hits_index(), id=hit_id, document=hit)
    except Exception:
        _memory_hits.append(hit)
    return hit_id


def update_hit(hit_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    es = get_es()
    if es is None:
        for hit in _memory_hits:
            if hit.get("hit_id") == hit_id:
                hit.update(updates)
                return hit
        return None
    try:
        es.update(index=hits_index(), id=hit_id, doc=updates)
        return get_hit(hit_id)
    except Exception:
        for hit in _memory_hits:
            if hit.get("hit_id") == hit_id:
                hit.update(updates)
                return hit
        return None


def get_hit(hit_id: str) -> dict[str, Any] | None:
    es = get_es()
    if es is None:
        for hit in reversed(_memory_hits):
            if hit.get("hit_id") == hit_id:
                return hit
        return None
    try:
        resp = es.get(index=hits_index(), id=hit_id)
        return resp["_source"]
    except Exception:
        for hit in reversed(_memory_hits):
            if hit.get("hit_id") == hit_id:
                return hit
        return None


def log_takedown_request(req: dict[str, Any]) -> None:
    req.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    es = get_es()
    if es is None:
        _memory_takedowns.append(req)
        if len(_memory_takedowns) > 500:
            _memory_takedowns.pop(0)
        return
    try:
        es.index(index=takedowns_index(), document=req)
    except Exception:
        _memory_takedowns.append(req)


def list_hits(limit: int = 50, workflow_status: str | None = None) -> list[dict[str, Any]]:
    es = get_es()
    if es is None:
        items = list(reversed(_memory_hits[-limit * 2:]))
        if workflow_status:
            items = [h for h in items if h.get("workflow_status") == workflow_status]
        return items[:limit]
    try:
        query: dict[str, Any] = {"match_all": {}}
        if workflow_status:
            query = {"term": {"workflow_status.keyword": workflow_status}}
        resp = es.search(
            index=hits_index(),
            query=query,
            sort=[{"timestamp": {"order": "desc"}}],
            size=limit,
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    except Exception:
        items = list(reversed(_memory_hits[-limit:]))
        if workflow_status:
            items = [h for h in items if h.get("workflow_status") == workflow_status]
        return items


def list_takedowns(limit: int = 50, status: str | None = None) -> list[dict[str, Any]]:
    es = get_es()
    if es is None:
        items = list(reversed(_memory_takedowns[-limit * 2:]))
        if status:
            items = [t for t in items if t.get("status") == status]
        return items[:limit]
    try:
        query: dict[str, Any] = {"match_all": {}}
        if status:
            query = {"term": {"status.keyword": status}}
        resp = es.search(
            index=takedowns_index(),
            query=query,
            sort=[{"timestamp": {"order": "desc"}}],
            size=limit,
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    except Exception:
        items = list(reversed(_memory_takedowns[-limit:]))
        if status:
            items = [t for t in items if t.get("status") == status]
        return items


def url_already_processed(url: str) -> bool:
    es = get_es()
    if es is None:
        for hit in _memory_hits:
            if hit.get("suspect_url") == url and hit.get("workflow_status") != "rejected":
                return True
        for td in _memory_takedowns:
            if td.get("suspect_url") == url and td.get("status") == "submitted":
                return True
        return False
    try:
        resp = es.search(
            index=hits_index(),
            query={
                "bool": {
                    "must": [{"term": {"suspect_url.keyword": url}}],
                    "must_not": [{"term": {"workflow_status.keyword": "rejected"}}],
                }
            },
            size=1,
        )
        if resp["hits"]["hits"]:
            return True
        resp2 = es.search(
            index=takedowns_index(),
            query={
                "bool": {
                    "must": [
                        {"term": {"suspect_url.keyword": url}},
                        {"term": {"status.keyword": "submitted"}},
                    ]
                }
            },
            size=1,
        )
        return bool(resp2["hits"]["hits"])
    except Exception:
        return False


def update_takedown_by_url(suspect_url: str, updates: dict[str, Any]) -> None:
    es = get_es()
    if es is None:
        for td in _memory_takedowns:
            if td.get("suspect_url") == suspect_url:
                td.update(updates)
        return
    try:
        resp = es.search(
            index=takedowns_index(),
            query={"term": {"suspect_url.keyword": suspect_url}},
            size=1,
        )
        if resp["hits"]["hits"]:
            doc_id = resp["hits"]["hits"][0]["_id"]
            es.update(index=takedowns_index(), id=doc_id, doc=updates)
    except Exception:
        pass


def list_failed_takedowns(limit: int = 20) -> list[dict[str, Any]]:
    return list_takedowns(limit, status="failed")


def list_failed_takedowns_ready(limit: int = 20) -> list[dict[str, Any]]:
    """Failed takedowns that passed exponential backoff window."""
    from backend.dmca.retry import is_ready_for_retry

    failed = list_failed_takedowns(limit * 5)
    ready = [td for td in failed if is_ready_for_retry(td)]
    return ready[:limit]


def get_stats() -> dict[str, Any]:
    hits = list_hits(1000)
    takedowns = list_takedowns(1000)
    submitted = sum(1 for t in takedowns if t.get("status") == "submitted")
    pending_approval = sum(1 for h in hits if h.get("workflow_status") == "pending_approval")
    pending_manual = sum(1 for t in takedowns if t.get("status") == "pending_manual")
    failed = sum(1 for t in takedowns if t.get("status") == "failed")
    return {
        "hits_total": len(hits),
        "takedowns_total": len(takedowns),
        "takedowns_submitted": submitted,
        "takedowns_failed": failed,
        "pending_approval": pending_approval,
        "pending_manual": pending_manual,
        "references_total": len(list_references()),
    }
