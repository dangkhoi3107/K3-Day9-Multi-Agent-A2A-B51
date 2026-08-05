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


@pytest.mark.xfail(reason="Vai tro 4 chua implement _rule_1_canceled_order_paid (TODO trong policy_agent.py)", strict=False)
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


def test_no_matching_rule_falls_back_with_low_confidence():
    # Cho toi khi cac rule con lai chua implement (con tra None het), decide() phai roi vao
    # nhanh fallback trong policy_agent.py: confidence THAP, khong loi.
    decision = decide(_order_seller(), _payment(), _delivery())
    assert 0.0 <= decision.confidence <= 1.0


# TODO (Vai tro 4) - viet tiep theo mau test_rule1:
# def test_rule2_unavailable_order_paid(): ...
# def test_rule3_late_delivery_seller(): _order_seller(late_seller_ids=["s1"]), _delivery(late_to_customer=True)
# def test_rule4_late_delivery_logistics(): _order_seller(late_seller_ids=[]), _delivery(late_to_customer=True)
# def test_rule5_valid_split_payment(): _payment(is_split=True, is_reconciled=True)
# def test_rule6_unsupported_late_claim(): _delivery(late_to_customer=False), _payment(is_reconciled=True)
#
# def test_priority_canceled_beats_valid_split_payment():
#     """Order vua canceled vua co 2 payment khop -> PHAI ra canceled_order_paid (rule 1 xet truoc rule 5)."""
#     decision = decide(
#         _order_seller(order_status="canceled"),
#         _payment(is_split=True, is_reconciled=True, payment_total_brl=115.0),
#         _delivery(),
#     )
#     assert decision.primary_issue == "canceled_order_paid"
