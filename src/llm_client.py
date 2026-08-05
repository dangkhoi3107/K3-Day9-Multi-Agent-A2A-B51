"""Wrapper mong goi model <=10B tham so (Groq hoac Ollama - ca hai deu co API tuong thich OpenAI,
chi khac base_url/model trong .env). Loi provider (mat mang, het quota, chua cai package) KHONG
duoc lam sap pipeline chinh - luon fallback ve 1 chuoi bao loi thay vi raise.

QUAN TRONG (xem architecture.md muc 1): output cua narrate() chi de ghi vao logging/trace.jsonl
lam ly do/tuong thuat. KHONG dung ket qua nay lam evidence_id, ID, hay so tien trong output cuoi -
nhung field do phai luon lay tu code tat dinh (data_access + policy_agent).
"""
from __future__ import annotations

from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI  # import tre - script khong dung LLM van chay duoc neu chua cai package

        _client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY or "ollama")
    return _client


def narrate(system_prompt: str, user_prompt: str, *, max_tokens: int = 200) -> str:
    """Goi model <=10B de sinh 1 doan ly do ngan. Luon tra ve string, khong bao gio raise."""
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # noqa: BLE001 - loi provider khong duoc chan pipeline
        return f"[llm_client] khong goi duoc model ({exc!r}); bo qua tuong thuat cho buoc nay."
