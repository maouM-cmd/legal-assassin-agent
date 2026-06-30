"""DMCA notice generation from Jinja2 template."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "data" / "dmca_templates"


def _rights_holder_info() -> dict[str, str]:
    return {
        "rights_holder_name": os.getenv("RIGHTS_HOLDER_NAME", "Rights Holder Inc."),
        "rights_holder_address": os.getenv("RIGHTS_HOLDER_ADDRESS", "123 Copyright Ave"),
        "rights_holder_email": os.getenv("RIGHTS_HOLDER_EMAIL", "legal@example.com"),
        "rights_holder_phone": os.getenv("RIGHTS_HOLDER_PHONE", "+1-000-000-0000"),
    }


def generate_dmca_notice(hit: dict[str, Any]) -> dict[str, Any]:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    template = env.get_template("dmca_notice.j2")
    evasion = hit.get("evasion_types", [])
    evasion_str = ", ".join(evasion) if evasion else "none detected"

    ctx = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "platform": hit.get("platform", "unknown"),
        "reference_title": hit.get("reference_title", ""),
        "content_id": hit.get("content_id", ""),
        "suspect_url": hit.get("suspect_url", ""),
        "evasion_types": evasion_str,
        **_rights_holder_info(),
    }
    body = template.render(**ctx)
    return {
        "platform": hit.get("platform"),
        "suspect_url": hit.get("suspect_url"),
        "content_id": hit.get("content_id"),
        "body": body,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
