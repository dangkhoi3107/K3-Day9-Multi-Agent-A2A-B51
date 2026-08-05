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

## Thứ tự ưu tiên (critical path)

Đọc mục này trước khi chia nhau ra làm — biết task nào phải chờ ai, để không ai ngồi chờ oan.
Hạ tầng dùng chung (`schemas.py`, `data_access.py`, `evidence.py`, `tracing.py`, `coordinator.py`,
`verifier_agent.py`) **đã xong** — không ai phải chờ phần này, bắt tay được ngay.

### Tier 0 — bắt đầu ngay, song song hoàn toàn, không chờ ai

| # | Task | Ai | Vì sao không bị chặn |
| - | --- | -- | --- |
| 1 | Implement + test rule 1 (`canceled_order_paid`) và rule 2 (`unavailable_order_paid`) trong `policy_agent.py` | Vai trò 4 | Chỉ cần `order_status` + `payment_total_brl` — cả 2 field này hạ tầng đã cung cấp sẵn, không nằm trong TODO của ai |
| 2 | Implement + test rule 5 (`valid_split_payment`) | Vai trò 4 | Chỉ cần `is_split`/`is_reconciled` — Payment Agent (Vai trò 2) đã implement xong từ đầu |
| 3 | Implement `late_seller_ids` trong `order_seller_agent.py` | Vai trò 1 | Độc lập hoàn toàn với Delivery Agent |
| 4 | Implement `late_to_customer` trong `delivery_agent.py` | Vai trò 3 | Độc lập hoàn toàn với Order & Seller Agent |
| 5 | Chốt dung sai rule 6 (giữ `0.10 BRL` hay đổi khác) | Vai trò 2 + Vai trò 4 | Chỉ cần trao đổi 2 phút — `config.py` đã có giá trị mặc định nên không ai bị chặn nếu chưa chốt kịp |

**Vai trò 4 đừng ngồi chờ Vai trò 1/3 — bắt tay ngay với task #1 và #2, đó là 3/6 rule làm được luôn.**

### Tier 1 — chờ đúng 1 người xong

| # | Task | Ai | Chờ gì |
| - | --- | -- | --- |
| 6 | Implement + test rule 6 (`unsupported_late_claim`) | Vai trò 4 | Chờ task #4 (Vai trò 3 xong `late_to_customer`) |

### Tier 2 — chờ đủ 2 người xong

| # | Task | Ai | Chờ gì |
| - | --- | -- | --- |
| 7 | Implement + test rule 3 (`late_delivery_seller`) và rule 4 (`late_delivery_logistics`) | Vai trò 4 | Chờ CẢ task #3 (Vai trò 1) VÀ task #4 (Vai trò 3) |

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

## Vai trò 5 (Leader) — Coordinator + Verifier + Hạ tầng (đã làm phần lớn — còn lại là tích hợp)

**File:** `src/agents/coordinator.py`, `scripts/*`, `logging/metadata.json`

- [ ] Review + merge nhánh của 4 người còn lại vào `main`; chạy `pytest` sau mỗi lần merge.
- [ ] Trong `coordinator.py::_process`, có 1 TODO về `seller_ids` trong `affected_entities` (đang mặc định = seller vi phạm) — xác nhận lại với Vai trò 1/4 xem có cần đổi theo từng rule không.
- [ ] Quyết định TODO thứ hai trong `_process`: khi Verifier trả `verify_fail`, có nên tự động hạ `confidence` / gắn cờ thay vì chỉ log không.
- [ ] Sau khi 4 vai trò xong: chạy `python scripts/run_pipeline.py` (full 50 case) → `python scripts/validate_output.py` → sửa lỗi tới khi sạch.
- [ ] Điền `logging/metadata.json`: tên model thật đã dùng, param size, framework, runtime, `policy_version`.
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
