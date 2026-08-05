"""Pydantic models khop dung schema input (README muc 3) va output (README muc 6).
Day la "hop dong" dung chung cho ca 5 nguoi - khong tu y doi field/kieu du lieu o day
ma khong bao ca nhom, vi Coordinator, Policy va Verifier deu dua vao dung cac model nay.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

POLICY_VERSION = "EC_POLICY_V1"

PrimaryIssue = Literal[
    "canceled_order_paid",
    "unavailable_order_paid",
    "late_delivery_seller",
    "late_delivery_logistics",
    "valid_split_payment",
    "unsupported_late_claim",
]

CauseCode = Literal[
    "SELLER_HANDOFF_AFTER_LIMIT",
    "CARRIER_DELIVERED_AFTER_ESTIMATE",
    "ORDER_CANCELED_AFTER_PAYMENT",
    "ORDER_UNAVAILABLE_AFTER_PAYMENT",
    "MULTIPLE_PAYMENTS_RECONCILED",
    "DELIVERY_WITHIN_ESTIMATE",
]

ResolutionAction = Literal[
    "issue_full_refund",
    "refund_freight",
    "explain_valid_split_payment",
    "reject_late_refund",
]

PartyType = Literal["platform", "seller", "logistics_provider"]


# ---- Input (README muc 3) ----------------------------------------------------


class CustomerRequest(BaseModel):
    language: str
    message: str
    claimed_order_id: str


class CaseInput(BaseModel):
    case_id: str
    opened_at: str
    customer_request: CustomerRequest
    policy_version: str


# ---- Output (README muc 6) ----------------------------------------------------


class Assessment(BaseModel):
    primary_issue: PrimaryIssue
    case_status: Literal["action_required", "no_action"]
    confidence: float = Field(ge=0.0, le=1.0)


class AffectedEntities(BaseModel):
    order_ids: list[str] = Field(default_factory=list, max_length=5)
    item_ids: list[str] = Field(default_factory=list, max_length=5)
    seller_ids: list[str] = Field(default_factory=list, max_length=5)
    payment_ids: list[str] = Field(default_factory=list, max_length=5)


class RankedCause(BaseModel):
    cause_code: CauseCode
    rank: int


class ResponsibleParty(BaseModel):
    party_type: PartyType
    party_id: str


class RootCauseAnalysis(BaseModel):
    ranked_causes: list[RankedCause] = Field(default_factory=list, max_length=3)
    responsible_parties: list[ResponsibleParty] = Field(default_factory=list, max_length=3)


class FinancialResolution(BaseModel):
    currency: Literal["BRL"] = "BRL"
    item_total_brl: float
    freight_total_brl: float
    payment_total_brl: float
    recommended_refund_brl: float

    @field_validator(
        "item_total_brl", "freight_total_brl", "payment_total_brl", "recommended_refund_brl"
    )
    @classmethod
    def _round_2dp(cls, v: float) -> float:
        return round(v, 2)


class CaseOutput(BaseModel):
    case_id: str
    assessment: Assessment
    affected_entities: AffectedEntities
    root_cause_analysis: RootCauseAnalysis
    evidence_ids: list[str] = Field(default_factory=list, max_length=10)
    financial_resolution: FinancialResolution
    resolution_actions: list[ResolutionAction] = Field(default_factory=list, max_length=5)
