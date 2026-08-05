"""Vai tro 5: Verifier Agent.
Kiem schema, evidence co that, va so tien nhat quan TRUOC KHI cho phep ghi file output.
KHONG tu y "sua" quyet dinh cua Policy Agent - chi tra pass/fail + ly do, Coordinator quyet
dinh buoc tiep theo (xem coordinator.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import ValidationError

from src.data_access import DataStore
from src.evidence import parse_evidence_id
from src.schemas import CaseOutput


@dataclass
class VerifyResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


def validate_schema(raw: dict) -> tuple[CaseOutput | None, list[str]]:
    """Parse + validate 1 dict theo CaseOutput (README muc 6). Dung TRUOC khi goi verify()."""
    try:
        return CaseOutput.model_validate(raw), []
    except ValidationError as exc:
        return None, [str(e) for e in exc.errors()]


def verify(output: CaseOutput) -> VerifyResult:
    store = DataStore.instance()
    errors: list[str] = []
    errors.extend(_check_evidence_exists(output, store))
    errors.extend(_check_financial_consistency(output))
    return VerifyResult(ok=not errors, errors=errors)


def _check_evidence_exists(output: CaseOutput, store: DataStore) -> list[str]:
    """Tra nguoc tung evidence_id vao data that - ID bia hoac sai dinh dang la 1 nguyen nhan hard-gate."""
    errors: list[str] = []
    for eid in output.evidence_ids:
        parsed = parse_evidence_id(eid)
        if parsed is None:
            errors.append(f"evidence_id sai dinh dang: {eid!r}")
            continue
        kind, groups = parsed
        if kind == "order" and store.get_order(groups["order_id"]) is None:
            errors.append(f"evidence order khong ton tai: {eid!r}")
        elif kind == "item":
            items = store.get_items(groups["order_id"])
            if not any(str(it["order_item_id"]) == groups["item_id"] for it in items):
                errors.append(f"evidence item khong ton tai: {eid!r}")
        elif kind == "payment":
            payments = store.get_payments(groups["order_id"])
            if not any(str(p["payment_sequential"]) == groups["seq"] for p in payments):
                errors.append(f"evidence payment khong ton tai: {eid!r}")
        elif kind == "seller" and store.get_seller(groups["seller_id"]) is None:
            errors.append(f"evidence seller khong ton tai: {eid!r}")
        # "policy:<cause_code>" luon hop le neu dung dinh dang - khong tra CSV.
    return errors


def _check_financial_consistency(output: CaseOutput) -> list[str]:
    """Kiem tra noi bo: action da chon co khop cong thuc refund tuong ung khong (README muc 4)."""
    errors: list[str] = []
    fr = output.financial_resolution
    actions = set(output.resolution_actions)

    if "issue_full_refund" in actions and round(fr.recommended_refund_brl, 2) != round(fr.payment_total_brl, 2):
        errors.append("issue_full_refund nhung recommended_refund_brl != payment_total_brl")
    if "refund_freight" in actions and round(fr.recommended_refund_brl, 2) != round(fr.freight_total_brl, 2):
        errors.append("refund_freight nhung recommended_refund_brl != freight_total_brl")
    if actions & {"explain_valid_split_payment", "reject_late_refund"} and fr.recommended_refund_brl != 0.0:
        errors.append("action khong hoan tien nhung recommended_refund_brl != 0.0")

    if output.assessment.case_status == "action_required" and fr.recommended_refund_brl <= 0:
        errors.append("case_status=action_required nhung recommended_refund_brl <= 0")
    if output.assessment.case_status == "no_action" and fr.recommended_refund_brl != 0:
        errors.append("case_status=no_action nhung recommended_refund_brl != 0")

    return errors
