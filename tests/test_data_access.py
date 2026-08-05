"""Test data_access.py - kiem tra load CSV va index dung, KHONG kiem tra logic nghiep vu."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_access import DataStore

# order_id that, lay tu input/EC_001.json (da xac nhan ton tai trong data/olist_orders_dataset.csv).
KNOWN_ORDER_ID = "e2a03ccf5ea816036608b2d8c3ab8e60"


def test_load_and_lookup_known_order():
    store = DataStore.instance()
    order = store.get_order(KNOWN_ORDER_ID)
    assert order is not None
    assert order["order_id"] == KNOWN_ORDER_ID


def test_unknown_order_returns_none():
    store = DataStore.instance()
    assert store.get_order("khong-ton-tai-000") is None


def test_items_and_payments_return_lists():
    store = DataStore.instance()
    assert isinstance(store.get_items(KNOWN_ORDER_ID), list)
    assert isinstance(store.get_payments(KNOWN_ORDER_ID), list)


def test_unknown_order_has_empty_items_and_payments():
    store = DataStore.instance()
    assert store.get_items("khong-ton-tai-000") == []
    assert store.get_payments("khong-ton-tai-000") == []
