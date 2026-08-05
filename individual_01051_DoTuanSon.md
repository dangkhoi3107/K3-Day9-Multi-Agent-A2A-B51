# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                        |
| --------------- | ----------------------------------------------- |
| Họ và tên       | Đỗ Tuấn Sơn                                      |
| MSSV            | (…)01051                                         |
| Khóa/Lớp        | K3 / B51                                         |
| Vai trò chính   | Vai trò 5 — Coordinator + Verifier + Hạ tầng    |
| Ngày hoàn thành | 2026-08-05                                       |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable            | File/hàm phụ trách                                                  | Input nhận vào                        | Output bàn giao                                              | Trạng thái   |
| ----------------------------- | ------------------------------------------------------------------ | ------------------------------------- | ----------------------------------------------------------- | ------------ |
| Coordinator (điều phối 1 case) | `src/agents/coordinator.py` — `run_case`, `_process`, `_fallback_output` | `input/EC_XXX.json`                   | `output/EC_XXX.json` hợp lệ schema + dòng trace              | Hoàn thành   |
| Verifier Agent                | `src/agents/verifier_agent.py` — `validate_schema`, `verify`       | dự thảo `CaseOutput` từ Coordinator   | pass/fail + danh sách lỗi (evidence có thật, số tiền khớp)   | Hoàn thành   |
| Hạ tầng dùng chung            | `src/config.py`, `src/schemas.py`, `src/evidence.py`, `src/data_access.py`, `src/tracing.py`, `src/llm_client.py` | CSV `data/`, `.env`                   | schema hợp đồng, evidence-ID builder, data store, trace     | Hoàn thành   |
| Scripts vận hành              | `scripts/run_pipeline.py`, `scripts/validate_output.py`, `scripts/package_submission.py` | `input/`, `output/`                   | chạy pipeline, self-check output, đóng gói `submission.zip`  | Hoàn thành   |
| Metadata nộp bài             | `logging/metadata.json`                                            | quyết định model/framework/runtime    | metadata hợp lệ JSON (model, param size, framework, runtime) | Hoàn thành   |
| Chạy full 50 case + đóng gói  | `scripts/run_pipeline.py` (không tham số) → `validate_output.py`   | 4 agent Role 1–4 đã implement         | 50 file `output/` + `submission.zip`                        | **Chưa hoàn thành — chờ Role 1–4** |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                                   | Thành viên/module được hỗ trợ | Kết quả                                                                             |
| ------------------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------- |
| Chốt & tài liệu hóa 2 quyết định tích hợp   | Vai trò 1 & 4 (policy/entity) | Gỡ 2 `# TODO` trong `_process`, ghi quyết định vào `architecture.md` mục 6         |
| Cung cấp facts giả cho test độc lập         | Vai trò 4 (Policy Agent)      | Helper trong `tests/test_policy_agent.py` cho phép Role 4 code trước khi 1/3 xong |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện                                    | File/hàm/artifact liên quan                | Kết quả bàn giao                                   | Cách xác minh                                  |
| ------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------- | ---------------------------------------------- |
| Điều phối pipeline 1 case, không bao giờ để thiếu file  | `coordinator.py:run_case` + `_fallback_output` | `output/EC_001.json` sinh đúng schema             | `python scripts/run_pipeline.py EC_001`        |
| Kiểm chứng output trước khi ghi (chống hallucination)   | `verifier_agent.py:verify`                 | `verify_pass` trong `logging/trace.jsonl`          | trace: event `verify_pass` cho EC_001          |
| Chốt xử lý `verify_fail`: hạ confidence + gắn cờ        | `coordinator.py` (`VERIFY_FAIL_CONFIDENCE`) | verify fail → confidence=0.1 + `verify_fail_flagged` | `architecture.md` mục 6; `pytest`              |
| Chốt `seller_ids` = `late_seller_ids`                   | `coordinator.py:_process`                  | affected_entities nhất quán với responsible_party  | `architecture.md` mục 6                        |
| Điền metadata nộp bài                                    | `logging/metadata.json`                    | JSON hợp lệ, khai báo model ≤10B                   | `python -c "import json;json.load(open(...))"` |

Output cụ thể do phần việc của tôi tạo ra và xác minh:

`output/EC_001.json` — chạy end-to-end qua toàn bộ 6 agent, `verifier_agent` trả `verify_pass`, số tiền nội bộ nhất quán (`item 119.90 + freight 12.04 = payment 131.94 BRL`, `recommended_refund 0.0` khớp action `reject_late_refund`), mọi `evidence_id` tra ngược được về `data/`. Kèm trace đầy đủ 6 bước handoff trong `logging/trace.jsonl`.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Coordinator phải điều phối 3 agent dữ liệu (Order&Seller, Payment, Delivery) → Policy → Verifier cho từng case, và **bảo đảm bất biến hard-gate của README mục 8**: `output/` luôn đủ 50 file JSON hợp lệ schema, không bao giờ có evidence bịa hay số tiền không nhất quán lọt ra ngoài. Một case lỗi không được làm thiếu file.

### Cách triển khai

- `run_case` bọc toàn bộ `_process` trong `try/except`: bất kỳ exception nào (kể cả schema invalid do Verifier raise) → ghi `_fallback_output` (JSON hợp lệ, `confidence=0.0`) thay vì bỏ trống → giữ đủ 50 file.
- `_process` gom evidence từ 3 agent (khử trùng lặp, cắt ≤10), build `CaseOutput`, rồi **bắt buộc qua 2 cửa Verifier**: `validate_schema` (parse Pydantic) và `verify` (evidence tồn tại thật + số tiền khớp công thức action). Schema fail → raise → fallback. Evidence/số tiền fail → giữ nguyên số liệu Policy nhưng **hạ `confidence` xuống 0.1** và log `verify_fail_flagged` để review tay.
- Verifier **không sửa** quyết định của Policy Agent — chỉ trả pass/fail + lý do; Coordinator mới là nơi quyết định bước tiếp. Đây là ranh giới trách nhiệm giữ cho hệ thống kiểm chứng được.
- Text do LLM sinh chỉ đi vào `trace.jsonl`, **không bao giờ** vào `evidence_ids`/ID/số tiền của output — mọi field chấm điểm đều tất định (pandas + rule engine).

### Input, output và contract

| Thành phần              | Mô tả                                                                         |
| ----------------------- | ----------------------------------------------------------------------------- |
| Input                   | `input/EC_XXX.json` (`CaseInput`: `claimed_order_id`, `policy_version`, …)     |
| Output                  | `output/EC_XXX.json` (`CaseOutput`, README mục 6) + 1 dòng/bước vào trace      |
| Module phụ thuộc        | `order_seller_agent`, `payment_agent`, `delivery_agent`, `policy_agent` (facts) |
| Module sử dụng output   | `scripts/validate_output.py`, `scripts/package_submission.py`, người chấm      |
| Điều kiện lỗi cần xử lý | Agent raise, schema invalid, evidence không tồn tại, số tiền lệch, ngày rỗng   |

### Cách xác minh

```bash
python -m pytest -q
python scripts/run_pipeline.py EC_001
python -c "import json; json.load(open('logging/metadata.json')); print('metadata OK')"
```

- **Kết quả mong đợi:** test hạ tầng xanh; EC_001 sinh 1 file hợp lệ + trace có `verify_pass`; metadata parse được.
- **Kết quả thực tế:** `17 passed, 1 xfailed` (xfail có chủ đích — rule 1 của Role 4 chưa cài); `output/EC_001.json` sinh đúng, trace ghi đủ 6 bước; `metadata OK`.
- **Artifact/log:** `output/EC_001.json`, `logging/trace.jsonl`, `logging/metadata.json` (không chứa secret; `.env` đã trong `.gitignore`).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi `verifier_agent.verify()` trả fail vì evidence/số tiền không nhất quán (không phải lỗi schema), Coordinator nên xử lý thế nào? Nếu bỏ file thì vi phạm hard-gate "đủ 50 file"; nếu ghi nguyên với confidence cao thì đẩy output đáng ngờ vào bài nộp.
- **Các phương án đã cân nhắc:** (1) chỉ log, ghi nguyên như Policy trả về; (2) raise → rơi vào `_fallback_output` (confidence 0, mất hết thông tin đã tính); (3) giữ số liệu Policy nhưng hạ confidence + gắn cờ review.
- **Phương án đã chọn:** (3) — hạ `confidence` xuống `VERIFY_FAIL_CONFIDENCE = 0.1`, log thêm `verify_fail_flagged`, vẫn ghi file.
- **Lý do:** Vẫn đủ 50 file (hard-gate), không phá số liệu tất định của Policy Agent (Verifier không được "sửa" quyết định — đúng ranh giới trách nhiệm), nhưng đánh dấu rõ case cần người review; `0.1` trùng ngưỡng fallback của Policy nên nhóm có một tiêu chí lọc thống nhất "case đáng ngờ".
- **Bằng chứng quyết định phù hợp:** `pytest` vẫn `17 passed, 1 xfailed` sau thay đổi; EC_001 (verify_pass) không bị ảnh hưởng; quyết định ghi vào `architecture.md` mục 6.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Trong `coordinator._process` còn 2 `# TODO` chưa chốt: (a) `seller_ids` trong `affected_entities` nên là seller vi phạm hay tất cả seller của đơn; (b) hành vi khi `verify_fail`. Để nguyên thì tài liệu và code lệch nhau, người chấm không biết hệ thống thật làm gì.
- **Bước tái hiện:** `grep -n "TODO (Vai tro 5" src/agents/coordinator.py`.
- **Nguyên nhân gốc:** Đây là quyết định tích hợp cross-role chưa được chốt, không phải bug runtime.
- **Cách xử lý:** Chốt (a) = `late_seller_ids` (chỉ seller bị quy trách nhiệm, nhất quán với `responsible_parties`; rule khác → `[]`); chốt (b) như mục 5. Thay 2 khối TODO bằng ghi chú "ĐÃ CHỐT" trong code và ghi cả 2 vào `architecture.md` mục 6.
- **Cách xác minh sau khi sửa:** `python -m pytest -q` → `17 passed, 1 xfailed`; `python scripts/run_pipeline.py EC_001` chạy lại OK.
- **Điều học được:** Trong hệ multi-agent, ranh giới "ai được sửa số liệu của ai" quan trọng ngang thuật toán — Verifier chỉ gác cổng, Coordinator mới điều phối; tài liệu hóa quyết định ngay tại chỗ tránh drift giữa code và `architecture.md`.

### Blocker chưa xử lý xong

- **Phạm vi bị ảnh hưởng:** Chạy full 50 case + `validate_output.py` + `package_submission.py` (`submission.zip`).
- **Những gì đã loại trừ:** Không phải lỗi hạ tầng — hạ tầng đã xanh trên EC_001 và unit test.
- **Nguyên nhân:** 4 agent của Vai trò 1–4 còn `# TODO` (chưa implement logic so sánh ngày/đối soát/rule engine) nên 50 case sẽ rơi fallback thay vì kết quả đúng.
- **Bước tiếp theo:** Sau khi Role 1–4 merge, chạy `python scripts/run_pipeline.py` → `python scripts/validate_output.py` → `python scripts/package_submission.py`, sửa tới khi sạch.

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của tôi (bám đúng bài lab Multi-Agent A2A này):

1. Một case đi từ `input/EC_XXX.json` tới `output/EC_XXX.json` như thế nào?
2. Vì sao mọi field chấm điểm được tính tất định thay vì để LLM sinh?
3. Verifier chặn những rủi ro hard-gate nào trước khi ghi file?
4. Vì sao chỉ 3 agent dữ liệu được đọc CSV, còn Policy/Verifier thì không?
5. Bài nộp được xem là hợp lệ dựa trên artifact và điều kiện nào?

**Câu trả lời:**

1. Coordinator đọc `claimed_order_id`, gọi 3 agent dữ liệu (Order&Seller, Payment, Delivery) — mỗi agent trả facts + evidence ID; gộp facts đưa qua Policy Agent (`EC_POLICY_V1`, rule đầu tiên khớp thắng) ra `primary_issue`/cause/refund/action; build `CaseOutput` rồi đưa qua Verifier; pass thì ghi file, mỗi bước append 1 dòng vào `trace.jsonl`.
2. Vì cả 6 thành phần điểm (mục 8) đều suy ra được 100% từ `data/*.csv` + bảng policy. Để LLM đoán số/ID sẽ hallucinate và thành hard-gate; LLM chỉ viết tường thuật cho trace.
3. JSON không parse/sai tên file; thiếu field/sai kiểu schema; `evidence_id` trỏ tới order/item/payment/seller không tồn tại hoặc sai định dạng; `confidence` ngoài [0,1] hay vượt giới hạn số lượng; và bất biến "đủ 50 file" (fallback thay vì bỏ trống).
4. Để mọi evidence đều truy vết được về nguồn handoff: Policy/Verifier chỉ làm việc trên facts + evidence ID đã được agent nguồn cấp, không tự mở CSV "tra thêm" — tránh evidence không có nguồn gốc trong luồng A2A.
5. Repo giữ nguyên tên, đủ source + `output/` (50 file) + `architecture.md` + báo cáo cá nhân + `trace.jsonl` + `metadata.json`; `python scripts/validate_output.py` sạch; `submission.zip` **chỉ chứa `output/`** (không kèm source/`.env`).

## 8. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng (full 50 case còn chờ Role 1–4).
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Đỗ Tuấn Sơn
**Ngày xác nhận:** 2026-08-05
