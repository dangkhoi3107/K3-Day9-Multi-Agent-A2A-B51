"""Vai tro 1: Order & Seller Agent.
Kiem tra order_status, item, seller va moc ban giao seller->carrier.
Doc README muc 4 (dong 3 "late_delivery_seller") va muc 6 (schema) truoc khi sua.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.data_access import DataStore
from src.evidence import evidence_item, evidence_order, evidence_seller


@dataclass
class OrderSellerFacts:
    order_id: str
    order_found: bool
    order_status: str | None
    items: list[dict]              # moi item: order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
    late_seller_ids: list[str]     # seller_id nao ban giao cho carrier SAU shipping_limit_date cua chinh item do
    item_total_brl: float
    freight_total_brl: float
    evidence_ids: list[str] = field(default_factory=list)


def investigate(order_id: str) -> OrderSellerFacts:
    store = DataStore.instance()
    order = store.get_order(order_id)
    items = store.get_items(order_id)

    if order is None:
        return OrderSellerFacts(
            order_id=order_id,
            order_found=False,
            order_status=None,
            items=[],
            late_seller_ids=[],
            item_total_brl=0.0,
            freight_total_brl=0.0,
            evidence_ids=[],
        )

    late_seller_ids: list[str] = []

    # README muc 4: seller bi coi la ban giao muon neu order_delivered_carrier_date (1 gia tri
    # DUY NHAT cho ca don) SAU shipping_limit_date CUA TUNG ITEM. pd.notna(...) bat buoc truoc
    # khi so sanh - don chua giao / bi canceled co carrier_date rong (NaT), va NaT > x / NaT <= x
    # deu tra False trong pandas nen neu khong kiem truoc se am tham "khong ai tre" du that ra
    # la "chua biet".
    carrier_date = order["order_delivered_carrier_date"]
    if pd.notna(carrier_date):
        for it in items:
            if pd.notna(it["shipping_limit_date"]) and carrier_date > it["shipping_limit_date"]:
                late_seller_ids.append(it["seller_id"])

    evidence_ids = [evidence_order(order_id)]
    for it in items:
        evidence_ids.append(evidence_item(order_id, it["order_item_id"]))
    for seller_id in dict.fromkeys(late_seller_ids):  # unique, giu thu tu xuat hien
        evidence_ids.append(evidence_seller(seller_id))

    item_total = round(sum(it["price"] for it in items), 2)
    freight_total = round(sum(it["freight_value"] for it in items), 2)

    return OrderSellerFacts(
        order_id=order_id,
        order_found=True,
        order_status=order["order_status"],
        items=items,
        late_seller_ids=late_seller_ids,
        item_total_brl=item_total,
        freight_total_brl=freight_total,
        evidence_ids=evidence_ids,
    )
