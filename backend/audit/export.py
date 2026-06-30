"""Export infringement hits and takedowns as compliance CSV."""
from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any

from backend.es_client import list_hits, list_takedowns


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _in_range(ts: str | None, start: datetime | None, end: datetime | None) -> bool:
    dt = _parse_ts(ts)
    if dt is None:
        return start is None and end is None
    if start and dt < start:
        return False
    if end and dt > end:
        return False
    return True


def export_compliance_report(
    start: datetime | None = None,
    end: datetime | None = None,
) -> str:
    hits = list_hits(2000)
    takedowns = list_takedowns(2000)

    td_by_url: dict[str, dict[str, Any]] = {}
    for td in takedowns:
        url = td.get("suspect_url", "")
        if url and url not in td_by_url:
            td_by_url[url] = td

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "timestamp",
            "platform",
            "content_id",
            "suspect_url",
            "final_score",
            "evasion_types",
            "workflow_status",
            "takedown_status",
        ]
    )

    for hit in hits:
        ts = hit.get("timestamp")
        if not _in_range(ts, start, end):
            continue
        url = hit.get("suspect_url", "")
        td = td_by_url.get(url, {})
        evasion = hit.get("evasion_types", [])
        evasion_str = ",".join(evasion) if isinstance(evasion, list) else str(evasion)
        writer.writerow(
            [
                ts,
                hit.get("platform", ""),
                hit.get("content_id", ""),
                url,
                hit.get("final_score", ""),
                evasion_str,
                hit.get("workflow_status", hit.get("status", "")),
                td.get("status", ""),
            ]
        )

    return output.getvalue()
