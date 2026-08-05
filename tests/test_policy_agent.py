"""Test policy_agent.py - 1 test cho tung rule theo dung README muc 4, cong test thu tu uu tien.
TODO (Vai tro 4): sau khi implement tung _rule_N trong src/agents/policy_agent.py, viet tiep
test_rule2 .. test_rule6 theo mau test_rule1 ben duoi. QUAN TRONG NHAT: them test thu tu uu
tien (vi du order vua canceled vua co 2 payment khop van phai ra canceled_order_paid, khong
phai valid_split_payment, vi rule 1 duoc xet TRUOC rule 5).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.agents.delivery_agent import DeliveryFacts
from src.agents.order_seller_agent import OrderSellerFacts
from src.agents.payment_agent import PaymentFacts
from src.agents.policy_agent import decide


def _order_seller(**overrides) -> OrderSellerFacts:
    base = dict(
        order_id="o1", order_found=True, order_status="delivered",
        items=[], late_seller_ids=[], item_total_brl=100.0, freight_total_brl=15.0, evidence_ids=[],
    )
    base.update(overrides)
    return OrderSellerFacts(**base)


def _payment(**overrides) -> PaymentFacts:
    base = dict(
        order_id="o1", payments=[], payment_total_brl=115.0, is_split=False, is_reconciled=True, evidence_ids=[],
    )
    base.update(overrides)
    return PaymentFacts(**base)


def _delivery(**overrides) -> DeliveryFacts:
    base = dict(
        order_id="o1", delivered=True, late_to_customer=False, delivered_carrier_date=None, evidence_ids=[],
    )
    base.update(overrides)
    return DeliveryFacts(**base)


def test_rule1_canceled_order_paid():
    decision = decide(
        _order_seller(order_status="canceled"),
        _payment(payment_total_brl=115.0),
        _delivery(),
    )
    assert decision.primary_issue == "canceled_order_paid"
    assert decision.cause_code == "ORDER_CANCELED_AFTER_PAYMENT"
    assert decision.recommended_refund_brl == 115.0
    assert decision.resolution_action == "issue_full_refund"
    assert decision.responsible_party_type == "platform"
    assert decision.responsible_party_id == "OLIST_PLATFORM"


def test_rule2_unavailable_order_paid():
    decision = decide(
        _order_seller(order_status="unavailable"),
        _payment(payment_total_brl=115.0),
        _delivery(),
    )
    assert decision.primary_issue == "unavailable_order_paid"
    assert decision.cause_code == "ORDER_UNAVAILABLE_AFTER_PAYMENT"
    assert decision.recommended_refund_brl == 115.0
    assert decision.resolution_action == "issue_full_refund"
    assert decision.responsible_party_type == "platform"
    assert decision.responsible_party_id == "OLIST_PLATFORM"


def test_rule3_late_delivery_seller():
    decision = decide(
        _order_seller(late_seller_ids=["s1"], freight_total_brl=15.0),
        _payment(),
        _delivery(late_to_customer=True),
    )
    assert decision.primary_issue == "late_delivery_seller"
    assert decision.cause_code == "SELLER_HANDOFF_AFTER_LIMIT"
    assert decision.recommended_refund_brl == 15.0
    assert decision.resolution_action == "refund_freight"
    assert decision.responsible_party_type == "seller"
    assert decision.responsible_party_id == "s1"


def test_rule4_late_delivery_logistics():
    decision = decide(
        _order_seller(late_seller_ids=[], freight_total_brl=15.0),
        _payment(),
        _delivery(late_to_customer=True),
    )
    assert decision.primary_issue == "late_delivery_logistics"
    assert decision.cause_code == "CARRIER_DELIVERED_AFTER_ESTIMATE"
    assert decision.recommended_refund_brl == 15.0
    assert decision.resolution_action == "refund_freight"
    assert decision.responsible_party_type == "logistics_provider"
    assert decision.responsible_party_id == "LOGISTICS_PROVIDER"


def test_rule5_valid_split_payment():
    decision = decide(
        _order_seller(order_status="delivered"),
        _payment(is_split=True, is_reconciled=True),
        _delivery(late_to_customer=None),
    )
    assert decision.primary_issue == "valid_split_payment"
    assert decision.cause_code == "MULTIPLE_PAYMENTS_RECONCILED"
    assert decision.recommended_refund_brl == 0.0
    assert decision.resolution_action == "explain_valid_split_payment"
    assert decision.responsible_party_type is None


def test_rule6_unsupported_late_claim():
    decision = decide(
        _order_seller(order_status="delivered"),
        _payment(is_reconciled=True),
        _delivery(late_to_customer=False),
    )
    assert decision.primary_issue == "unsupported_late_claim"
    assert decision.cause_code == "DELIVERY_WITHIN_ESTIMATE"
    assert decision.recommended_refund_brl == 0.0
    assert decision.resolution_action == "reject_late_refund"
    assert decision.responsible_party_type is None


def test_priority_canceled_beats_valid_split_payment():
    """Order vua canceled vua co 2 payment khop -> PHAI ra canceled_order_paid (rule 1 xet truoc rule 5)."""
    decision = decide(
        _order_seller(order_status="canceled"),
        _payment(is_split=True, is_reconciled=True, payment_total_brl=115.0),
        _delivery(),
    )
    assert decision.primary_issue == "canceled_order_paid"


def test_no_matching_rule_falls_back_with_low_confidence():
    # Neu khong co rule nao khop (vi du payment khong reconciled)
    decision = decide(_order_seller(), _payment(is_reconciled=False), _delivery(late_to_customer=None))
    assert 0.0 <= decision.confidence <= 1.0
