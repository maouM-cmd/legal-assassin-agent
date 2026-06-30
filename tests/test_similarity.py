"""Unit tests for similarity scoring."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.matchers.similarity import compute_final_score


def test_compute_final_score_balanced():
    score = compute_final_score(0.8, 0.8, 0.8)
    assert abs(score - 0.8) < 0.01


def test_compute_final_score_evasion_boost():
    score = compute_final_score(0.9, 0.5, 0.8, evasion_types=["flipped"])
    assert score > 0.8


def test_compute_final_score_low():
    score = compute_final_score(0.3, 0.3, 0.3)
    assert score < 0.5
