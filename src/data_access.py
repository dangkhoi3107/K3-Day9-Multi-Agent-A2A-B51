"""Nap du lieu Olist tu data/*.csv MOT LAN, index san theo order_id/seller_id de moi agent
tra cuu O(1). Day la ha tang dung chung cho Vai tro 1/2/3 - KHONG tu mo lai CSV o noi khac,
de tranh moi nguoi doc/parse ngay thang khac nhau roi ra so lieu vet nhau.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_DIR

_ORDER_DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


class DataStore:
    """Singleton - goi DataStore.instance() de dung, khong tu new() truc tiep (tranh nap CSV nhieu lan)."""

    _instance: Optional["DataStore"] = None

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        orders = pd.read_csv(data_dir / "olist_orders_dataset.csv", dtype=str)
        for col in _ORDER_DATE_COLS:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")
        self._orders = orders.set_index("order_id", drop=False)

        items = pd.read_csv(data_dir / "olist_order_items_dataset.csv", dtype=str)
        items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"], errors="coerce")
        items["price"] = items["price"].astype(float)
        items["freight_value"] = items["freight_value"].astype(float)
        items["order_item_id"] = items["order_item_id"].astype(int)
        self._items_by_order: dict[str, list[dict]] = {
            order_id: grp.to_dict("records") for order_id, grp in items.groupby("order_id")
        }

        payments = pd.read_csv(data_dir / "olist_order_payments_dataset.csv", dtype=str)
        payments["payment_value"] = payments["payment_value"].astype(float)
        payments["payment_sequential"] = payments["payment_sequential"].astype(int)
        payments["payment_installments"] = payments["payment_installments"].astype(int)
        self._payments_by_order: dict[str, list[dict]] = {
            order_id: grp.sort_values("payment_sequential").to_dict("records")
            for order_id, grp in payments.groupby("order_id")
        }

        sellers = pd.read_csv(data_dir / "olist_sellers_dataset.csv", dtype=str)
        self._sellers = sellers.set_index("seller_id", drop=False)

    @classmethod
    def instance(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Chi dung trong test khi can nap lai tu 1 data_dir khac."""
        cls._instance = None

    def get_order(self, order_id: str) -> Optional[dict]:
        """Tra ve 1 dict (cac cot ngay la pd.Timestamp hoac pd.NaT - luon pd.notna(...) truoc khi so sanh)."""
        if order_id not in self._orders.index:
            return None
        return self._orders.loc[order_id].to_dict()

    def get_items(self, order_id: str) -> list[dict]:
        """Tra ve list rong neu order khong co item row nao (README muc 6)."""
        return list(self._items_by_order.get(order_id, []))

    def get_payments(self, order_id: str) -> list[dict]:
        return list(self._payments_by_order.get(order_id, []))

    def get_seller(self, seller_id: str) -> Optional[dict]:
        if seller_id not in self._sellers.index:
            return None
        return self._sellers.loc[seller_id].to_dict()
