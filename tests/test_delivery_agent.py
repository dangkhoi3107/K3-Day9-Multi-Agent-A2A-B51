"""Test delivery_agent.py tren cac order co trong bo 50 case that."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.delivery_agent import investigate

KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"  # tu input/EC_001.json
NOT_DELIVERED_ORDER_ID = "71303d7e93b399f5bcd537d124c0bcfa"  # input/EC_003.json
ON_TIME_ORDER_ID = "8067c5e4834f3c0a3c8a4e921d65c5b1"  # input/EC_002.json
LATE_ORDER_ID = KNOWN_ORDER_ID


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
    facts = investigate(NOT_DELIVERED_ORDER_ID)
    assert facts.delivered is False
    assert facts.late_to_customer is None


def test_delivered_on_time():
    facts = investigate(ON_TIME_ORDER_ID)
    assert facts.delivered is True
    assert facts.late_to_customer is False


def test_delivered_late():
    facts = investigate(LATE_ORDER_ID)
    assert facts.delivered is True
    assert facts.late_to_customer is True
