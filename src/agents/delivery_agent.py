"""Vai tro 3: Delivery Agent.
So sanh thoi diem giao thuc te (order_delivered_customer_date) voi han giao (order_estimated_delivery_date).
KHONG tu ket luan seller hay logistics chiu trach nhiem - chi neu su kien "co tre voi khach hang
khong". Policy Agent moi ghep fact nay voi late_seller_ids tu Order&Seller Agent de ra primary_issue.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.data_access import DataStore
from src.evidence import evidence_order


@dataclass
class DeliveryFacts:
    order_id: str
    delivered: bool                    # order_delivered_customer_date co gia tri (khong phai NaT)
    late_to_customer: bool | None      # None neu chua giao - khong danh gia duoc "dung/tre han"
    delivered_carrier_date: Any        # pd.Timestamp hoac NaT - de Order&Seller/Policy doi chieu shipping_limit_date
    evidence_ids: list[str] = field(default_factory=list)


def investigate(order_id: str) -> DeliveryFacts:
    store = DataStore.instance()
    order = store.get_order(order_id)

    if order is None:
        return DeliveryFacts(
            order_id=order_id,
            delivered=False,
            late_to_customer=None,
            delivered_carrier_date=None,
            evidence_ids=[],
        )

    delivered_customer_date = order["order_delivered_customer_date"]
    estimated_date = order["order_estimated_delivery_date"]
    delivered = bool(pd.notna(delivered_customer_date))

    late_to_customer: bool | None = None
    # TODO (Vai tro 3): neu da giao (delivered=True) VA estimated_date co gia tri, so sanh
    # delivered_customer_date voi estimated_date -> late_to_customer = True/False.
    # Neu chua giao (delivered=False), GIU NGUYEN None - khong suy dien "dung han" tu gia tri rong.
    #
    # if delivered and pd.notna(estimated_date):
    #     late_to_customer = bool(delivered_customer_date > estimated_date)

    return DeliveryFacts(
        order_id=order_id,
        delivered=delivered,
        late_to_customer=late_to_customer,
        delivered_carrier_date=order["order_delivered_carrier_date"],
        evidence_ids=[evidence_order(order_id)],
    )
