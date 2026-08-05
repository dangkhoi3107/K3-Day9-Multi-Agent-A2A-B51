# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                                              |
| --------------- | ---------------------------------------------------------------------- |
| Họ và tên       | Phạm Nguyễn Đăng Khôi                                                   |
| MSSV            | 2A202601243                                                               |
| Khóa/Lớp        | K3 / B51                                                               |
| Vai trò chính   | Vai trò 1 — Order & Seller Agent, kiêm Leader (hạ tầng, tích hợp, kiểm chứng) |
| Ngày hoàn thành | 2026-08-05                                                             |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Order & Seller Agent | `src/agents/order_seller_agent.py::investigate()` | `claimed_order_id` | `OrderSellerFacts` (order_status, items, `late_seller_ids`, item/freight total, evidence IDs) | Hoàn thành |
| Test Order & Seller Agent | `tests/test_order_seller_agent.py` | order_id thật lấy từ chính 50 case (`scripts/find_test_fixtures.py`) | 5 test: seller trễ hạn, seller đúng hạn, order không có item row | Hoàn thành |
| Hạ tầng dùng chung (khởi tạo) | `src/config.py`, `src/schemas.py`, `src/evidence.py`, `src/data_access.py`, `src/tracing.py`, `src/llm_client.py`, khung `coordinator.py`/`verifier_agent.py` | CSV `data/`, README mục 3/5/6 | Hợp đồng schema Pydantic, data loader, evidence-ID builder, trace writer | Hoàn thành |
| Scripts vận hành | `scripts/run_pipeline.py`, `scripts/validate_output.py`, `scripts/package_submission.py`, `scripts/find_test_fixtures.py` | `input/`, `output/`, `data/` | Chạy pipeline, tự kiểm output, đóng gói zip, tìm fixture test thật cho cả nhóm | Hoàn thành |
| Tích hợp 4 nhánh vào `main` | `git merge` (`son`, `TranTrung`, `Khoi`, `dangduc`) | 4 nhánh làm việc độc lập | `main` chạy được, không conflict, `pytest` xanh sau mỗi lần merge | Hoàn thành |
| Kiểm chứng độc lập 50 case | Script tự viết riêng (không dùng lại code repo), so với `output/*.json` | `data/*.csv`, 50 `input/EC_XXX.json` | 0 sai lệch giữa đáp án tự tính và output thật của Vai trò 4 | Hoàn thành |
| Mở rộng test Verifier + demo | `tests/test_verifier_agent.py` (+9 test), demo corruption (không commit) | `CaseOutput` cố tình sai theo nhiều kiểu | 13/13 test pass; demo bắt đúng 6/6 lỗi cố tình tạo | Hoàn thành |
| Đóng gói nộp bài | `scripts/package_submission.py`, `submission.zip`, `submission_full.zip` | `output/` đã validate sạch | 2 file zip đúng cấu trúc, đã kiểm tay số entry | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Phát hiện + sửa input bị đặt lệch thư mục (`input/input/*.json` thay vì `input/*.json`) ngay sau khi Checkpoint 1 công bố | Cả nhóm | 50 file chuyển đúng vị trí, validate lại đủ 50/50, không case nào bị pipeline bỏ sót |
| Phát hiện thư mục `archive/` (bản Kaggle tải trùng `data/`, ~121MB) không nên commit | Cả nhóm | Thêm vào `.gitignore`, tránh phình repo dùng chung |
| Review kỹ code Delivery Agent (Vai trò 3, không thuộc phần mình) trước khi merge | Vai trò 3 | Đối chiếu tay 3 fixture test với `orders.csv` gốc, xác nhận đúng trước khi cho vào `main` |
| Review + kiểm chứng độc lập Policy Agent (Vai trò 4) trước khi merge | Vai trò 4 (dangduc) | Tự viết lại thuật toán 6 rule để so sánh, không chỉ đọc code — phát hiện 0 sai lệch trên 50 case |
| Từ chối yêu cầu chỉnh sai lệch output có chủ đích để "chỉ đạt 95 điểm" | Cả nhóm (tính toàn vẹn bài nộp) | Giải thích rõ rủi ro làm giả kết quả nộp bài, đề xuất hướng hợp lệ hơn (test verifier) và đã thực hiện hướng đó |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Tính `late_seller_ids` từ so sánh `order_delivered_carrier_date` với `shipping_limit_date` từng item | `order_seller_agent.py::investigate()` | Seller vi phạm được đưa đúng vào `affected_entities.seller_ids` và evidence | `pytest tests/test_order_seller_agent.py -v` → 5/5 pass; chạy thật `EC_022.json` (case chứa seller trễ hạn nằm trong 50 case thật) |
| Merge 4 nhánh không sửa tay conflict | `git merge-tree` trước, `git merge` sau | `main` có đủ 5 agent, `pytest` 30 passed / 0 fail / 0 xfail sau merge cuối | `git log --oneline --graph`, `python -m pytest` |
| Tự tính lại đáp án đúng cho 50 case từ CSV gốc (độc lập với code repo) | Script Python viết riêng trong phiên làm việc | 0 sai lệch về `primary_issue`, `recommended_refund_brl`, `resolution_actions`, `seller_ids` so với output của Vai trò 4 | So khớp từng case, in ra danh sách mismatch (rỗng) |
| Mở rộng test Verifier bắt evidence bịa (item/payment/seller), số tiền không khớp action, vượt giới hạn schema | `tests/test_verifier_agent.py` | 13/13 test pass | `pytest tests/test_verifier_agent.py -v` |
| Đóng gói `submission.zip` (chỉ `output/`, đúng README) và `submission_full.zip` (4 phần, dự phòng) | `scripts/package_submission.py` | 2 file zip đúng số entry (50 và 53) | Đọc lại `zipfile.namelist()` sau khi tạo |

Output cụ thể do phần việc của tôi tạo ra và xác minh: `output/EC_022.json` — case thật duy nhất trong 50 case ban đầu thể hiện rõ `late_seller_ids` hoạt động đúng (seller `02d35243ea2e497335cd0f076b45675d` xuất hiện trong cả `affected_entities.seller_ids` và `evidence_ids`), cùng toàn bộ `logging/trace.jsonl` của lượt chạy full 50 case cuối cùng (350 dòng, đúng 7 sự kiện × 50 case, không lẫn log chạy thử của ai).

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Hai lớp vấn đề khác nhau: (1) Order & Seller Agent phải xác định seller nào bàn giao trễ cho đơn vị vận chuyển — dữ liệu chỉ có 1 mốc `order_delivered_carrier_date` cho cả đơn nhưng `shipping_limit_date` là riêng từng item, nên phải so đúng theo từng item chứ không so 1 lần cho cả đơn; (2) với vai trò tích hợp, vấn đề là ghép 4 phần việc làm độc lập (đôi khi trên nhánh xuất phát từ các thời điểm `main` khác nhau) thành 1 hệ thống chạy đúng, mà không có "đáp án chuẩn" nào để đối chiếu ngoài chính README.

### Cách triển khai

- `late_seller_ids`: với mỗi item của đơn, nếu `order_delivered_carrier_date` (đã kiểm `pd.notna`) lớn hơn `shipping_limit_date` của item đó thì seller của item bị tính là vi phạm; đơn chưa giao/bị canceled có `carrier_date` rỗng nên không bị tính nhầm là "đúng hạn".
- Tích hợp: trước khi merge bất kỳ nhánh nào, chạy `git merge-tree --write-tree` (không đụng working tree, an toàn dù đang có việc dở) để biết trước có conflict không; sau khi merge, không chỉ tin exit code mà đọc lại nội dung file quan trọng (`TASKS.md`, `architecture.md`) để chắc merge tự động không âm thầm làm mất thông tin của bên nào.
- Kiểm chứng: thay vì chỉ đọc code Policy Agent và tin test đã viết sẵn, tôi viết lại **từ đầu** một bản tính 6 rule EC_POLICY_V1 hoàn toàn độc lập (không import code trong repo), chạy trên cả 50 case thật rồi so với `output/*.json` — đây là cách duy nhất phát hiện được nếu code và test cùng sai giống nhau theo 1 kiểu.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | `claimed_order_id` (Order & Seller Agent); toàn bộ `output/*.json` + `data/*.csv` (vai trò kiểm chứng) |
| Output | `OrderSellerFacts` cho agent; báo cáo mismatch (rỗng) cho kiểm chứng độc lập |
| Module phụ thuộc | `src.data_access.DataStore`, `src.evidence` |
| Module sử dụng output | `payment_agent.py` (nhận `item_total_brl`/`freight_total_brl`), `policy_agent.py` (nhận `late_seller_ids`), `coordinator.py` |
| Điều kiện lỗi cần xử lý | Order không tồn tại → trả rỗng; order không có item row → `items=[]` (README mục 6); ngày rỗng (NaT) không được suy diễn thành "đúng hạn" |

### Cách xác minh

```bash
python -m pytest -q
python scripts/run_pipeline.py EC_022
python scripts/validate_output.py
```

- **Kết quả mong đợi:** toàn bộ test xanh; `EC_022.json` có `seller_ids` đúng seller vi phạm; `output/` đủ 50 file hợp lệ.
- **Kết quả thực tế:** `39 passed` (thời điểm cuối, gồm cả 9 test Verifier mở rộng); `EC_022.json` đúng như mong đợi; `validate_output.py` báo "OK - du 50 file, dung schema, evidence deu tra cuu duoc trong data/".
- **Artifact/log:** `output/EC_022.json`, `logging/trace.jsonl`, `TASKS.md` (đã cập nhật theo từng mốc thật, không phải viết trước rồi để nguyên).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Trước khi merge Policy Agent (Vai trò 4) — module quyết định trực tiếp ~90% trọng số điểm — cần biết chắc 6 rule cài đúng cho cả 50 case thật, không chỉ 8 unit test dùng facts giả.
- **Các phương án đã cân nhắc:** (1) chỉ đọc code + chạy test có sẵn rồi merge nếu xanh; (2) chọn vài case mẫu đối chiếu tay; (3) viết lại toàn bộ logic 6 rule một lần nữa, hoàn toàn độc lập, chạy trên cả 50 case thật rồi so từng field với output thật.
- **Phương án đã chọn:** (3).
- **Lý do:** Phương án (1) không phát hiện được lỗi hệ thống nếu code và test cùng sai giống nhau; (2) chỉ phủ được vài case, có thể bỏ sót case biên. Viết lại độc lập là cách duy nhất tạo ra một nguồn sự thật thứ hai, tách biệt hoàn toàn khỏi code đang review — đúng tinh thần "grounding" của cả bài lab.
- **Bằng chứng quyết định phù hợp:** So khớp cả 50 case, 0 mismatch về `primary_issue`/refund/action/seller; đồng thời phát hiện toàn bộ 50 case đều khớp đúng 1 trong 6 rule (0 case rơi vào fallback), xác nhận bộ 50 case thật đúng như README mô tả là "không có tình huống mơ hồ".

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Ngay sau khi 50 file input thật được đưa vào máy (đúng thời điểm Checkpoint 1), `input/` vẫn báo trống khi pipeline chạy thử.
- **Lệnh hoặc bước tái hiện:** `ls input/` → chỉ thấy `.gitkeep`; kiểm sâu hơn phát hiện 50 file thật nằm ở `input/input/EC_XXX.json`.
- **Nguyên nhân gốc:** File input được giải nén từ gói tải về nhưng đặt lồng thêm 1 cấp thư mục `input/` bên trong `input/` có sẵn của repo, thay vì giải nén đè lên đúng vị trí.
- **Cách xử lý:** Di chuyển toàn bộ 50 file lên đúng `input/`, xóa thư mục `input/input/` rỗng còn sót lại (kể cả `.gitkeep`).
- **Cách xác minh sau khi sửa:** Viết script kiểm tra nhanh — đúng 50 file `EC_001.json`–`EC_050.json`, parse JSON hợp lệ, `policy_version` đúng `EC_POLICY_V1`, cả 50 `claimed_order_id` đều tồn tại thật và phân biệt nhau trong `orders.csv`.
- **Điều học được:** Nên tự động hoá bước kiểm tra input ngay khi nhận được thay vì giả định vị trí đúng — lỗi đặt sai thư mục kiểu này im lặng (không crash, chỉ "không tìm thấy gì để chạy"), rất dễ bị bỏ qua nếu không kiểm tra chủ động ngay từ đầu.

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của tôi (bám đúng bài lab Multi-Agent A2A này):

1. Một case đi từ `input/EC_XXX.json` tới `output/EC_XXX.json` như thế nào?
2. Vì sao mọi field chấm điểm được tính tất định thay vì để LLM sinh?
3. Verifier chặn những rủi ro hard-gate nào trước khi ghi file?
4. Vì sao chỉ 3 agent dữ liệu được đọc CSV, còn Policy/Verifier thì không?
5. Bài nộp được xem là hợp lệ dựa trên artifact và điều kiện nào?

**Câu trả lời:**

1. Coordinator đọc `claimed_order_id` từ input, gọi song song 3 agent dữ liệu (Order & Seller, Payment, Delivery) — mỗi agent trả về facts kèm evidence ID truy vết được về `data/*.csv`. Facts được gộp lại và đưa qua Policy Agent, nơi áp dụng đúng thứ tự 6 rule của `EC_POLICY_V1` (rule đầu tiên khớp điều kiện là thắng, dừng ngay không xét tiếp) để ra `primary_issue`, root cause, refund và action. Kết quả được build thành `CaseOutput` và bắt buộc đi qua Verifier trước khi ghi file; mỗi bước đều append 1 dòng vào `logging/trace.jsonl`.
2. Vì cả 6 thành phần chấm điểm ở README mục 8 đều tính được 100% từ dữ liệu CSV và bảng policy — không có phần nào cần suy luận ngôn ngữ tự nhiên. Để LLM tự sinh số tiền hay evidence ID sẽ có rủi ro hallucinate, mà evidence bịa là nguyên nhân trực tiếp dẫn tới hard-gate. Model ≤10B chỉ dùng để viết tường thuật cho trace, không bao giờ quyết định con số hay ID trong output cuối.
3. Verifier kiểm: schema (thiếu field, sai kiểu, vượt giới hạn số lượng, `confidence` ngoài [0,1]); evidence ID sai định dạng hoặc trỏ tới order/item/payment/seller không có thật trong `data/`; số tiền không khớp công thức của action đã chọn (vd `issue_full_refund` nhưng refund khác tổng payment). Ngoài ra Coordinator tự đảm bảo bất biến "không bao giờ thiếu file" — case lỗi bất kỳ đâu vẫn ghi ra 1 JSON hợp lệ với confidence thấp thay vì bỏ trống, vì thiếu 1/50 file cũng là một dạng hard-gate.
4. Vì đó là ranh giới trách nhiệm giữ cho evidence luôn truy vết được đúng nguồn của luồng A2A: 3 agent dữ liệu là nơi duy nhất "chạm" vào CSV gốc và sinh evidence ID; Policy Agent chỉ suy luận trên facts đã có evidence kèm theo, Verifier chỉ đối chiếu chứ không tự tra thêm dữ liệu mới. Nếu để Policy/Verifier tự mở CSV, evidence có thể xuất hiện mà không qua đúng handoff nào, phá vỡ tính kiểm chứng được của chuỗi agent.
5. Repo (giữ nguyên tên) phải có đủ source code, `output/` đúng 50 file, `architecture.md`, `logging/trace.jsonl`, `logging/metadata.json` và báo cáo cá nhân từng người, tất cả đã commit trước khi nộp. `python scripts/validate_output.py` phải sạch (đúng 50 file, đúng schema, evidence tồn tại thật). File zip nộp qua form theo README repo **chỉ chứa `output/`** — không kèm source code hay `.env`.

## 8. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Phạm Nguyễn Đăng Khôi
**Ngày xác nhận:** 2026-08-05
