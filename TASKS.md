# TASKS — Phân công 5 người

> Xem `architecture.md` cho **thiết kế** (vai trò, luồng handoff, bảng policy). File này chỉ để track **ai làm gì, còn thiếu gì** trong code đã có sẵn ở `src/`. Tick `[x]` khi xong; đừng tự ý xóa mục để "cho gọn" — xóa thì mất dấu vết ai đã làm gì.

## Legend

| Tag | Ý nghĩa |
| --- | --- |
| `P0` | Cần chốt trước khi code phần riêng (đã xong phần lớn) |
| `P1` | Code chính | `P2` | Test + chạy thật | `P3` | Tích hợp cuối |

## Trạng thái hiện tại (đã build sẵn, đọc trước khi bắt đầu)

**CẢ 4 AGENT NGHIỆP VỤ ĐÃ XONG VÀ ĐÃ MERGE VÀO `main`.** `pytest` → **30 passed, 0 fail, 0 xfail**. Full batch `python scripts/run_pipeline.py` đã chạy thật trên **50/50 case** (nhánh `dangduc`), `python scripts/validate_output.py` đã sạch. Đã verify độc lập: tự tính lại đáp án đúng cho cả 50 case từ CSV gốc (code viết riêng, không dùng lại code trong repo) — khớp 100% với output thật, không case nào rơi vào fallback.

- **Hạ tầng + cả 5 agent (xong hết):** `src/config.py`, `src/schemas.py`, `src/evidence.py`, `src/data_access.py`, `src/tracing.py`, `src/llm_client.py`, `src/agents/coordinator.py`, `src/agents/order_seller_agent.py` (Khoi), `src/agents/payment_agent.py` (TranTrung), `src/agents/delivery_agent.py` (role 3), `src/agents/policy_agent.py` (dangduc), `src/agents/verifier_agent.py`, `scripts/*`.
- **`logging/metadata.json`:** đã điền.
- **Dung sai rule 6:** đã chốt `0.10 BRL` (Role 2 + Role 4), ghi trong `architecture.md` mục 6.

**Còn lại chỉ là việc của Leader (đóng gói, nộp) + báo cáo cá nhân từng người — không còn TODO code nào.**

---

## Thứ tự ưu tiên (critical path)

Đọc mục này trước khi chia nhau ra làm — biết task nào phải chờ ai, để không ai ngồi chờ oan.
Hạ tầng dùng chung (`schemas.py`, `data_access.py`, `evidence.py`, `tracing.py`, `coordinator.py`,
`verifier_agent.py`) **đã xong** — không ai phải chờ phần này, bắt tay được ngay.

### Tier 0 — bắt đầu ngay, song song hoàn toàn, không chờ ai

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 1 | Implement + test rule 1 (`canceled_order_paid`) và rule 2 (`unavailable_order_paid`) trong `policy_agent.py` | Vai trò 4 | ✅ Xong |
| 2 | Implement + test rule 5 (`valid_split_payment`) | Vai trò 4 | ✅ Xong |
| 3 | Implement `late_seller_ids` trong `order_seller_agent.py` | Vai trò 1 | ✅ Xong |
| 4 | Implement `late_to_customer` trong `delivery_agent.py` | Vai trò 3 | ✅ Xong |
| 5 | Chốt dung sai rule 6 (giữ `0.10 BRL` hay đổi khác) | Vai trò 2 + Vai trò 4 | ✅ Xong — giữ `0.10 BRL` |

### Tier 1 & 2 — hoàn tất

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 6 | Implement + test rule 6 (`unsupported_late_claim`) | Vai trò 4 | ✅ Xong |
| 7 | Implement + test rule 3 (`late_delivery_seller`) và rule 4 (`late_delivery_logistics`) | Vai trò 4 | ✅ Xong |

### Tier 3 & 4 — đã chạy thật, đã verify

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 8 | Chạy full 50 case thật: `python scripts/run_pipeline.py` | Leader/dangduc | ✅ Xong — 50/50 file, đã verify độc lập khớp 100% |
| 9 | `python scripts/validate_output.py` | Leader | ✅ Xong — sạch, evidence đều tra cứu được thật |
| 10 | Điền `logging/metadata.json`, chạy `package_submission.py`, nộp form | Leader | ⬜ `metadata.json` đã điền — còn `package_submission.py` + nộp form |
| 11 | Hoàn thiện báo cáo cá nhân | Cả 5 người | ⬜ Chưa xác nhận — mỗi người tự kiểm file `individual_...md` của mình |

---

## Vai trò 1 — Order & Seller Agent

**File:** `src/agents/order_seller_agent.py` · **Test:** `tests/test_order_seller_agent.py`

- [x] Trong `investigate()`, implement đoạn so sánh `order["order_delivered_carrier_date"]` với `it["shipping_limit_date"]` của từng item để tính `late_seller_ids`.
- [x] Cập nhật `tests/test_order_seller_agent.py` với order_id thật (late-seller, on-time, order không có item row — cả 3 đều lấy từ chính 50 case thật, xem `scripts/find_test_fixtures.py`).
- [x] Viết `test_seller_late_when_carrier_after_shipping_limit()` + bonus `test_seller_on_time_is_not_flagged_late()`.
- [x] `python -m pytest tests/test_order_seller_agent.py -v` — 5/5 pass. Đã verify thêm end-to-end thật trên `EC_022.json` (case chứa order late-seller) qua `run_pipeline.py`.
- [x] Đã báo/đã dùng: Vai trò 4 (dangduc) đã dùng `late_seller_ids` đúng trong rule 3/4, verify qua độc lập khớp 100%.

## Vai trò 2 — Payment Agent

**File:** `src/agents/payment_agent.py` · **Test:** `tests/test_payment_agent.py`

- [x] Công thức đối soát đã implement sẵn — đọc lại để xác nhận đúng ý, không cần viết mới.
- [x] Chốt cùng Vai trò 4: dùng lại dung sai `0.10 BRL` cho rule 6 — đã xác nhận, ghi trong `architecture.md` mục 6.
- [x] Mở `tests/test_payment_agent.py`, viết 2 test còn để `# TODO` cuối file (2 payment khớp = valid split; 2 payment lệch = không hợp lệ) — tìm order_id thật bằng cách lọc `data/olist_order_payments_dataset.csv` theo số dòng/`order_id`.
- [x] Chạy `python -m pytest tests/test_payment_agent.py -v`.
- [x] Verify trên vài case thật: so `payment_total_brl` agent tính ra với tổng cột `payment_value` lọc tay trong CSV.

## Vai trò 3 — Delivery Agent

**File:** `src/agents/delivery_agent.py` · **Test:** `tests/test_delivery_agent.py`

- [x] Trong `investigate()`, implement đoạn so sánh `delivered_customer_date` với `estimated_date` để tính `late_to_customer` — đã push thẳng lên `main`, đã review: đúng logic (giữ `None` khi chưa giao), không sửa/copy nhầm.
- [x] Cập nhật `tests/test_delivery_agent.py` với order_id thật (không dùng `REPLACE_ME` nữa) — đã đối chiếu tay cả 3 fixture (`EC_001` trễ hạn, `EC_002` đúng hạn, `EC_003` chưa giao) với `orders.csv` gốc, khớp 100%.
- [x] `test_delivered_on_time()` và `test_delivered_late()` đã viết, cả 2 pass.
- [x] `python -m pytest tests/test_delivery_agent.py -v` — 5/5 pass. Full suite sau khi merge: 23 passed, 1 xfail.
- [x] Đã báo/đã dùng: Vai trò 4 (dangduc) đã dùng `late_to_customer` đúng trong rule 3/4/6.
- [x] Đã gián tiếp xác nhận: cả 50/50 case thật khớp đúng 1 trong 6 rule khi verify độc lập — không case nào bị `order_status` lạ làm rơi vào fallback ngoài ý muốn.

## Vai trò 4 — Policy Agent (rule engine)

**File:** `src/agents/policy_agent.py` · **Test:** `tests/test_policy_agent.py`

Phần việc nặng nhất — phụ thuộc field từ Vai trò 1 (`late_seller_ids`) và Vai trò 3 (`late_to_customer`), nên có thể bắt đầu bằng facts giả (`tests/test_policy_agent.py` đã có sẵn helper `_order_seller()/_payment()/_delivery()` để tự dựng facts, không cần chờ 2 vai trò kia xong mới code được).

- [x] Implement lần lượt 6 hàm `_rule_1_canceled_order_paid` → `_rule_6_unsupported_late_claim` (mỗi hàm đã có docstring trích đúng điều kiện + cause_code + action từ README mục 4).
- [x] Chốt cùng Vai trò 2: dung sai rule 6 — **Giữ `0.10 BRL`, ghi trong `architecture.md` mục 6.**
- [x] Viết `test_rule2` .. `test_rule6` theo đúng mẫu `test_rule1_canceled_order_paid`.
- [x] Viết `test_priority_canceled_beats_valid_split_payment()` — test thứ tự ưu tiên.
- [x] Chạy `python -m pytest tests/test_policy_agent.py -v` — 8/8 PASSED xanh hết!
- [x] Chạy full 50 case (`python scripts/run_pipeline.py`).

## Vai trò 5 (Leader) — Coordinator + Verifier + Hạ tầng (đã làm phần lớn — còn lại là tích hợp)

**File:** `src/agents/coordinator.py`, `scripts/*`, `logging/metadata.json`

- [x] Review + merge nhánh của **cả 4 người** vào `main` (`son`, `TranTrung`, `Khoi`, `dangduc`) — tất cả đều review kỹ + verify trước khi merge, không nhánh nào bị conflict. `pytest` cuối cùng: **30 passed, 0 fail, 0 xfail.**
- [x] Trong `coordinator.py::_process`, TODO về `seller_ids` trong `affected_entities` — đã chốt = `late_seller_ids` (seller vi phạm), ghi rõ lý do trong `architecture.md` mục 6.
- [x] Quyết định TODO thứ hai trong `_process`: `verify_fail` → hạ `confidence` xuống `0.1` (không tự sửa số liệu Policy Agent), vẫn ghi file. Đã implement (`VERIFY_FAIL_CONFIDENCE`).
- [x] Chạy `python scripts/run_pipeline.py` (full 50 case) → `python scripts/validate_output.py` — **cả 2 đã sạch** (dangduc chạy, đã verify độc lập lại toàn bộ).
- [x] Điền `logging/metadata.json`: tên model thật đã dùng, param size, framework, runtime, `policy_version`.
- [ ] Chạy `python scripts/package_submission.py`, kiểm tra `submission.zip` chỉ chứa `output/` (đúng README, không kèm source/.env). **— việc kỹ thuật cuối cùng còn lại.**
- [ ] Review 5 file `individual_[5 số cuối MSSV]_[Họ Tên].md` — mỗi người 1 file riêng, không dùng chung.
- [x] Rà lại `architecture.md` mục 6 — đã cập nhật khớp code thật (dung sai rule 6, làm tròn tiền, xác nhận 50/50 case không rơi fallback).

### Lớp việc thêm của Leader — quản lý người/thời gian, không phải code

Nên là cùng 1 người với Vai trò 5 (đã nhìn thấy toàn cảnh hệ thống) chứ không tách thành người
thứ 6 đứng ngoài không code — 5 người là đủ, leader vẫn code phần của mình, chỉ gánh thêm phần dưới.

**Trước giờ G**

- [ ] Đảm bảo cả 5 người đã đọc `README.md`, `architecture.md`, `TASKS.md` — biết rõ file/hàm mình phụ trách, không ai mù mờ vai trò lúc bắt đầu.
- [ ] Có 1 kênh chat riêng để báo block/lỗi ngay lập tức trong lúc chạy — đừng để ai im lặng cả nửa tiếng vì kẹt 1 dòng code.
- [ ] Xác nhận cả 5 người push/pull được đúng repo (không ai lỡ code trên fork/clone lạc).

**Trong lúc chạy — Checkpoint 2 (9h30–12h30)**

- [ ] Hỏi thăm tiến độ định kỳ (khoảng mỗi 30–45 phút) — vai trò nào đang block thì ưu tiên gỡ trước, đừng để tự bơi đến hết giờ mới báo.
- [ ] Chốt các quyết định đang mở khi nhóm tranh luận không ra nhanh: dung sai rule 6, cách xử lý khi Verifier fail, `seller_ids` trong `affected_entities` (xem đúng 3 TODO này trong code) — leader quyết cuối để không mất thời gian chung, ghi lại lý do vào `architecture.md` mục 6.
- [ ] Giữ `main` luôn chạy được: không merge code chưa qua `pytest` của chính vai trò đó.
- [ ] Theo dõi đồng hồ: còn ~45 phút mà 1–2 rule chưa xong thì ưu tiên "có kết quả confidence thấp cho đủ 50 file" hơn "cố hoàn hảo rồi lỡ crash/thiếu file" — nhắc anh em đừng cầu toàn quá đà.

**Checkpoint 3 (12h30–13h) — chốt & nộp**

- [ ] Chạy `python scripts/run_pipeline.py` (full 50 case) lần cuối, `python scripts/validate_output.py` phải sạch mới cho qua.
- [ ] Điền `logging/metadata.json` (model, param size, framework, runtime, `policy_version`) đúng thứ đã dùng thật.
- [ ] Chạy `python scripts/package_submission.py`, kiểm tay `submission.zip` chỉ có `output/` đúng 50 file — không kèm source code/`.env`.
- [ ] Xác nhận đủ 5 file `individual_[5 số cuối MSSV]_[Họ Tên].md`, không ai bỏ trống hoặc chép bài người khác.
- [ ] Soát `git status`/`git log` lần cuối: không commit `.env`, không commit `archive/`.
- [ ] Nộp: dán link GitHub (giữ nguyên tên repo) vào biểu mẫu nộp bài, chọn rating, xác nhận nộp.

---

## Trước khi nộp — mọi người cùng kiểm

- [x] `python -m pytest` — 30 passed, không còn `xfail`.
- [x] `python scripts/run_pipeline.py` chạy full 50 case — không case nào rơi fallback ngoài ý muốn (đã verify độc lập).
- [x] `python scripts/validate_output.py` — sạch, không lỗi.
- [ ] `git status` — không có `.env`, không có `archive/` trong danh sách staged (soát lại lần cuối trước khi push commit nộp bài).
- [ ] `python scripts/package_submission.py` đã chạy, `submission.zip` chỉ chứa `output/`.
- [ ] Đủ 5 báo cáo cá nhân, không ai bỏ trống.
