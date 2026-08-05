"""Test order_seller_agent.py. Cac order_id fixture ben duoi la du lieu THAT, tim bang
cach quet data/olist_orders_dataset.csv join data/olist_order_items_dataset.csv (xem
scripts/find_role1_fixtures.py neu can tim them fixture khac)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.order_seller_agent import investigate

KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"  # tu input/EC_001.json

# Nam trong chinh 50 case that (input/): carrier nhan hang 2017-08-30 17:35:05, sau
# shipping_limit_date 2017-08-25 00:55:05 cua item -> seller nay phai bi tinh la ban giao muon.
LATE_SELLER_ORDER_ID = "1f7565efbb90c33b80f467d6a75332c5"
LATE_SELLER_ID = "02d35243ea2e497335cd0f076b45675d"

# carrier nhan hang khong muon hon shipping_limit_date -> khong seller nao bi tinh la tre.
ON_TIME_ORDER_ID = "103de323ece563a1012b4b6adf5a81b2"

# nam trong chinh 50 case that: co that trong orders.csv nhung khong co dong nao trong
# order_items.csv (status=unavailable).
NO_ITEM_ORDER_ID = "2636a02ee7de9590df86a4c24b739c49"


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
    """README muc 6: order khong co item row -> item_ids/seller_ids rong, 2 tong tien = 0.0."""
    facts = investigate(NO_ITEM_ORDER_ID)
    assert facts.order_found is True
    assert facts.items == []
    assert facts.late_seller_ids == []
    assert facts.item_total_brl == 0.0
    assert facts.freight_total_brl == 0.0


def test_seller_late_when_carrier_after_shipping_limit():
    """README muc 4 (SELLER_HANDOFF_AFTER_LIMIT): carrier nhan hang SAU shipping_limit_date
    cua item -> seller cua item do phai co mat trong late_seller_ids + co evidence seller:<id>."""
    facts = investigate(LATE_SELLER_ORDER_ID)
    assert facts.order_found is True
    assert LATE_SELLER_ID in facts.late_seller_ids
    assert f"seller:{LATE_SELLER_ID}" in facts.evidence_ids


def test_seller_on_time_is_not_flagged_late():
    """Doi chung voi test tren: carrier nhan hang dung han -> khong seller nao bi tinh la tre."""
    facts = investigate(ON_TIME_ORDER_ID)
    assert facts.order_found is True
    assert facts.late_seller_ids == []
