"""Chay pipeline cho tat ca input/*.json, hoac 1 case le de debug nhanh.

Vi du:
    python scripts/run_pipeline.py            # chay het 50 case, reset trace.jsonl truoc khi chay
    python scripts/run_pipeline.py EC_001      # chi chay 1 case (debug nhanh), KHONG reset trace
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.coordinator import run_case
from src.config import INPUT_DIR, OUTPUT_DIR
from src.tracing import reset_trace


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    case_filter = sys.argv[1] if len(sys.argv) > 1 else None

    if case_filter:
        paths = [INPUT_DIR / f"{case_filter}.json"]
    else:
        paths = sorted(INPUT_DIR.glob("EC_*.json"))
        reset_trace()  # README muc 8: trace.jsonl "khong append, chi can luot chay moi nhat"

    if not paths or not paths[0].exists():
        print(f"Khong tim thay input trong {INPUT_DIR} (case_filter={case_filter!r})")
        return

    ok, failed = 0, []
    t0 = time.time()
    for i, path in enumerate(paths, 1):
        try:
            run_case(path)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed.append((path.name, repr(exc)))
        print(f"[{i}/{len(paths)}] {path.name}", flush=True)

    print(f"\nXong {ok}/{len(paths)} case trong {time.time() - t0:.1f}s")
    if failed:
        print(f"{len(failed)} case LOI CA FALLBACK (khong chi bug logic - kiem tra ngay):")
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
