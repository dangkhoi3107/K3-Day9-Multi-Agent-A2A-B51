"""Test verifier_agent.py - cac check cau truc (schema, evidence co that, so tien nhat quan).
Day la QA tooling, khong phu thuoc logic 6-rule (chua implement) nen chay duoc ngay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.verifier_agent import validate_schema, verify
from src.schemas import (
    AffectedEntities,
    Assessment,
    CaseOutput,
    FinancialResolution,
    RootCauseAnalysis,
)

# Order that really exists (from input/EC_001.json), dung de test "ton tai nhung sai sub-id".
REAL_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"


def _base_output(**overrides) -> CaseOutput:
    base = dict(
        case_id="EC_TEST",
        assessment=Assessment(primary_issue="unsupported_late_claim", case_status="no_action", confidence=0.9),
        affected_entities=AffectedEntities(),
        root_cause_analysis=RootCauseAnalysis(),
        evidence_ids=[],
        financial_resolution=FinancialResolution(
            item_total_brl=0.0, freight_total_brl=0.0, payment_total_brl=0.0, recommended_refund_brl=0.0
        ),
        resolution_actions=["reject_late_refund"],
    )
    base.update(overrides)
    return CaseOutput(**base)


def test_fabricated_order_evidence_is_rejected():
    output = _base_output(evidence_ids=["order:khong-ton-tai-000"])
    result = verify(output)
    assert result.ok is False
    assert any("khong ton tai" in e for e in result.errors)


def test_malformed_evidence_id_is_rejected():
    output = _base_output(evidence_ids=["order-thieu-dau-hai-cham"])
    result = verify(output)
    assert result.ok is False
    assert any("sai dinh dang" in e for e in result.errors)


def test_no_action_with_nonzero_refund_is_rejected():
    output = _base_output(
        assessment=Assessment(primary_issue="unsupported_late_claim", case_status="no_action", confidence=0.9),
        financial_resolution=FinancialResolution(
            item_total_brl=0.0, freight_total_brl=0.0, payment_total_brl=0.0, recommended_refund_brl=10.0
        ),
    )
    result = verify(output)
    assert result.ok is False


def test_clean_output_passes():
    output = _base_output()
    result = verify(output)
    assert result.ok is True
    assert result.errors == []


# ---- Them: evidence ton tai order that nhung sai sub-id (item/payment/seller) --------------


def test_fabricated_item_evidence_is_rejected():
    """Order co that, nhung order_item_id 999 khong ton tai trong don do."""
    output = _base_output(evidence_ids=[f"item:{REAL_ORDER_ID}:999"])
    result = verify(output)
    assert result.ok is False
    assert any("item" in e and "khong ton tai" in e for e in result.errors)


def test_fabricated_payment_evidence_is_rejected():
    """Order co that, nhung payment_sequential 999 khong ton tai trong don do."""
    output = _base_output(evidence_ids=[f"payment:{REAL_ORDER_ID}:999"])
    result = verify(output)
    assert result.ok is False
    assert any("payment" in e and "khong ton tai" in e for e in result.errors)


def test_fabricated_seller_evidence_is_rejected():
    output = _base_output(evidence_ids=["seller:seller-bia-khong-co-that"])
    result = verify(output)
    assert result.ok is False
    assert any("seller" in e and "khong ton tai" in e for e in result.errors)


# ---- Them: so tien khong khop voi action da chon --------------------------------------------


def test_issue_full_refund_mismatch_is_rejected():
    """Action issue_full_refund nhung recommended_refund_brl khac payment_total_brl."""
    output = _base_output(
        assessment=Assessment(primary_issue="canceled_order_paid", case_status="action_required", confidence=0.9),
        financial_resolution=FinancialResolution(
            item_total_brl=100.0, freight_total_brl=15.0, payment_total_brl=115.0, recommended_refund_brl=50.0
        ),
        resolution_actions=["issue_full_refund"],
    )
    result = verify(output)
    assert result.ok is False


def test_refund_freight_mismatch_is_rejected():
    """Action refund_freight nhung recommended_refund_brl khac freight_total_brl."""
    output = _base_output(
        assessment=Assessment(primary_issue="late_delivery_seller", case_status="action_required", confidence=0.9),
        financial_resolution=FinancialResolution(
            item_total_brl=100.0, freight_total_brl=15.0, payment_total_brl=115.0, recommended_refund_brl=15.01
        ),
        resolution_actions=["refund_freight"],
    )
    result = verify(output)
    assert result.ok is False


def test_action_required_with_zero_refund_is_rejected():
    output = _base_output(
        assessment=Assessment(primary_issue="canceled_order_paid", case_status="action_required", confidence=0.9),
        resolution_actions=["issue_full_refund"],
    )
    result = verify(output)
    assert result.ok is False


# ---- Them: vi pham schema (Pydantic phai chan truoc khi toi verify()) -----------------------


def test_confidence_out_of_range_is_rejected_by_schema():
    raw = _base_output().model_dump()
    raw["assessment"]["confidence"] = 1.5
    parsed, errors = validate_schema(raw)
    assert parsed is None
    assert errors


def test_too_many_evidence_ids_is_rejected_by_schema():
    raw = _base_output().model_dump()
    raw["evidence_ids"] = [f"policy:CODE_{i}" for i in range(11)]  # gioi han la 10
    parsed, errors = validate_schema(raw)
    assert parsed is None
    assert errors


def test_invalid_primary_issue_is_rejected_by_schema():
    raw = _base_output().model_dump()
    raw["assessment"]["primary_issue"] = "khong_nam_trong_6_gia_tri_hop_le"
    parsed, errors = validate_schema(raw)
    assert parsed is None
    assert errors
