"""Tu kiem output/ TRUOC KHI dong goi nop bai. Chay: python scripts/validate_output.py
Kiem: du 50 file dung ten, parse + dung schema, evidence co that trong data/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from src.config import OUTPUT_DIR
from src.data_access import DataStore
from src.evidence import parse_evidence_id
from src.schemas import CaseOutput

EXPECTED = [f"EC_{i:03d}" for i in range(1, 51)]


def main() -> None:
    problems: list[str] = []
    store = DataStore.instance()

    found = {p.stem: p for p in OUTPUT_DIR.glob("EC_*.json")}
    missing = [c for c in EXPECTED if c not in found]
    extra = [name for name in found if name not in EXPECTED]
    if missing:
        problems.append(f"THIEU {len(missing)} file: {missing}")
    if extra:
        problems.append(f"File la trong output/ (khong thuoc 50 case chinh thuc): {extra}")

    for case_id in EXPECTED:
        path = found.get(case_id)
        if path is None:
            continue

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{case_id}: JSON khong parse duoc ({exc})")
            continue

        try:
            output = CaseOutput.model_validate(raw)
        except ValidationError as exc:
            problems.append(f"{case_id}: sai schema - {exc.errors()}")
            continue

        if output.case_id != case_id:
            problems.append(f"{case_id}: field case_id ben trong la {output.case_id!r}, khong khop ten file")

        for eid in output.evidence_ids:
            parsed = parse_evidence_id(eid)
            if parsed is None:
                problems.append(f"{case_id}: evidence sai dinh dang {eid!r}")
                continue
            kind, groups = parsed
            if kind == "order" and store.get_order(groups["order_id"]) is None:
                problems.append(f"{case_id}: evidence order khong ton tai {eid!r}")
            elif kind == "seller" and store.get_seller(groups["seller_id"]) is None:
                problems.append(f"{case_id}: evidence seller khong ton tai {eid!r}")
            elif kind == "item":
                items = store.get_items(groups["order_id"])
                if not any(str(it["order_item_id"]) == groups["item_id"] for it in items):
                    problems.append(f"{case_id}: evidence item khong ton tai {eid!r}")
            elif kind == "payment":
                payments = store.get_payments(groups["order_id"])
                if not any(str(p["payment_sequential"]) == groups["seq"] for p in payments):
                    problems.append(f"{case_id}: evidence payment khong ton tai {eid!r}")

    print(f"output/: {len(found)}/50 file")
    if problems:
        print(f"\n{len(problems)} VAN DE:")
        for p in problems:
            print(" -", p)
        sys.exit(1)

    print("OK - du 50 file, dung schema, evidence deu tra cuu duoc trong data/.")


if __name__ == "__main__":
    main()
