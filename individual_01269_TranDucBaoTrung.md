# Member Role Report - Day 9: Multi Agent A2A

## 1. Thong tin ca nhan

| Thong tin | Noi dung |
| --- | --- |
| Ho va ten | Tran Duc Bao Trung |
| MSSV | 01269 |
| Khoa/Lop | K3 |
| Vai tro chinh | Role 2 - Payment Agent |
| Ngay hoan thanh | 2026-08-05 |

## 2. Vai tro va pham vi cong viec

### Phan viec so huu

| Module/deliverable | File/ham phu trach | Input nhan vao | Output ban giao | Trang thai |
| --- | --- | --- | --- | --- |
| Payment Agent review | `src/agents/payment_agent.py::investigate()` | `order_id`, `item_total_brl`, `freight_total_brl` | `PaymentFacts` gom payment rows, tong payment, co split payment, trang thai reconciled va evidence IDs | Hoan thanh |
| Payment Agent tests | `tests/test_payment_agent.py` | Order ID that trong Olist payments/items CSV | 2 test moi cho split payment khop va split payment lech | Hoan thanh |
| Ghi chu quyet dinh tolerance rule 6 | `architecture.md` muc 6 | Yeu cau can thong nhat voi Role 4 | De xuat dung lai `0.10 BRL` qua `UNSUPPORTED_CLAIM_TOLERANCE_BRL`, cho Role 4 confirm | Mot phan |
| Cap nhat task tracking | `TASKS.md` | Tien do Role 2 | Tick cac muc doc lap da xong, giu muc phu thuoc Role 4 o trang thai chua xong | Hoan thanh |

### Viec ho tro ngoai pham vi chinh

| Hoat dong | Thanh vien/module duoc ho tro | Ket qua |
| --- | --- | --- |
| Ghi ro dependency voi Policy Agent | Role 4 - Policy Agent | `architecture.md` co note Role 2 de xuat tolerance `0.10 BRL` cho rule 6, nhung van de Role 4 chot cuoi |

## 3. Ket qua theo vai tro

| Nhiem vu da thuc hien | File/ham/artifact lien quan | Ket qua ban giao | Cach xac minh |
| --- | --- | --- | --- |
| Doc lai cong thuc doi soat payment | `src/agents/payment_agent.py::investigate()` | Xac nhan agent tinh `payment_total_brl = sum(payment_value)`, `is_split = len(payments) >= 2`, `is_reconciled` neu lech voi item+freight khong qua `0.10 BRL` | Review code va doi chieu voi README rule 5 |
| Viet test split payment hop le | `tests/test_payment_agent.py::test_two_reconciled_payments_is_valid_split()` | Order `0016dfedd97fc2950e388d2971d718c7` co 2 payment, tong payment `70.55`, tong item+freight `70.55`, reconciled | `python -m pytest tests/test_payment_agent.py -v` |
| Viet test split payment lech | `tests/test_payment_agent.py::test_two_mismatched_payments_is_not_reconciled()` | Order `b38b3526b8b8fdc807e8a0a42ab78573` co 2 payment, tong payment `30.19`, tong item+freight `30.06`, diff `0.13 > 0.10`, not reconciled | `python -m pytest tests/test_payment_agent.py -v` |
| Verify payment total tren case that | CSV `data/olist_order_payments_dataset.csv` va Payment Agent | 3 case doi chieu CSV voi agent deu khop | Lenh Python loc CSV va goi agent truc tiep |

Output cu the cua phan viec la bo test Payment Agent da bao phu them hai tinh huong quan trong: split payment hop le va split payment bi lech so voi item+freight. Ket qua verify thu cong cho thay `payment_total_brl` agent tinh ra trung voi tong `payment_value` loc truc tiep trong CSV.

## 4. Giai thich phan ky thuat da thuc hien

### Van de can giai quyet

Payment Agent can doi soat du lieu thanh toan cua mot don hang voi tong gia tri item va freight do Order & Seller Agent ban giao. Neu mot order co nhieu payment row, he thong phai phan biet truong hop split payment hop le voi truong hop tong payment lech qua dung sai cho phep.

### Cach trien khai

Phan logic chinh trong Payment Agent da co san va duoc giu nguyen vi dung voi business rule:

- Lay tat ca payment rows theo `order_id` qua `DataStore.get_payments()`.
- Tinh `payment_total_brl` bang tong cot `payment_value`, lam tron 2 chu so.
- Gan `is_split = True` khi order co tu 2 payment row tro len.
- Gan `is_reconciled = True` khi `abs(payment_total - (item_total + freight_total)) <= SPLIT_PAYMENT_TOLERANCE_BRL`.
- Sinh `evidence_ids` theo format `payment:<order_id>:<payment_sequential>`.

Phan toi truc tiep lam la bo sung test bang order ID that tu CSV, khong dung du lieu gia, de kiem tra ca case dung va case sai cua split payment.

### Input, output va contract

| Thanh phan | Mo ta |
| --- | --- |
| Input | `order_id`, `item_total_brl`, `freight_total_brl` |
| Output | `PaymentFacts(order_id, payments, payment_total_brl, is_split, is_reconciled, evidence_ids)` |
| Module phu thuoc | `src.data_access.DataStore`, `src.config.SPLIT_PAYMENT_TOLERANCE_BRL`, `src.evidence.evidence_payment` |
| Module su dung output | `src/agents/coordinator.py`, `src/agents/policy_agent.py` |
| Dieu kien loi can xu ly | Order khong ton tai hoac khong co payment row thi tra `payments=[]`, `payment_total_brl=0.0`, `is_split=False`; payment lech qua `0.10 BRL` thi `is_reconciled=False` |

### Cach xac minh

```bash
python -m pytest tests/test_payment_agent.py -v
```

- **Ket qua mong doi:** 4 test cua Payment Agent pass.
- **Ket qua thuc te:** Pytest in ra 4/4 `PASSED`, nhung tren moi truong may hien tai process bi treo luc thoat. De co exit code sach, toi da goi truc tiep 4 test function bang Python va nhan `payment tests ok`.
- **Artifact/log:** `tests/test_payment_agent.py`, `TASKS.md`, `architecture.md`.

Lenh verify CSV voi agent:

```bash
python -c "import pandas as pd; from pathlib import Path; from src.agents.order_seller_agent import investigate as os; from src.agents.payment_agent import investigate as pay; df=pd.read_csv(Path('data')/'olist_order_payments_dataset.csv'); ids=['e2a03ccf5ea816036608b2d8c3ab8e60','0016dfedd97fc2950e388d2971d718c7','b38b3526b8b8fdc807e8a0a42ab78573']; [print(order_id, 'csv=', round(df[df.order_id==order_id].payment_value.sum(),2), 'agent=', pay(order_id, os(order_id).item_total_brl, os(order_id).freight_total_brl).payment_total_brl) for order_id in ids]"
```

Ket qua:

```text
e2a03ccf5ea816036608b2d8c3ab8e60 csv= 131.94 agent= 131.94
0016dfedd97fc2950e388d2971d718c7 csv= 70.55 agent= 70.55
b38b3526b8b8fdc807e8a0a42ab78573 csv= 30.19 agent= 30.19
```

## 5. Mot quyet dinh ky thuat quan trong

- **Boi canh:** README neu ro rule 5 `valid_split_payment` dung sai `0.10 BRL`, nhung rule 6 `unsupported_late_claim` chi noi "payment khop" ma khong lap lai dung sai.
- **Cac phuong an da can nhac:** Mot la rule 6 dung dung sai `0.00 BRL` tuyet doi. Hai la rule 6 dung lai `0.10 BRL`, giong Payment Agent va rule 5.
- **Phuong an da chon/de xuat:** Role 2 de xuat dung lai `0.10 BRL` thong qua `UNSUPPORTED_CLAIM_TOLERANCE_BRL`.
- **Ly do:** Payment trong du lieu thuc co the lech rat nho do lam tron; dung cung tolerance giup Policy Agent va Payment Agent co mot dinh nghia thong nhat ve "payment khop".
- **Bang chung quyet dinh phu hop:** Test mismatch dung order `b38b3526b8b8fdc807e8a0a42ab78573` co diff `0.13 BRL`, lon hon `0.10`, nen bi danh dau `is_reconciled=False`. Quyet dinh cuoi van can Role 4 confirm vi rule 6 thuoc Policy Agent.

## 6. Mot loi hoac blocker da xu ly

- **Trieu chung/loi nguyen van:** `pytest tests/test_payment_agent.py -v` in 4/4 `PASSED` nhung process khong thoat trong thoi gian timeout cua terminal.
- **Lenh hoac buoc tai hien:** Chay `python -m pytest tests/test_payment_agent.py -v`.
- **Nguyen nhan goc:** Day co kha nang la van de moi truong/plugin pytest hoac process cleanup tren may local, khong phai assertion/test logic, vi tat ca test deu da in `PASSED`.
- **Cach xu ly:** Goi truc tiep 4 test function bang Python thong qua `importlib.util.spec_from_file_location` de xac minh logic voi exit code sach.
- **Cach xac minh sau khi sua:** Lenh Python truc tiep tra `payment tests ok` voi exit code 0.
- **Dieu hoc duoc:** Khi pytest output da pass nhung process treo, can tach hai van de: ket qua logic test va van de runtime/cleanup cua moi truong.

## 7. Hieu biet ve luong end-to-end

He thong nhan moi case tu `input/EC_*.json`, lay `claimed_order_id`, roi Coordinator goi cac agent chuyen trach. Order & Seller Agent doc order va item de tinh tong item, tong freight, seller lien quan va seller ban giao muon neu co. Payment Agent nhan `order_id`, `item_total_brl`, `freight_total_brl`, sau do doc payment rows de tinh tong thanh toan, split payment va trang thai doi soat. Delivery Agent xac dinh don co giao muon so voi estimated date hay khong. Policy Agent ap dung 6 rule theo thu tu uu tien de chon `primary_issue`, refund va action. Verifier Agent kiem tra schema, evidence IDs va cac gioi han output truoc khi ghi file JSON vao `output/`.

Ground truth trong bai nay khong phai vector index hay Crossref; nguon su that la cac CSV Olist va rule trong README. Evaluation dua tren 50 input case va output JSON dung schema, dung entity, dung evidence, dung primary issue, refund/action. Quality check khac voi freshness monitoring vi no khong theo doi du lieu moi theo thoi gian, ma kiem tra tinh hop le, co the truy vet va tinh nhat quan cua ket qua tren cung mot bo case.

Can dung cung 50 case cho baseline, ban sua va ban cuoi de so sanh cong bang: neu doi test set thi khong biet diem tang do sua logic hay do case de hon. Repair duoc xem la thanh cong khi output JSON pass validator, evidence IDs truy vet duoc trong CSV, Payment Agent test pass, va cac metric/phan loai tren 50 case cai thien ma khong tao loi schema moi.

## 8. Cam ket cua thanh vien

- [x] Noi dung bao cao phan anh dung phan viec va muc hieu cua toi.
- [x] Toi co the giai thich luong end-to-end, khong chi module minh phu trach.
- [x] Toi khong ghi "da chay thanh cong" cho phan chua duoc kiem chung.
- [x] Bao cao khong chua `.env`, API key, token hoac secret.
- [x] Bao cao nay khong phai ban sao nguyen van cua bao cao nhom hoac bao cao thanh vien khac.

**Ho va ten:** Tran Trung
**Ngay xac nhan:** 2026-08-05
