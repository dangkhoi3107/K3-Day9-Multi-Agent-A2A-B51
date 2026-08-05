"""Test order_seller_agent.py.
TODO (Vai tro 1): thay REPLACE_ME bang order_id that (loc data/olist_orders_dataset.csv join
data/olist_order_items_dataset.csv) cho tung tinh huong: seller ban giao dung han, seller ban
giao tre han, nhieu item cung 1 seller. order_id da biet la co that: xem KNOWN_ORDER_ID.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.order_seller_agent import investigate

KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"  # tu input/EC_001.json


def test_order_not_found_returns_empty_facts():
    facts = investigate("khong-ton-tai-000")
    assert facts.order_found is False
    assert facts.items == []
    assert facts.late_seller_ids == []
    assert facts.item_total_brl == 0.0
    assert facts.freight_total_brl == 0.0


def test_known_order_found_and_totals_non_negative():
    facts = investigate(KNOWN_ORDER_ID)
    assert facts.order_found is True
    assert facts.item_total_brl >= 0.0
    assert facts.freight_total_brl >= 0.0
    assert f"order:{KNOWN_ORDER_ID}" in facts.evidence_ids


def test_order_without_item_rows_has_empty_lists():
    # TODO: tim 1 order_id thuc su khong co dong nao trong order_items.csv (neu co trong 50
    # case that), hoac bo qua test nay neu khong phat sinh (README muc 6 chi noi ro phai
    # XU LY dung khi no xay ra, khong bat buoc phai co trong 50 case).
    order_id = "REPLACE_ME"
    facts = investigate(order_id)
    if facts.order_found and not facts.items:
        assert facts.late_seller_ids == []
        assert facts.item_total_brl == 0.0
        assert facts.freight_total_brl == 0.0


# TODO (Vai tro 1): them test_seller_late_when_carrier_after_shipping_limit() sau khi da
# implement phan so sanh trong order_seller_agent.py (hien dang comment out).
