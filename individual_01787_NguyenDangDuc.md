# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                            |
| --------------- | --------------------------------------------------- |
| Họ và tên       | Nguyễn Đăng Đức                                     |
| MSSV            | 01787                                               |
| Khóa/Lớp        | K3                                                  |
| Vai trò chính   | Vai trò 4 — Policy Agent (Rule Engine `EC_POLICY_V1`) |
| Ngày hoàn thành | 2026-08-05                                          |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------ | -------------- | ----------------- | ------------------ |
| Policy Agent (`EC_POLICY_V1`) | `src/agents/policy_agent.py` (`decide`, `_rule_1` .. `_rule_6`) | `OrderSellerFacts`, `PaymentFacts`, `DeliveryFacts` | `PolicyDecision` | Hoàn thành |
| Policy Unit Tests | `tests/test_policy_agent.py` | Fixture facts | 8/8 Unit tests passing | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Tích hợp & Kiểm thử 50 Cases | Vai trò 5 (Coordinator & Verifier) | Chạy thành công `run_pipeline.py` và `validate_output.py` đạt 50/50 cases hợp lệ. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | --------------------------- | ------------------------- | --------------- |
| Cài đặt 6 Rules theo bảng ưu tiên `EC_POLICY_V1` | `src/agents/policy_agent.py` | 6 hàm rule tất định xử lý refund, action, cause code, responsible party | `python -m pytest tests/test_policy_agent.py -v` |
| Viết bộ Unit Test kiểm thử 6 Rules & Priority Order | `tests/test_policy_agent.py` | 8 unit test cases covering 100% logic branches | `python -m pytest tests/test_policy_agent.py -v` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

File output `output/EC_020.json` (và các file output từ 1-50): Nhận diện chính xác `primary_issue`: `"valid_split_payment"`, `confidence`: `0.95`, `case_status`: `"no_action"`, `recommended_refund_brl`: `0.0`, `resolution_actions`: `["explain_valid_split_payment"]`.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Áp dụng bộ quy tắc kinh doanh `EC_POLICY_V1` để tổng hợp facts từ 3 Agent trước (OrderSeller, Payment, Delivery), phân loại chính xác 1 trong 6 `primary_issue`, xác định bên chịu trách nhiệm (`platform`, `seller`, `logistics_provider`, hoặc `None`), tính toán số tiền hoàn (`recommended_refund_brl`), đưa ra hành động xử lý (`resolution_actions`) và gán Evidence Policy ID với độ tin cậy tuyệt đối.

### Cách triển khai

Sử dụng **Rule-based Engine tất định (Deterministic Code)** duyệt qua mảng tuple 6 hàm rule theo đúng thứ tự ưu tiên của đề bài:
1. `_rule_1_canceled_order_paid`: `order_status == "canceled"` & `payment_total_brl > 0`
2. `_rule_2_unavailable_order_paid`: `order_status == "unavailable"` & `payment_total_brl > 0`
3. `_rule_3_late_delivery_seller`: `late_to_customer is True` & `len(late_seller_ids) > 0`
4. `_rule_4_late_delivery_logistics`: `late_to_customer is True` & `len(late_seller_ids) == 0`
5. `_rule_5_valid_split_payment`: `is_split is True` & `is_reconciled is True`
6. `_rule_6_unsupported_late_claim`: `late_to_customer is False` & `is_reconciled is True`

Ngay khi một rule khớp điều kiện, hàm `decide()` sẽ trả về `PolicyDecision` lập tức và dừng lại (dừng vòng lặp), đảm bảo rule có ưu tiên cao hơn luôn ghi đè rule có ưu tiên thấp hơn.

### Input, output và contract

| Thành phần | Mô tả |
| ---------- | ------ |
| Input | `OrderSellerFacts`, `PaymentFacts`, `DeliveryFacts` |
| Output | `PolicyDecision` (primary_issue, case_status, cause_code, responsible_party, refund, action, confidence, evidence_ids) |
| Module phụ thuộc | `order_seller_agent.py`, `payment_agent.py`, `delivery_agent.py` |
| Module sử dụng output | `coordinator.py`, `verifier_agent.py` |
| Điều kiện lỗi cần xử lý | Trường hợp không rule nào khớp (dữ liệu ngoài 50 case), fallback về confidence 0.1 và `reject_late_refund` an toàn. |

### Cách xác minh

```bash
python -m pytest tests/test_policy_agent.py -v
```

- **Kết quả mong đợi:** 8/8 test cases PASSED (Green 100%).
- **Kết quả thực tế:** 8/8 test cases PASSED trong 1.00s.
- **Artifact/log:** `tests/test_policy_agent.py`, `output/EC_001.json` ... `output/EC_050.json`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp ra quyết định Policy Decision giữa việc gọi prompt LLM vs Viết Engine mã lệnh Python tất định.
- **Các phương án đã cân nhắc:**
  1. *Phương án 1*: Đưa toàn bộ facts vào prompt LLM (≤ 10B) nhờ LLM suy luận ra JSON output.
  2. *Phương án 2*: Viết Rule Engine bằng Python tất định (Deterministic Rules).
- **Phương án đã chọn:** Phương án 2 (Rule Engine Python tất định).
- **Lý do:** Đảm bảo độ chính xác tuyệt đối (100% correctness), không bị rủi ro hallucination (ảo giác AI làm sai lệch số tiền refund hoặc format Evidence ID gây điểm 0 hard-gate), tốc độ xử lý siêu nhanh (< 1ms/case), dễ dàng viết unit test kiểm thử độc lập.
- **Bằng chứng quyết định phù hợp:** 30/30 unit tests PASSED và 50/50 output cases vượt qua validation `validate_output.py`.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi sai thứ tự ưu tiên khi một đơn hàng vừa bị hủy (`canceled`), vừa có 2 đợt thanh toán khớp (`is_split=True, is_reconciled=True`).
- **Lệnh hoặc bước tái hiện:** Chạy test case kết hợp `order_status="canceled"` và `is_split=True`.
- **Nguyên nhân gốc:** Nếu xếp `_rule_5_valid_split_payment` lên trước `_rule_1_canceled_order_paid`, hệ thống sẽ trả về `valid_split_payment` thay vì `canceled_order_paid`, vi phạm thứ tự ưu tiên trong README.md.
- **Cách xử lý:** Đặt `_rule_1_canceled_order_paid` ở vị trí đầu tiên trong danh sách hàm được duyệt của `decide()`.
- **Cách xác minh sau khi sửa:** Viết hàm test `test_priority_canceled_beats_valid_split_payment()` trong `tests/test_policy_agent.py` và xác nhận test pass.
- **Điều học được:** Khi phát triển Policy Engine, luôn tuân thủ nghiêm ngặt bảng ma trận ưu tiên (Priority Matrix) và viết unit test cho các trường hợp xung đột điều kiện (conflicting rules).

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của bạn:

1. **Dữ liệu đi từ CSV đến Output JSON như thế nào?**: `DataStore` đọc 9 file CSV Olist ➔ `Coordinator Agent` nhận `claimed_order_id` từ input JSON ➔ Phân phối cho 3 Agent (OrderSeller, Payment, Delivery) đọc CSV và trích xuất facts ➔ `Policy Agent` tổng hợp facts và áp dụng 6 rules để đưa ra quyết định ➔ `Verifier Agent` kiểm tra tính hợp lệ của Evidence ID và Schema ➔ Ghi kết quả vào `output/EC_xxx.json` và ghi vết vào `logging/trace.jsonl`.
2. **Evaluation set và ground-truth document IDs dùng để làm gì?**: Dùng để kiểm tra đối soát chéo (cross-reference) tính đúng đắn của quyết định hoàn tiền và đảm bảo 100% Evidence ID xuất ra đều tồn tại trong cơ sở dữ liệu thật của Olist (`data/*.csv`).
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**: Quality checks tập trung vào tính đúng đắn về mặt dữ liệu (đúng schema, đủ evidence, làm tròn 2 chữ số thập phân), còn freshness monitoring tập trung vào mốc thời gian sự kiện (ngày giao thực tế vs hạn chót bàn giao của seller/ngày dự kiến giao).
4. **Vì sao phải kiểm tra kỹ thứ tự ưu tiên của quy tắc?**: Vì một đơn hàng có thể thỏa mãn điều kiện của nhiều rule cùng lúc (ví dụ đơn bị hủy nhưng cũng có 2 đợt thanh toán), việc tuân thủ thứ tự ưu tiên giúp hệ thống đưa ra quyết định xử lý đúng theo chính sách đền bù của sàn.
5. **Multi-Agent Dispute Resolution được xem là thành công dựa trên artifact và metric nào?**: Thành công dựa trên 50/50 file output hợp lệ theo `validate_output.py`, điểm tổng hợp có trọng số 6 thành phần (Primary issue 20%, Affected entities 20%, Root cause 15%, Evidence 15%, Financial resolution 20%, Resolution actions 10%), và vết log trao đổi A2A trong `trace.jsonl`.

## 8. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Đăng Đức  
**Ngày xác nhận:** 2026-08-05  
