"""Test verifier_agent.py - cac check cau truc (schema, evidence co that, so tien nhat quan).
Day la QA tooling, khong phu thuoc logic 6-rule (chua implement) nen chay duoc ngay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.verifier_agent import verify
from src.schemas import (
    AffectedEntities,
    Assessment,
    CaseOutput,
    FinancialResolution,
    RootCauseAnalysis,
)


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
