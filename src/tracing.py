"""Append 1 dong JSON vao logging/trace.jsonl cho moi buoc handoff giua cac agent.
README muc 8: "trace chay that cua 50 case (khong append, chi can luot chay moi nhat)"
-> reset_trace() duoc goi 1 lan dau moi luot chay FULL batch (xem scripts/run_pipeline.py),
KHONG goi khi chay debug 1 case le (se xoa mat trace cua lan chay full gan nhat).
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Any

from src.config import TRACE_PATH

_lock = threading.Lock()


def reset_trace() -> None:
    """Xoa trace cu, bat dau ghi lai tu dau cho 1 luot chay full moi."""
    with _lock:
        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        TRACE_PATH.write_text("", encoding="utf-8")


def log_step(case_id: str, agent: str, event: str, data: dict[str, Any] | None = None) -> None:
    """Ghi 1 dong trace. Goi cho MOI buoc handoff: agent nhan input, agent tra facts,
    policy quyet dinh, verifier pass/fail, coordinator ghi file..."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "agent": agent,
        "event": event,
        "data": data or {},
    }
    with _lock:
        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
