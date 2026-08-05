"""Xay va kiem tra chuoi evidence ID theo dung 5 dang trong README muc 5.
Dung DUY NHAT cac ham nay de tao evidence_id o moi agent - khong tu ghep chuoi f"..." rai rac
o nhieu noi, de tranh sai dinh dang (1 nguyen nhan hard-gate).
"""
from __future__ import annotations

import re

_PATTERNS: dict[str, re.Pattern[str]] = {
    "order": re.compile(r"^order:(?P<order_id>[^:]+)$"),
    "item": re.compile(r"^item:(?P<order_id>[^:]+):(?P<item_id>\d+)$"),
    "payment": re.compile(r"^payment:(?P<order_id>[^:]+):(?P<seq>\d+)$"),
    "seller": re.compile(r"^seller:(?P<seller_id>[^:]+)$"),
    "policy": re.compile(r"^policy:(?P<cause_code>[A-Z_]+)$"),
}


def evidence_order(order_id: str) -> str:
    return f"order:{order_id}"


def evidence_item(order_id: str, order_item_id: int | str) -> str:
    return f"item:{order_id}:{order_item_id}"


def evidence_payment(order_id: str, payment_sequential: int | str) -> str:
    return f"payment:{order_id}:{payment_sequential}"


def evidence_seller(seller_id: str) -> str:
    return f"seller:{seller_id}"


def evidence_policy(cause_code: str) -> str:
    return f"policy:{cause_code}"


def parse_evidence_id(evidence_id: str) -> tuple[str, dict[str, str]] | None:
    """Tra ve (kind, groups) neu evidence_id dung 1 trong 5 dinh dang, None neu sai."""
    for kind, pattern in _PATTERNS.items():
        m = pattern.match(evidence_id)
        if m:
            return kind, m.groupdict()
    return None
