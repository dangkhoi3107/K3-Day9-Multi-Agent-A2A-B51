"""Tien ich dung chung: quet data/*.csv de tim order_id THAT lam fixture cho unit test cua
tung vai tro (thay cho cac REPLACE_ME trong tests/). Chay: python scripts/find_test_fixtures.py

Uu tien order_id nam trong chinh 50 case that (input/) khi co the, de fixture "gan" voi du
lieu se cham diem. Neu khong tim thay trong 50 case, roi xuong toan bo dataset Olist.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from src.config import DATA_DIR, INPUT_DIR


def _real_claimed_order_ids() -> set[str]:
    ids = set()
    for p in INPUT_DIR.glob("EC_*.json"):
        ids.add(json.loads(p.read_text(encoding="utf-8"))["customer_request"]["claimed_order_id"])
    return ids


def _prefer_in_50(df: pd.DataFrame, order_id_col: str, real_ids: set[str]) -> tuple[pd.Series, bool]:
    in_50 = df[df[order_id_col].isin(real_ids)]
    if len(in_50):
        return in_50.iloc[0], True
    return df.iloc[0], False


def main() -> None:
    real_ids = _real_claimed_order_ids()
    print(f"({len(real_ids)} claimed_order_id thuc su trong input/)\n")

    orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv", dtype=str)
    for col in ["order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv", dtype=str)
    items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"], errors="coerce")

    payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv", dtype=str)
    payments["payment_value"] = payments["payment_value"].astype(float)

    # --- Vai tro 1: seller ban giao muon / dung han, order khong co item ---
    merged = items.merge(orders[["order_id", "order_delivered_carrier_date"]], on="order_id", how="left")
    merged = merged.dropna(subset=["order_delivered_carrier_date", "shipping_limit_date"])
    late = merged[merged["order_delivered_carrier_date"] > merged["shipping_limit_date"]]
    on_time = merged[merged["order_delivered_carrier_date"] <= merged["shipping_limit_date"]]
    row, in50 = _prefer_in_50(late, "order_id", real_ids)
    print(f"[Vai tro 1] seller tre han{' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']} seller_id={row['seller_id']}")
    row, in50 = _prefer_in_50(on_time, "order_id", real_ids)
    print(f"[Vai tro 1] seller dung han{' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']}")

    orders_with_items = set(items["order_id"].unique())
    no_item = orders[~orders["order_id"].isin(orders_with_items)]
    row, in50 = _prefer_in_50(no_item, "order_id", real_ids)
    print(f"[Vai tro 1] order khong co item row{' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']} status={row['order_status']}")

    # --- Vai tro 2: payment 1 dong / nhieu dong ---
    pay_counts = payments.groupby("order_id").size()
    single = pay_counts[pay_counts == 1].index
    multi = pay_counts[pay_counts >= 2].index
    row_id = next((oid for oid in multi if oid in real_ids), multi[0])
    print(f"\n[Vai tro 2] order co >=2 dong payment{' (trong 50 case that)' if row_id in real_ids else ''}: order_id={row_id}")
    row_id = next((oid for oid in single if oid in real_ids), single[0])
    print(f"[Vai tro 2] order co dung 1 dong payment{' (trong 50 case that)' if row_id in real_ids else ''}: order_id={row_id}")

    # --- Vai tro 3: giao dung han / tre han / chua giao ---
    d = orders.dropna(subset=["order_estimated_delivery_date"]).copy()
    delivered_late = d[d["order_delivered_customer_date"] > d["order_estimated_delivery_date"]]
    delivered_on_time = d[
        d["order_delivered_customer_date"].notna() & (d["order_delivered_customer_date"] <= d["order_estimated_delivery_date"])
    ]
    not_delivered = orders[orders["order_delivered_customer_date"].isna()]
    row, in50 = _prefer_in_50(delivered_late, "order_id", real_ids)
    print(f"\n[Vai tro 3] giao tre han{' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']}")
    row, in50 = _prefer_in_50(delivered_on_time, "order_id", real_ids)
    print(f"[Vai tro 3] giao dung han{' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']}")
    row, in50 = _prefer_in_50(not_delivered, "order_id", real_ids)
    print(f"[Vai tro 3] chua giao (customer_date rong){' (trong 50 case that)' if in50 else ''}: order_id={row['order_id']} status={row['order_status']}")


if __name__ == "__main__":
    main()
