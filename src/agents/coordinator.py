"""Vai tro 5: Coordinator.
Chay pipeline cho 1 case: doc input -> goi 3 agent du lieu -> goi Policy -> build output ->
goi Verifier -> ghi file. KHONG BAO GIO de 1 case loi lam thieu file trong output/ - loi thi
van ghi 1 JSON hop le schema, confidence thap, va log loi vao trace (dem du 50 file la 1 dieu
kien hard-gate - xem README muc 8 va architecture.md muc 7).
"""
from __future__ import annotations

import json
from pathlib import Path

from src.agents import delivery_agent, order_seller_agent, payment_agent, policy_agent, verifier_agent
from src.config import OUTPUT_DIR
from src.evidence import evidence_policy
from src.schemas import (
    AffectedEntities,
    Assessment,
    CaseOutput,
    FinancialResolution,
    RankedCause,
    ResponsibleParty,
    RootCauseAnalysis,
)
from src.tracing import log_step

# Vai tro 5 - quyet dinh xu ly verify_fail (xem architecture.md muc 6): khi Verifier bao
# fail (evidence/so tien khong nhat quan) nhung KHONG phai loi schema, van ghi output (dam bao
# du 50 file - hard-gate), nhung ha confidence xuong nguong nay de danh dau "can review tay".
# Khong tu y sua lai quyet dinh cua Policy Agent - chi giam do tin cay va log.
VERIFY_FAIL_CONFIDENCE = 0.1


def run_case(input_path: Path) -> Path:
    case_id = input_path.stem
    raw_input = json.loads(input_path.read_text(encoding="utf-8"))
    order_id = raw_input["customer_request"]["claimed_order_id"]
    log_step(case_id, "coordinator", "case_started", {"order_id": order_id})

    try:
        output = _process(case_id, order_id)
    except Exception as exc:  # noqa: BLE001 - khong duoc de 1 case loi lam thieu file output
        log_step(case_id, "coordinator", "case_failed_fallback", {"error": repr(exc)})
        output = _fallback_output(case_id)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{case_id}.json"
    out_path.write_text(json.dumps(output.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    log_step(case_id, "coordinator", "case_written", {"path": str(out_path)})
    return out_path


def _process(case_id: str, order_id: str) -> CaseOutput:
    os_facts = order_seller_agent.investigate(order_id)
    log_step(case_id, "order_seller_agent", "facts", {"evidence_ids": os_facts.evidence_ids})

    pay_facts = payment_agent.investigate(order_id, os_facts.item_total_brl, os_facts.freight_total_brl)
    log_step(case_id, "payment_agent", "facts", {"evidence_ids": pay_facts.evidence_ids})

    deliv_facts = delivery_agent.investigate(order_id)
    log_step(case_id, "delivery_agent", "facts", {"evidence_ids": deliv_facts.evidence_ids})

    decision = policy_agent.decide(os_facts, pay_facts, deliv_facts)
    log_step(case_id, "policy_agent", "decision", {"primary_issue": decision.primary_issue})

    evidence_ids = list(
        dict.fromkeys(os_facts.evidence_ids + pay_facts.evidence_ids + deliv_facts.evidence_ids + decision.evidence_ids)
    )[:10]

    responsible_parties = []
    if decision.responsible_party_type and decision.responsible_party_id:
        responsible_parties.append(
            ResponsibleParty(party_type=decision.responsible_party_type, party_id=decision.responsible_party_id)
        )

    # DA CHOT (Vai tro 5, xac nhan voi Vai tro 1/4 - xem architecture.md muc 6): seller_ids trong
    # affected_entities = cac seller "vi pham" (os_facts.late_seller_ids), KHONG liet ke tat ca
    # seller cua don. Ly do: affected_entities la cac ben BI QUY TRACH NHIEM trong assessment,
    # khong phai danh sach lien quan chung chung. Chi rule 3 (late_delivery_seller) co seller
    # trach nhiem -> field nay chi non-empty o rule 3; cac rule khac late_seller_ids rong -> [] la
    # dung y (trach nhiem thuoc platform/logistics/khong ai). Giu nhat quan voi responsible_party.
    output = CaseOutput(
        case_id=case_id,
        assessment=Assessment(
            primary_issue=decision.primary_issue,
            case_status=decision.case_status,
            confidence=decision.confidence,
        ),
        affected_entities=AffectedEntities(
            order_ids=[order_id][:5],
            item_ids=[f"{order_id}:{it['order_item_id']}" for it in os_facts.items][:5],
            seller_ids=list(dict.fromkeys(os_facts.late_seller_ids))[:5],
            payment_ids=[f"{order_id}:{p['payment_sequential']}" for p in pay_facts.payments][:5],
        ),
        root_cause_analysis=RootCauseAnalysis(
            ranked_causes=[RankedCause(cause_code=decision.cause_code, rank=1)],
            responsible_parties=responsible_parties,
        ),
        evidence_ids=evidence_ids,
        financial_resolution=FinancialResolution(
            item_total_brl=os_facts.item_total_brl,
            freight_total_brl=os_facts.freight_total_brl,
            payment_total_brl=pay_facts.payment_total_brl,
            recommended_refund_brl=decision.recommended_refund_brl,
        ),
        resolution_actions=[decision.resolution_action],
    )

    parsed, schema_errors = verifier_agent.validate_schema(output.model_dump())
    if schema_errors:
        log_step(case_id, "verifier_agent", "schema_fail", {"errors": schema_errors})
        raise ValueError(f"schema invalid: {schema_errors}")

    result = verifier_agent.verify(output)
    if not result.ok:
        log_step(case_id, "verifier_agent", "verify_fail", {"errors": result.errors})
        # DA CHOT (Vai tro 5): verify fail (khong phai loi schema) -> KHONG sua so lieu cua
        # Policy Agent, nhung ha confidence xuong VERIFY_FAIL_CONFIDENCE de danh dau case can
        # review tay. Van ghi file (dam bao du 50 - hard-gate) thay vi bo trong.
        if output.assessment.confidence > VERIFY_FAIL_CONFIDENCE:
            output = output.model_copy(
                update={
                    "assessment": output.assessment.model_copy(
                        update={"confidence": VERIFY_FAIL_CONFIDENCE}
                    )
                }
            )
        log_step(
            case_id,
            "coordinator",
            "verify_fail_flagged",
            {"confidence": output.assessment.confidence},
        )
    else:
        log_step(case_id, "verifier_agent", "verify_pass", {})

    return output


def _fallback_output(case_id: str) -> CaseOutput:
    """JSON hop le schema, confidence = 0 - dung khi _process loi bat ky buoc nao, de KHONG
    BAO GIO thieu file trong output/ (dem du 50 file la 1 dieu kien hard-gate)."""
    cause = "DELIVERY_WITHIN_ESTIMATE"
    return CaseOutput(
        case_id=case_id,
        assessment=Assessment(primary_issue="unsupported_late_claim", case_status="no_action", confidence=0.0),
        affected_entities=AffectedEntities(),
        root_cause_analysis=RootCauseAnalysis(ranked_causes=[RankedCause(cause_code=cause, rank=1)]),
        evidence_ids=[evidence_policy(cause)],
        financial_resolution=FinancialResolution(
            item_total_brl=0.0, freight_total_brl=0.0, payment_total_brl=0.0, recommended_refund_brl=0.0
        ),
        resolution_actions=["reject_late_refund"],
    )
