"""Base scanner interface for platform patrol."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ScanCandidate:
    platform: str
    url: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    platform: str
    candidates: list[ScanCandidate]
    scanned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str | None = None


class BaseScanner(ABC):
    platform: str = "unknown"

    @abstractmethod
    async def scan(self, keywords: list[str]) -> ScanResult:
        ...
