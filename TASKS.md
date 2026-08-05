# TASKS — Phân công 5 người

> Xem `architecture.md` cho **thiết kế** (vai trò, luồng handoff, bảng policy). File này chỉ để track **ai làm gì, còn thiếu gì** trong code đã có sẵn ở `src/`. Tick `[x]` khi xong; đừng tự ý xóa mục để "cho gọn" — xóa thì mất dấu vết ai đã làm gì.

## Legend

| Tag | Ý nghĩa |
| --- | --- |
| `P0` | Cần chốt trước khi code phần riêng (đã xong phần lớn) |
| `P1` | Code chính | `P2` | Test + chạy thật | `P3` | Tích hợp cuối |

## Trạng thái hiện tại (đã build sẵn, đọc trước khi bắt đầu)

Khung code đã chạy được thật (`pytest`: 17 passed / 1 xfail có chủ đích; `python scripts/run_pipeline.py EC_001` đã chạy thành công trên case thật, xem `output/EC_001.json` + `logging/trace.jsonl`). **Phần hạ tầng dưới đây đã xong, không cần đụng vào trừ khi có bug:**

- `src/config.py`, `src/schemas.py`, `src/evidence.py`, `src/data_access.py`, `src/tracing.py`, `src/llm_client.py`
- `src/agents/verifier_agent.py`, `src/agents/coordinator.py`
- `scripts/run_pipeline.py`, `scripts/validate_output.py`, `scripts/package_submission.py`

**Phần còn TODO — đúng phần việc của 4 vai trò dưới đây:** mỗi hàm cần sửa đã có comment `# TODO (Vai trò N)` kèm công thức trích từ README ngay tại chỗ, và có sẵn pseudo-code bị comment-out để tham khảo.

---

## Vai trò 1 — Order & Seller Agent

**File:** `src/agents/order_seller_agent.py` · **Test:** `tests/test_order_seller_agent.py`

- [ ] Trong `investigate()`, implement đoạn so sánh `order["order_delivered_carrier_date"]` với `it["shipping_limit_date"]` của từng item để tính `late_seller_ids` (pseudo-code có sẵn dạng comment ngay dưới TODO — nhớ `pd.notna(...)` trước khi so sánh).
- [ ] Mở `tests/test_order_seller_agent.py`, thay 2 chỗ `REPLACE_ME` bằng order_id thật (order không có item row, nếu tìm thấy trong 50 case).
- [ ] Viết thêm `test_seller_late_when_carrier_after_shipping_limit()` (đã có gợi ý cuối file test).
- [ ] Chạy `python -m pytest tests/test_order_seller_agent.py -v` tới khi xanh hết.
- [ ] Báo Vai trò 4 khi `late_seller_ids` đã hoạt động đúng — Policy Agent (rule 3/4) phụ thuộc trực tiếp field này.

## Vai trò 2 — Payment Agent

**File:** `src/agents/payment_agent.py` · **Test:** `tests/test_payment_agent.py`

- [ ] Công thức đối soát đã implement sẵn — đọc lại để xác nhận đúng ý, không cần viết mới.
- [ ] Chốt cùng Vai trò 4: rule 6 (`unsupported_late_claim`) có dùng lại dung sai `0.10 BRL` không (biến `UNSUPPORTED_CLAIM_TOLERANCE_BRL` trong `src/config.py`) — ghi quyết định vào `architecture.md` mục 6.
- [ ] Mở `tests/test_payment_agent.py`, viết 2 test còn để `# TODO` cuối file (2 payment khớp = valid split; 2 payment lệch = không hợp lệ) — tìm order_id thật bằng cách lọc `data/olist_order_payments_dataset.csv` theo số dòng/`order_id`.
- [ ] Chạy `python -m pytest tests/test_payment_agent.py -v`.
- [ ] Verify trên vài case thật: so `payment_total_brl` agent tính ra với tổng cột `payment_value` lọc tay trong CSV.

## Vai trò 3 — Delivery Agent

**File:** `src/agents/delivery_agent.py` · **Test:** `tests/test_delivery_agent.py`

- [ ] Trong `investigate()`, implement đoạn so sánh `delivered_customer_date` với `estimated_date` để tính `late_to_customer` (pseudo-code có sẵn dạng comment — nhớ giữ `None` khi chưa giao, không suy diễn).
- [ ] Thay `REPLACE_ME` trong `tests/test_delivery_agent.py` bằng order_id thật có `order_delivered_customer_date` rỗng.
- [ ] Viết `test_delivered_on_time()` và `test_delivered_late()` (đã có gợi ý cuối file test).
- [ ] Chạy `python -m pytest tests/test_delivery_agent.py -v`.
- [ ] Báo Vai trò 4 khi `late_to_customer` hoạt động đúng — Policy Agent (rule 3/4/6) phụ thuộc field này.
- [ ] Khi có kết quả 50 case thật: rà xem `order_status` có giá trị lạ nào ngoài `delivered/canceled/unavailable` không, báo sớm cho Vai trò 4.

## Vai trò 4 — Policy Agent (rule engine)

**File:** `src/agents/policy_agent.py` · **Test:** `tests/test_policy_agent.py`

Phần việc nặng nhất — phụ thuộc field từ Vai trò 1 (`late_seller_ids`) và Vai trò 3 (`late_to_customer`), nên có thể bắt đầu bằng facts giả (`tests/test_policy_agent.py` đã có sẵn helper `_order_seller()/_payment()/_delivery()` để tự dựng facts, không cần chờ 2 vai trò kia xong mới code được).

- [ ] Implement lần lượt 6 hàm `_rule_1_canceled_order_paid` → `_rule_6_unsupported_late_claim` (mỗi hàm đã có docstring trích đúng điều kiện + cause_code + action từ README mục 4).
- [ ] Chốt cùng Vai trò 2: dung sai rule 6.
- [ ] Viết `test_rule2` .. `test_rule6` theo đúng mẫu `test_rule1_canceled_order_paid` (đã viết sẵn, đang bị đánh dấu `@pytest.mark.xfail` vì rule 1 chưa cài — **xóa dòng `@pytest.mark.xfail` đó khi bạn implement xong rule 1**, đó là tín hiệu để biết mình đã xong).
- [ ] Viết `test_priority_canceled_beats_valid_split_payment()` (khung có sẵn cuối file, đang comment) — test quan trọng nhất vì kiểm tra đúng THỨ TỰ ưu tiên, không chỉ đúng từng rule riêng lẻ.
- [ ] Chạy `python -m pytest tests/test_policy_agent.py -v` tới khi xanh hết (kể cả rule 1).
- [ ] Sau khi cả nhóm merge: chạy full 50 case (`python scripts/run_pipeline.py`), thống kê phân bố 6 `primary_issue`, cùng nhóm review case nào rơi vào nhánh fallback (`confidence=0.1`) — nghĩa là chưa rule nào khớp, cần xem lại logic.

## Vai trò 5 — Coordinator + Verifier + Hạ tầng (đã làm phần lớn — còn lại là tích hợp)

**File:** `src/agents/coordinator.py`, `scripts/*`, `logging/metadata.json`

- [ ] Review + merge nhánh của 4 người còn lại vào `main`; chạy `pytest` sau mỗi lần merge.
- [ ] Trong `coordinator.py::_process`, có 1 TODO về `seller_ids` trong `affected_entities` (đang mặc định = seller vi phạm) — xác nhận lại với Vai trò 1/4 xem có cần đổi theo từng rule không.
- [ ] Quyết định TODO thứ hai trong `_process`: khi Verifier trả `verify_fail`, có nên tự động hạ `confidence` / gắn cờ thay vì chỉ log không.
- [ ] Sau khi 4 vai trò xong: chạy `python scripts/run_pipeline.py` (full 50 case) → `python scripts/validate_output.py` → sửa lỗi tới khi sạch.
- [ ] Điền `logging/metadata.json`: tên model thật đã dùng, param size, framework, runtime, `policy_version`.
- [ ] Chạy `python scripts/package_submission.py`, kiểm tra `submission.zip` chỉ chứa `output/` (đúng README, không kèm source/.env).
- [ ] Review 5 file `individual_[5 số cuối MSSV]_[Họ Tên].md` — mỗi người 1 file riêng, không dùng chung.
- [ ] Rà lại `architecture.md` — bản nháp đã có, cập nhật phần nào lệch so với code thật (đặc biệt mục 6 "Quyết định kỹ thuật cần chốt").

---

## Trước khi nộp — mọi người cùng kiểm

- [ ] `python -m pytest` — tất cả pass (không còn `xfail`).
- [ ] `python scripts/run_pipeline.py` chạy full 50 case, không case nào rơi fallback ngoài ý muốn.
- [ ] `python scripts/validate_output.py` — sạch, không lỗi.
- [ ] `git status` — không có `.env`, không có `archive/` trong danh sách staged.
