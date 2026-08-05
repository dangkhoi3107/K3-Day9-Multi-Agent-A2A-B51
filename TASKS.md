# TASKS — Phân công 5 người

> Xem `architecture.md` cho **thiết kế** (vai trò, luồng handoff, bảng policy). File này chỉ để track **ai làm gì, còn thiếu gì** trong code đã có sẵn ở `src/`. Tick `[x]` khi xong; đừng tự ý xóa mục để "cho gọn" — xóa thì mất dấu vết ai đã làm gì.

## Legend

| Tag | Ý nghĩa |
| --- | --- |
| `P0` | Cần chốt trước khi code phần riêng (đã xong phần lớn) |
| `P1` | Code chính | `P2` | Test + chạy thật | `P3` | Tích hợp cuối |

## Trạng thái hiện tại (đã build sẵn, đọc trước khi bắt đầu)

**Đã merge vào `main`** (octopus merge `son` + `TranTrung` + `Khoi`, sạch, không conflict — verify bằng `git merge-tree` trước khi merge và `pytest` sau khi merge; role 3 push thẳng lên `main` sau đó, đã pull + review + verify tay fixture khớp `orders.csv`): `pytest` → **23 passed, 1 xfail có chủ đích**. `python scripts/run_pipeline.py EC_001` / `EC_022` đã chạy thành công trên case thật.

- **Hạ tầng (xong, không cần đụng vào trừ khi có bug):** `src/config.py`, `src/schemas.py`, `src/evidence.py`, `src/data_access.py`, `src/tracing.py`, `src/llm_client.py`, `src/agents/verifier_agent.py`, `scripts/run_pipeline.py`, `scripts/validate_output.py`, `scripts/package_submission.py`.
- **`src/agents/coordinator.py`:** xong, kể cả 2 quyết định mở trước đó (`seller_ids` trong `affected_entities`, xử lý `verify_fail`) — Vai trò 5 (son) đã chốt, xem `architecture.md` mục 6.
- **`src/agents/order_seller_agent.py`:** xong — Vai trò 1 (Khoi) đã implement `late_seller_ids` + test.
- **`src/agents/payment_agent.py`:** logic xong từ đầu, test đã đủ — Vai trò 2 (TranTrung) đã verify + đề xuất dung sai rule 6 (đang chờ Vai trò 4 xác nhận).
- **`src/agents/delivery_agent.py`:** xong — Vai trò 3 đã implement `late_to_customer` + test, đã verify tay fixture khớp dữ liệu gốc.
- **`logging/metadata.json`:** đã điền (Vai trò 5).

**Còn TODO thật sự — chỉ còn đúng 1 vai trò, không còn ai chặn:** `src/agents/policy_agent.py` (Vai trò 4) — cả 6/6 rule đều làm được ngay, xem "Thứ tự ưu tiên" bên dưới. Mỗi hàm đã có comment `# TODO (Vai trò 4)` kèm công thức trích từ README ngay tại chỗ.

---

## Thứ tự ưu tiên (critical path)

Đọc mục này trước khi chia nhau ra làm — biết task nào phải chờ ai, để không ai ngồi chờ oan.
Hạ tầng dùng chung (`schemas.py`, `data_access.py`, `evidence.py`, `tracing.py`, `coordinator.py`,
`verifier_agent.py`) **đã xong** — không ai phải chờ phần này, bắt tay được ngay.

### Tier 0 — bắt đầu ngay, song song hoàn toàn, không chờ ai

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 1 | Implement + test rule 1 (`canceled_order_paid`) và rule 2 (`unavailable_order_paid`) trong `policy_agent.py` | Vai trò 4 | ⬜ Chưa làm — không chờ ai, làm được ngay |
| 2 | Implement + test rule 5 (`valid_split_payment`) | Vai trò 4 | ⬜ Chưa làm — không chờ ai, làm được ngay |
| 3 | Implement `late_seller_ids` trong `order_seller_agent.py` | Vai trò 1 | ✅ Xong (đã merge vào `main`) |
| 4 | Implement `late_to_customer` trong `delivery_agent.py` | Vai trò 3 | ✅ Xong (đã merge vào `main`) |
| 5 | Chốt dung sai rule 6 (giữ `0.10 BRL` hay đổi khác) | Vai trò 2 + Vai trò 4 | 🟡 Vai trò 2 đã đề xuất `0.10 BRL` (xem `architecture.md` mục 6) — chờ Vai trò 4 xác nhận |

**Vai trò 4 đừng ngồi chờ Vai trò 1/3 — bắt tay ngay với task #1 và #2, đó là 3/6 rule làm được luôn.**

### Tier 1 — hết chặn, làm được ngay

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 6 | Implement + test rule 6 (`unsupported_late_claim`) | Vai trò 4 | ✅ Hết chặn — task #4 (Vai trò 3) đã xong |

### Tier 2 — hết chặn, làm được ngay

| # | Task | Ai | Trạng thái |
| - | --- | -- | --- |
| 7 | Implement + test rule 3 (`late_delivery_seller`) và rule 4 (`late_delivery_logistics`) | Vai trò 4 | ✅ Hết chặn — cả task #3 (Vai trò 1) và #4 (Vai trò 3) đã xong |

**Vai trò 4 giờ không còn bị chặn bởi ai nữa — cả 6/6 rule đều làm được ngay bây giờ.**

### Tier 3 — chỉ chạy có ý nghĩa khi Vai trò 4 xong đủ 6 rule

| # | Task | Ai | Chờ gì |
| - | --- | -- | --- |
| 8 | Chạy full 50 case thật: `python scripts/run_pipeline.py` | Leader | Chờ task #1, #2, #6, #7 (đủ 6/6 rule — chạy sớm hơn chỉ toàn ra fallback confidence thấp như `EC_001` lúc nãy) |
| 9 | `python scripts/validate_output.py`, quay lại sửa đúng người phụ trách tới khi sạch | Leader | Chờ task #8 |

### Tier 4 — cuối cùng, không còn phụ thuộc kỹ thuật

| # | Task | Ai | Chờ gì |
| - | --- | -- | --- |
| 10 | Điền `logging/metadata.json`, chạy `package_submission.py`, nộp form | Leader | Chờ task #9 sạch |
| 11 | Hoàn thiện báo cáo cá nhân | Cả 5 người | Không chặn ai khác — làm song song bất cứ lúc nào rảnh tay, không cần chờ tier nào |

---

## Vai trò 1 — Order & Seller Agent

**File:** `src/agents/order_seller_agent.py` · **Test:** `tests/test_order_seller_agent.py`

- [x] Trong `investigate()`, implement đoạn so sánh `order["order_delivered_carrier_date"]` với `it["shipping_limit_date"]` của từng item để tính `late_seller_ids`.
- [x] Cập nhật `tests/test_order_seller_agent.py` với order_id thật (late-seller, on-time, order không có item row — cả 3 đều lấy từ chính 50 case thật, xem `scripts/find_test_fixtures.py`).
- [x] Viết `test_seller_late_when_carrier_after_shipping_limit()` + bonus `test_seller_on_time_is_not_flagged_late()`.
- [x] `python -m pytest tests/test_order_seller_agent.py -v` — 5/5 pass. Đã verify thêm end-to-end thật trên `EC_022.json` (case chứa order late-seller) qua `run_pipeline.py`.
- [ ] **Còn lại — không phải chờ ai, chỉ cần bạn báo:** nhắn Vai trò 4 là `late_seller_ids` đã chạy đúng, có thể bắt đầu code rule 3/4 phần seller (rule 3/4 vẫn còn chờ thêm Vai trò 3 xong `late_to_customer` mới đủ điều kiện, xem Tier 2 ở trên).

## Vai trò 2 — Payment Agent

**File:** `src/agents/payment_agent.py` · **Test:** `tests/test_payment_agent.py`

- [x] Công thức đối soát đã implement sẵn — đọc lại để xác nhận đúng ý, không cần viết mới.
- [ ] Chốt cùng Vai trò 4: rule 6 (`unsupported_late_claim`) có dùng lại dung sai `0.10 BRL` không (biến `UNSUPPORTED_CLAIM_TOLERANCE_BRL` trong `src/config.py`) — ghi quyết định vào `architecture.md` mục 6. **Role 2 note:** đã ghi đề xuất trong `architecture.md`, chờ Role 4 xác nhận.
- [x] Mở `tests/test_payment_agent.py`, viết 2 test còn để `# TODO` cuối file (2 payment khớp = valid split; 2 payment lệch = không hợp lệ) — tìm order_id thật bằng cách lọc `data/olist_order_payments_dataset.csv` theo số dòng/`order_id`.
- [x] Chạy `python -m pytest tests/test_payment_agent.py -v`.
- [x] Verify trên vài case thật: so `payment_total_brl` agent tính ra với tổng cột `payment_value` lọc tay trong CSV.

## Vai trò 3 — Delivery Agent

**File:** `src/agents/delivery_agent.py` · **Test:** `tests/test_delivery_agent.py`

- [x] Trong `investigate()`, implement đoạn so sánh `delivered_customer_date` với `estimated_date` để tính `late_to_customer` — đã push thẳng lên `main`, đã review: đúng logic (giữ `None` khi chưa giao), không sửa/copy nhầm.
- [x] Cập nhật `tests/test_delivery_agent.py` với order_id thật (không dùng `REPLACE_ME` nữa) — đã đối chiếu tay cả 3 fixture (`EC_001` trễ hạn, `EC_002` đúng hạn, `EC_003` chưa giao) với `orders.csv` gốc, khớp 100%.
- [x] `test_delivered_on_time()` và `test_delivered_late()` đã viết, cả 2 pass.
- [x] `python -m pytest tests/test_delivery_agent.py -v` — 5/5 pass. Full suite sau khi merge: 23 passed, 1 xfail.
- [ ] **Còn lại — không phải chờ ai, chỉ cần báo:** báo Vai trò 4 là `late_to_customer` đã chạy đúng và merge vào `main` — rule 3/4/6 giờ không còn bị chặn bởi Vai trò 1 hay 3 nữa.
- [ ] Khi có kết quả 50 case thật: rà xem `order_status` có giá trị lạ nào ngoài `delivered/canceled/unavailable` không, báo sớm cho Vai trò 4 (chưa thấy làm mục này).

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

- [x] Review + merge nhánh của các người còn lại vào `main` (đã merge `son` + `TranTrung` + `Khoi`, octopus merge sạch, `pytest` 21 passed/1 xfail sau merge) — **còn nhánh Vai trò 3, 4 sẽ merge tiếp khi họ xong.**
- [x] Trong `coordinator.py::_process`, TODO về `seller_ids` trong `affected_entities` — đã chốt = `late_seller_ids` (seller vi phạm), ghi rõ lý do trong `architecture.md` mục 6.
- [x] Quyết định TODO thứ hai trong `_process`: `verify_fail` → hạ `confidence` xuống `0.1` (không tự sửa số liệu Policy Agent), vẫn ghi file. Đã implement (`VERIFY_FAIL_CONFIDENCE`).
- [ ] Sau khi Vai trò 3 + 4 xong: chạy `python scripts/run_pipeline.py` (full 50 case) → `python scripts/validate_output.py` → sửa lỗi tới khi sạch.
- [x] Điền `logging/metadata.json`: tên model thật đã dùng, param size, framework, runtime, `policy_version`.
- [ ] Chạy `python scripts/package_submission.py`, kiểm tra `submission.zip` chỉ chứa `output/` (đúng README, không kèm source/.env).
- [ ] Review 5 file `individual_[5 số cuối MSSV]_[Họ Tên].md` — mỗi người 1 file riêng, không dùng chung.
- [ ] Rà lại `architecture.md` — bản nháp đã có, cập nhật phần nào lệch so với code thật (đặc biệt mục 6 "Quyết định kỹ thuật cần chốt").

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

- [ ] `python -m pytest` — tất cả pass (không còn `xfail`).
- [ ] `python scripts/run_pipeline.py` chạy full 50 case, không case nào rơi fallback ngoài ý muốn.
- [ ] `python scripts/validate_output.py` — sạch, không lỗi.
- [ ] `git status` — không có `.env`, không có `archive/` trong danh sách staged.
