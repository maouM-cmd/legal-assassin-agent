"""Unit tests for video hashing."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.fingerprint.video_hash import compare_hash_sequences, hash_similarity


def test_hash_similarity_identical():
    h = "c4c43b3bc4c43b3b"
    assert hash_similarity(h, h) == 1.0


def test_hash_similarity_different():
    a = "0000000000000000"
    b = "ffffffffffffffff"
    assert hash_similarity(a, b) < 0.5


def test_compare_hash_sequences():
    ref = ["a" * 16, "b" * 16, "c" * 16]
    suspect = ["a" * 16, "b" * 16]
    score = compare_hash_sequences(ref, suspect)
    assert score == 1.0
