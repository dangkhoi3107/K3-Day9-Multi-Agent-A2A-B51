# Báo cáo cá nhân — Day 9: Multi-Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Vi Minh Hiển |
| MSSV | 2A202601743 |
| Khóa/Lớp | K3 |
| Vai trò chính | Vai trò 3 — Delivery Agent |
| Ngày hoàn thành | 2026-08-05 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Delivery Agent | `src/agents/delivery_agent.py::investigate()` | `order_id` | `DeliveryFacts` gồm trạng thái giao hàng, kết luận đúng/trễ hạn và evidence | Hoàn thành |
| Unit test Delivery Agent | `tests/test_delivery_agent.py` | Các order thật trong bộ 50 case | Kiểm chứng ba trạng thái chưa giao, đúng hạn và giao trễ | Hoàn thành |

Delivery Agent chỉ xác định sự kiện giao hàng có trễ so với ngày dự kiến hay không. Agent không tự kết luận seller hoặc đơn vị logistics chịu trách nhiệm; quyết định này thuộc Policy Agent sau khi kết hợp `late_to_customer` với `late_seller_ids` từ Order & Seller Agent.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Rà soát trạng thái của 50 order đầu vào | Policy Agent — Vai trò 4 | Xác nhận chỉ có `delivered` (34), `canceled` (8) và `unavailable` (8); không phát hiện trạng thái lạ |
| Xác nhận contract handoff | Policy Agent — Vai trò 4 | `late_to_customer` trả `True`, `False` hoặc `None`; Policy Agent có thể dùng trực tiếp cho rule 3, 4 và 6 |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Cài đặt so sánh ngày giao thực tế và ngày giao dự kiến | `src/agents/delivery_agent.py::investigate()` | Trả `True` khi giao sau hạn, `False` khi giao đúng/trước hạn, `None` khi chưa đủ dữ liệu | `python -m pytest tests/test_delivery_agent.py -v` |
| Thay dữ liệu test placeholder bằng order thật | `tests/test_delivery_agent.py` | Dùng các case EC_001, EC_002 và EC_003 | Đối chiếu `input/*.json` với `data/olist_orders_dataset.csv` |
| Bổ sung test đúng hạn và trễ hạn | `tests/test_delivery_agent.py` | Tổng cộng 5 test của Delivery Agent đều pass | Kết quả: `5 passed` |
| Kiểm tra regression toàn repo | Toàn bộ thư mục `tests/` | Không phát sinh lỗi do Delivery Agent | Kết quả: `19 passed, 1 xfailed`; xfail thuộc Policy Agent chưa triển khai, ngoài phạm vi Vai trò 3 |

Output cụ thể của phần việc là field `late_to_customer` đáng tin cậy để Policy Agent áp dụng:

- `EC_001` — order `e2a03ccf5ea816036608b2d8c3ab8e60`: giao sau estimated date, trả `True`.
- `EC_002` — order `8067c5e4834f3c0a3c8a4e921d65c5b1`: giao trước estimated date, trả `False`.
- `EC_003` — order `71303d7e93b399f5bcd537d124c0bcfa`: chưa có ngày giao cho khách, trả `None`.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline cần một fact khách quan cho biết đơn hàng có được giao trễ so với cam kết hay không. Fact này là điều kiện bắt buộc của rule 3 (`late_delivery_seller`), rule 4 (`late_delivery_logistics`) và rule 6 (`unsupported_late_claim`). Nếu ngày giao bị rỗng mà hệ thống tự coi là đúng hạn hoặc trễ hạn, Policy Agent có thể đưa ra kết luận sai và tạo evidence không được dữ liệu hỗ trợ.

### Cách triển khai

`DataStore` đọc cột ngày từ CSV và chuẩn hóa thành `pd.Timestamp` hoặc `pd.NaT`. Trong `investigate(order_id)`, Delivery Agent thực hiện:

1. Tra order bằng `DataStore.instance().get_order(order_id)`.
2. Nếu order không tồn tại, trả `delivered=False`, `late_to_customer=None` và không tạo evidence giả.
3. Xác định `delivered` bằng `pd.notna(order_delivered_customer_date)`.
4. Chỉ so sánh khi đã giao và `order_estimated_delivery_date` có giá trị.
5. Gán `late_to_customer = delivered_customer_date > estimated_date`.
6. Nếu chưa giao hoặc thiếu estimated date, giữ `late_to_customer=None` để biểu diễn “chưa đủ dữ liệu”.
7. Với order tồn tại, bàn giao evidence `order:<order_id>` cho Coordinator.

Agent cũng chuyển tiếp `order_delivered_carrier_date` dưới dạng `delivered_carrier_date`, nhưng không dùng field này để tự quy trách nhiệm. Policy Agent chịu trách nhiệm kết hợp fact giao cho khách với fact seller bàn giao cho carrier.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | `order_id: str` từ `customer_request.claimed_order_id` |
| Output | `DeliveryFacts(order_id, delivered, late_to_customer, delivered_carrier_date, evidence_ids)` |
| Module phụ thuộc | `src/data_access.py`, `src/evidence.py`, pandas |
| Module sử dụng output | `src/agents/coordinator.py`, sau đó `src/agents/policy_agent.py` |
| Điều kiện lỗi cần xử lý | Order không tồn tại; ngày giao khách rỗng; ngày dự kiến rỗng |

### Cách xác minh

```powershell
& "C:\Users\Asus\miniconda3\python.exe" -m pytest tests\test_delivery_agent.py -v -p no:cacheprovider
```

- **Kết quả mong đợi:** 5 test pass; không kết luận đúng/trễ hạn khi order chưa giao.
- **Kết quả thực tế:** `5 passed`.
- **Artifact/log:** `tests/test_delivery_agent.py`; dữ liệu kiểm chứng tại `input/EC_001.json`, `input/EC_002.json`, `input/EC_003.json` và `data/olist_orders_dataset.csv`.

Kiểm tra regression:

```powershell
& "C:\Users\Asus\miniconda3\python.exe" -m pytest -v -p no:cacheprovider
```

- **Kết quả thực tế:** `19 passed, 1 xfailed`.
- **Ghi chú:** test xfail thuộc rule 1 của Policy Agent chưa được Vai trò 4 triển khai, không phải lỗi Delivery Agent.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần biểu diễn trạng thái order chưa có `order_delivered_customer_date`.
- **Các phương án đã cân nhắc:** Gán `late_to_customer=False`; hoặc sử dụng giá trị ba trạng thái `True/False/None`.
- **Phương án đã chọn:** Giữ `None` khi chưa giao hoặc chưa đủ ngày để so sánh.
- **Lý do:** `False` mang nghĩa đã xác minh đơn không trễ, trong khi ngày giao rỗng chỉ cho biết chưa đủ bằng chứng. Dùng `None` giúp Policy Agent phân biệt rõ “đúng hạn” và “không thể đánh giá”, tránh bác bỏ khiếu nại dựa trên dữ liệu thiếu.
- **Bằng chứng quyết định phù hợp:** Test `test_not_delivered_never_has_late_verdict` xác minh order EC_003 trả `delivered=False` và `late_to_customer=None`; toàn bộ test Delivery Agent pass.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `ImportError: DLL load failed while importing hashtable: An Application Control policy has blocked this file.`
- **Lệnh tái hiện:** `python -m pytest tests/test_delivery_agent.py -v` khi Python trỏ vào `.venv` hoặc bản Python trong `AppData` có pandas cài từ PyPI.
- **Nguyên nhân gốc:** Windows Application Control chặn binary extension của pandas trong môi trường Python đó; lỗi xảy ra khi import pandas, trước khi pytest chạy test Delivery Agent.
- **Cách xử lý:** Dùng bản Python Miniconda và pandas cài từ Conda, gọi đúng interpreter thay vì Python đang bị block.
- **Cách xác minh sau khi sửa:** Chạy lệnh pytest bằng `C:\Users\Asus\miniconda3\python.exe`; kết quả `5 passed` cho test riêng và `19 passed, 1 xfailed` cho full suite.
- **Điều học được:** Cần phân biệt lỗi môi trường import dependency với lỗi logic của agent; luôn xác nhận chính xác interpreter bằng đường dẫn hoặc `where.exe python` trước khi kết luận code sai.

## 7. Hiểu biết về luồng end-to-end

1. Mỗi file `input/EC_XXX.json` cung cấp `case_id`, nội dung khiếu nại và `claimed_order_id`. Coordinator đọc input rồi giao cùng order ID cho Order & Seller Agent, Payment Agent và Delivery Agent.
2. Ba agent dữ liệu truy cập `DataStore` dùng chung và bàn giao facts kèm evidence. Delivery Agent cung cấp `late_to_customer`; Order & Seller Agent cung cấp trạng thái order, item, seller và seller bàn giao muộn; Payment Agent cung cấp tổng payment và kết quả đối soát.
3. Policy Agent ghép các facts theo đúng thứ tự ưu tiên EC_POLICY_V1. Với giao trễ, `late_to_customer=True` kết hợp seller bàn giao muộn để phân biệt trách nhiệm seller với logistics. Khi `late_to_customer=False` và payment khớp, rule 6 có thể bác claim giao trễ.
4. Coordinator dựng output gồm assessment, affected entities, root cause, evidence, tài chính và action. Verifier kiểm tra schema, giới hạn số lượng, phép tính tiền và sự tồn tại của evidence trước khi cho ghi `output/EC_XXX.json`.
5. Mỗi handoff được ghi vào `logging/trace.jsonl`. Chạy cùng input, dataset và policy phải tạo cùng facts nghiệp vụ; tính đúng được xác nhận bằng unit test, output validation và không có evidence giả.

Phần đóng góp của Delivery Agent nằm ở ranh giới giữa dữ liệu timestamp và rule nghiệp vụ: agent chỉ xác nhận sự kiện giao đúng/trễ/chưa xác định, không vượt quyền sang quy trách nhiệm hay quyết định refund.

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Vi Minh Hiển  
**Ngày xác nhận:** 2026-08-05
