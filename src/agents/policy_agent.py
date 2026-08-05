"""Vai tro 4: Policy Agent - ap dung EC_POLICY_V1 (README muc 4).
QUAN TRONG: 6 rule duoi day PHAI duoc xet dung THU TU uu tien nhu README. Rule dau tien
khop la thang, dung() dung lai ngay - KHONG xet tiep rule sau (vi du: order vua canceled
vua co 2 payment khop van phai ra canceled_order_paid, khong phai valid_split_payment).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.agents.delivery_agent import DeliveryFacts
from src.agents.order_seller_agent import OrderSellerFacts
from src.agents.payment_agent import PaymentFacts
from src.evidence import evidence_policy


@dataclass
class PolicyDecision:
    primary_issue: str
    case_status: str                    # "action_required" | "no_action"
    cause_code: str
    responsible_party_type: str | None  # "platform" | "seller" | "logistics_provider" | None
    responsible_party_id: str | None
    recommended_refund_brl: float
    resolution_action: str
    confidence: float
    evidence_ids: list[str]


def decide(order_seller: OrderSellerFacts, payment: PaymentFacts, delivery: DeliveryFacts) -> PolicyDecision:
    """Xet 6 rule theo dung thu tu README muc 4. Moi _rule_N tra PolicyDecision neu khop,
    None neu khong khop - decide() dung ngay o rule dau tien khop."""
    for rule_fn in (
        _rule_1_canceled_order_paid,
        _rule_2_unavailable_order_paid,
        _rule_3_late_delivery_seller,
        _rule_4_late_delivery_logistics,
        _rule_5_valid_split_payment,
        _rule_6_unsupported_late_claim,
    ):
        decision = rule_fn(order_seller, payment, delivery)
        if decision is not None:
            return decision

    # TODO (Vai tro 4): README dam bao 50 case chinh thuc "khong co tinh huong mo ho", nen
    # nhanh nay ly thuyet khong nen bi cham toi. Van giu lai de an toan khi test tren du lieu
    # ngoai 50 case - confidence THAP, khong bia evidence gi ngoai policy:<cause_code> mac dinh.
    return PolicyDecision(
        primary_issue="unsupported_late_claim",
        case_status="no_action",
        cause_code="DELIVERY_WITHIN_ESTIMATE",
        responsible_party_type=None,
        responsible_party_id=None,
        recommended_refund_brl=0.0,
        resolution_action="reject_late_refund",
        confidence=0.1,
        evidence_ids=[evidence_policy("DELIVERY_WITHIN_ESTIMATE")],
    )


def _rule_1_canceled_order_paid(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """order_status = canceled & tong payment > 0 -> platform/OLIST_PLATFORM, refund = tong
    payment, action = issue_full_refund, cause = ORDER_CANCELED_AFTER_PAYMENT."""
    if os_.order_status == "canceled" and pay.payment_total_brl > 0:
        return PolicyDecision(
            primary_issue="canceled_order_paid",
            case_status="action_required",
            cause_code="ORDER_CANCELED_AFTER_PAYMENT",
            responsible_party_type="platform",
            responsible_party_id="OLIST_PLATFORM",
            recommended_refund_brl=round(pay.payment_total_brl, 2),
            resolution_action="issue_full_refund",
            confidence=0.95,
            evidence_ids=[evidence_policy("ORDER_CANCELED_AFTER_PAYMENT")],
        )
    return None


def _rule_2_unavailable_order_paid(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """order_status = unavailable & tong payment > 0 -> platform/OLIST_PLATFORM, refund = tong
    payment, action = issue_full_refund, cause = ORDER_UNAVAILABLE_AFTER_PAYMENT."""
    if os_.order_status == "unavailable" and pay.payment_total_brl > 0:
        return PolicyDecision(
            primary_issue="unavailable_order_paid",
            case_status="action_required",
            cause_code="ORDER_UNAVAILABLE_AFTER_PAYMENT",
            responsible_party_type="platform",
            responsible_party_id="OLIST_PLATFORM",
            recommended_refund_brl=round(pay.payment_total_brl, 2),
            resolution_action="issue_full_refund",
            confidence=0.95,
            evidence_ids=[evidence_policy("ORDER_UNAVAILABLE_AFTER_PAYMENT")],
        )
    return None


def _rule_3_late_delivery_seller(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """giao sau estimated date (deliv.late_to_customer is True) & co seller ban giao muon
    (os_.late_seller_ids khong rong) -> seller/<seller_id>, refund = tong freight,
    action = refund_freight, cause = SELLER_HANDOFF_AFTER_LIMIT."""
    if deliv.late_to_customer is True and len(os_.late_seller_ids) > 0:
        return PolicyDecision(
            primary_issue="late_delivery_seller",
            case_status="action_required",
            cause_code="SELLER_HANDOFF_AFTER_LIMIT",
            responsible_party_type="seller",
            responsible_party_id=os_.late_seller_ids[0],
            recommended_refund_brl=round(os_.freight_total_brl, 2),
            resolution_action="refund_freight",
            confidence=0.95,
            evidence_ids=[evidence_policy("SELLER_HANDOFF_AFTER_LIMIT")],
        )
    return None


def _rule_4_late_delivery_logistics(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """giao sau estimated date & KHONG co seller nao ban giao muon -> logistics_provider/
    LOGISTICS_PROVIDER, refund = tong freight, action = refund_freight,
    cause = CARRIER_DELIVERED_AFTER_ESTIMATE."""
    if deliv.late_to_customer is True and len(os_.late_seller_ids) == 0:
        return PolicyDecision(
            primary_issue="late_delivery_logistics",
            case_status="action_required",
            cause_code="CARRIER_DELIVERED_AFTER_ESTIMATE",
            responsible_party_type="logistics_provider",
            responsible_party_id="LOGISTICS_PROVIDER",
            recommended_refund_brl=round(os_.freight_total_brl, 2),
            resolution_action="refund_freight",
            confidence=0.95,
            evidence_ids=[evidence_policy("CARRIER_DELIVERED_AFTER_ESTIMATE")],
        )
    return None


def _rule_5_valid_split_payment(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """pay.is_split & pay.is_reconciled -> khong ai chiu trach nhiem, refund = 0,
    action = explain_valid_split_payment, cause = MULTIPLE_PAYMENTS_RECONCILED."""
    if pay.is_split is True and pay.is_reconciled is True:
        return PolicyDecision(
            primary_issue="valid_split_payment",
            case_status="no_action",
            cause_code="MULTIPLE_PAYMENTS_RECONCILED",
            responsible_party_type=None,
            responsible_party_id=None,
            recommended_refund_brl=0.0,
            resolution_action="explain_valid_split_payment",
            confidence=0.95,
            evidence_ids=[evidence_policy("MULTIPLE_PAYMENTS_RECONCILED")],
        )
    return None


def _rule_6_unsupported_late_claim(
    os_: OrderSellerFacts, pay: PaymentFacts, deliv: DeliveryFacts
) -> PolicyDecision | None:
    """giao khong muon hon estimated date (deliv.late_to_customer is False) & payment khop
    (pay.is_reconciled) -> khong ai chiu trach nhiem, refund = 0, action = reject_late_refund,
    cause = DELIVERY_WITHIN_ESTIMATE."""
    if deliv.late_to_customer is False and pay.is_reconciled is True:
        return PolicyDecision(
            primary_issue="unsupported_late_claim",
            case_status="no_action",
            cause_code="DELIVERY_WITHIN_ESTIMATE",
            responsible_party_type=None,
            responsible_party_id=None,
            recommended_refund_brl=0.0,
            resolution_action="reject_late_refund",
            confidence=0.95,
            evidence_ids=[evidence_policy("DELIVERY_WITHIN_ESTIMATE")],
        )
    return None
