"""Test delivery_agent.py.
TODO (Vai tro 3): thay REPLACE_ME bang order_id that cho tung tinh huong: giao dung han,
giao tre han, chua giao (order_delivered_customer_date rong trong orders.csv).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.delivery_agent import investigate

KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"  # tu input/EC_001.json


def test_unknown_order_not_delivered_no_verdict():
    facts = investigate("khong-ton-tai-000")
    assert facts.delivered is False
    assert facts.late_to_customer is None


def test_known_order_returns_evidence():
    facts = investigate(KNOWN_ORDER_ID)
    assert f"order:{KNOWN_ORDER_ID}" in facts.evidence_ids


def test_not_delivered_never_has_late_verdict():
    # Bat bien quan trong: don chua giao KHONG DUOC ket luan dung/tre han (README: chi suy
    # dien tu du lieu that, khong tu bia).
    order_id = "REPLACE_ME"  # TODO: order_id co order_delivered_customer_date rong
    facts = investigate(order_id)
    if not facts.delivered:
        assert facts.late_to_customer is None


# TODO (Vai tro 3):
# def test_delivered_on_time(): order_id = "REPLACE_ME"; assert late_to_customer is False
# def test_delivered_late(): order_id = "REPLACE_ME"; assert late_to_customer is True
