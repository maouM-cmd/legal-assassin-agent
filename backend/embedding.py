"""Gemini text embeddings with mock zero-vector fallback."""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
DIMS = int(os.getenv("EMBEDDING_DIMS", "768"))
_FALLBACK_MODEL = "models/gemini-embedding-001"


def _mock_vector() -> list[float]:
    return [0.0] * DIMS


def _has_api_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def _normalize(vec: list[float]) -> list[float]:
    if len(vec) == DIMS:
        return vec
    if len(vec) > DIMS:
        return vec[:DIMS]
    return vec + [0.0] * (DIMS - len(vec))


def _embed_with_genai(text: str, task_type: str) -> list[float]:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    models_to_try = [MODEL]
    if MODEL != _FALLBACK_MODEL:
        models_to_try.append(_FALLBACK_MODEL)

    last_err: Exception | None = None
    for model in models_to_try:
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "content": text,
                "task_type": task_type,
            }
            if "gemini-embedding" in model and DIMS < 3072:
                kwargs["output_dimensionality"] = DIMS
            result = genai.embed_content(**kwargs)
            return _normalize(list(result["embedding"]))
        except Exception as exc:
            last_err = exc
            continue
    if last_err:
        raise last_err
    return _mock_vector()


def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    if not _has_api_key() or not text.strip():
        return _mock_vector()
    try:
        return _embed_with_genai(text, task_type)
    except Exception:
        return _mock_vector()


def embed_query(text: str) -> list[float]:
    return embed_text(text, task_type="retrieval_query")


def embed_reference(content_id: str, title: str, scene_summary: str = "") -> list[float]:
    text = f"{title} {content_id} {scene_summary}".strip()
    return embed_text(text, task_type="retrieval_document")
