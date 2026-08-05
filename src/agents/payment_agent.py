"""Vai tro 2: Payment Agent.
Doi soat payment voi item+freight tu Order&Seller Agent. README muc 4 dong 5 (valid_split_payment)
noi ro cong thuc nen phan lon da implement san - trao doi voi Vai tro 4 truoc khi doi dung sai.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.config import SPLIT_PAYMENT_TOLERANCE_BRL
from src.data_access import DataStore
from src.evidence import evidence_payment


@dataclass
class PaymentFacts:
    order_id: str
    payments: list[dict]       # moi dong: payment_sequential, payment_type, payment_installments, payment_value
    payment_total_brl: float
    is_split: bool              # >= 2 dong payment
    is_reconciled: bool         # |payment_total - (item_total+freight_total)| <= dung sai
    evidence_ids: list[str] = field(default_factory=list)


def investigate(order_id: str, item_total_brl: float, freight_total_brl: float) -> PaymentFacts:
    store = DataStore.instance()
    payments = store.get_payments(order_id)

    payment_total = round(sum(p["payment_value"] for p in payments), 2)
    is_split = len(payments) >= 2

    # README muc 4: "tong payment khop tong item + freight trong sai so 0.10 BRL" (rule 5).
    # TODO (Vai tro 2, xac nhan voi Vai tro 4): dung sai nay co ap dung nguyen ven cho ca
    # rule 6 ("payment khop") khong - xem SPLIT_PAYMENT_TOLERANCE_BRL trong src/config.py.
    is_reconciled = abs(payment_total - (item_total_brl + freight_total_brl)) <= SPLIT_PAYMENT_TOLERANCE_BRL

    evidence_ids = [evidence_payment(order_id, p["payment_sequential"]) for p in payments]

    return PaymentFacts(
        order_id=order_id,
        payments=payments,
        payment_total_brl=payment_total,
        is_split=is_split,
        is_reconciled=is_reconciled,
        evidence_ids=evidence_ids,
    )
