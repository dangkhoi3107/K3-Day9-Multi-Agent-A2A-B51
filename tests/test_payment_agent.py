"""Test payment_agent.py.
TODO (Vai tro 2): thay REPLACE_ME bang order_id that cho tung tinh huong (1 dong payment,
2 dong khop, 2 dong lech) - loc data/olist_order_payments_dataset.csv theo so dong/order_id.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.order_seller_agent import investigate as investigate_order_seller
from src.agents.payment_agent import investigate

KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"  # tu input/EC_001.json


def test_unknown_order_has_zero_payment_total():
    facts = investigate("khong-ton-tai-000", item_total_brl=0.0, freight_total_brl=0.0)
    assert facts.payments == []
    assert facts.payment_total_brl == 0.0
    assert facts.is_split is False


def test_known_order_payment_total_matches_sum_of_rows():
    os_facts = investigate_order_seller(KNOWN_ORDER_ID)
    pay_facts = investigate(KNOWN_ORDER_ID, os_facts.item_total_brl, os_facts.freight_total_brl)
    assert pay_facts.payment_total_brl == round(sum(p["payment_value"] for p in pay_facts.payments), 2)
    assert pay_facts.is_split == (len(pay_facts.payments) >= 2)


def test_two_reconciled_payments_is_valid_split():
    order_id = "0016dfedd97fc2950e388d2971d718c7"
    os_facts = investigate_order_seller(order_id)
    pay_facts = investigate(order_id, os_facts.item_total_brl, os_facts.freight_total_brl)

    assert len(pay_facts.payments) == 2
    assert pay_facts.is_split is True
    assert pay_facts.payment_total_brl == 70.55
    assert round(os_facts.item_total_brl + os_facts.freight_total_brl, 2) == 70.55
    assert pay_facts.is_reconciled is True


def test_two_mismatched_payments_is_not_reconciled():
    order_id = "b38b3526b8b8fdc807e8a0a42ab78573"
    os_facts = investigate_order_seller(order_id)
    pay_facts = investigate(order_id, os_facts.item_total_brl, os_facts.freight_total_brl)

    assert len(pay_facts.payments) == 2
    assert pay_facts.is_split is True
    assert pay_facts.payment_total_brl == 30.19
    assert round(os_facts.item_total_brl + os_facts.freight_total_brl, 2) == 30.06
    assert pay_facts.is_reconciled is False
