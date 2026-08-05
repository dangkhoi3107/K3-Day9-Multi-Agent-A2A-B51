"""Hang so dung chung: duong dan, gioi han field theo README muc 6, model LLM."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"
LOGGING_DIR = ROOT_DIR / "logging"
TRACE_PATH = LOGGING_DIR / "trace.jsonl"
METADATA_PATH = LOGGING_DIR / "metadata.json"

POLICY_VERSION = "EC_POLICY_V1"

# README muc 4: "tong payment khop tong item + freight trong sai so 0.10 BRL" (rule 5 - valid_split_payment).
SPLIT_PAYMENT_TOLERANCE_BRL = 0.10

# TODO (Vai tro 4, thong nhat voi Vai tro 2): rule 6 (unsupported_late_claim, "payment khop")
# KHONG duoc README nhac lai dung sai ro rang. Quyet dinh dung lai 0.10 BRL cho nhat quan hay
# gia tri khac - ghi ro ly do vao architecture.md muc 6.
UNSUPPORTED_CLAIM_TOLERANCE_BRL = 0.10

# Gioi han output theo README muc 6.
MAX_ENTITY_IDS = 5
MAX_EVIDENCE_IDS = 10
MAX_RANKED_CAUSES = 3
MAX_RESPONSIBLE_PARTIES = 3
MAX_RESOLUTION_ACTIONS = 5

# Model <=10B tham so (bat buoc - README muc 9.1). Doc tu .env, KHONG hardcode key.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
