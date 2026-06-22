```markdown
# Quản lý Chi tiêu Cá nhân (Personal Finance Manager)

Dự án môn học **Kỹ thuật lập trình** – xây dựng ứng dụng quản lý thu chi cá nhân bằng Python, hoạt động trên giao diện dòng lệnh (CLI). Chương trình tự cài đặt cấu trúc dữ liệu **HashMap** (bảng băm với dây chuyền) thay vì sử dụng `dict` có sẵn, kết hợp với các chỉ mục và thuật toán tối ưu để quản lý giao dịch, danh mục, ngân sách và báo cáo.

## Mục lục

- [Tính năng chính](#tính-năng-chính)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt và chạy](#cài-đặt-và-chạy)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
  - [Menu chính](#menu-chính)
  - [Quản lý danh mục](#quản-lý-danh-mục)
  - [Quản lý giao dịch](#quản-lý-giao-dịch)
  - [Báo cáo thống kê](#báo-cáo-thống-kê)
  - [Nhập CSV](#nhập-csv)
- [Kiểm thử](#kiểm-thử)
  - [Chạy toàn bộ bộ test](#chạy-toàn-bộ-bộ-test)
  - [Cấu trúc test case](#cấu-trúc-test-case)
- [Cấu trúc dữ liệu & Kỹ thuật lập trình](#cấu-trúc-dữ-liệu--kỹ-thuật-lập-trình)
- [Thông tin nhóm](#thông-tin-nhóm)
- [Giấy phép](#giấy-phép)

## Tính năng chính

- **Quản lý danh mục** (thêm, sửa, xoá mềm, phục hồi) với ràng buộc loại thu/chi và hạn mức.
- **Quản lý giao dịch** (thêm, sửa, xoá, tìm kiếm theo từ khoá, gợi ý danh mục theo ghi chú).
- **Cảnh báo vượt ngân sách** tự động khi thêm hoặc chỉnh sửa giao dịch làm tổng chi vượt hạn mức tháng.
- **Báo cáo thống kê** theo ngày, tháng, năm, K tháng gần nhất; kèm biểu đồ tỷ trọng bằng ký tự ASCII.
- **Nhập giao dịch hàng loạt** từ tệp CSV với cơ chế kiểm tra lỗi 2 lớp.
- **Lưu trữ dữ liệu** ra tệp văn bản phẳng (`storage/data.txt`) và khôi phục khi khởi động.
- **Tự cài đặt HashMap** với phương pháp dây chuyền (separate chaining) và tự động mở rộng (rehash) khi quá tải.

## Cấu trúc thư mục

```
.
├── core/
│   ├── data_structure.py         # HashMap, HashNode tự cài đặt
│   └── models.py                 # Lớp dữ liệu: Transaction, Category, MonthData, IncomeState, ExpenseState
├── data/
│   ├── file_io.py                # Đọc/ghi file text (serialize/deserialize)
│   └── index_services.py         # Chỉ mục: MonthIndex, TransactionIndex, CategoryIndex, TransactionMap
├── services/
│   ├── category_manager.py       # Quản lý danh mục (CRUD, xoá mềm)
│   ├── transaction_manager.py    # Điều phối giao dịch, kiểm tra ngân sách
│   └── report_manager.py         # Báo cáo thống kê, biểu đồ ASCII
├── storage/
│   ├── data.txt                  # Cơ sở dữ liệu phẳng (tự động tạo)
│   └── inputoutput.txt           # Nhật ký luồng CLI (tự động tạo)
├── tests/
│   ├── __init__.py
│   ├── test_hashmap.py           # Kiểm thử hộp trắng HashMap
│   ├── test_blackbox.py          # Kiểm thử hộp đen nhập liệu
│   ├── test_business_logic.py    # Kiểm thử logic nghiệp vụ
│   └── test_integration_stress.py# Kiểm thử tích hợp & tải
├── gen_data.py                   # Sinh dữ liệu lớn ngẫu nhiên (hỗ trợ stress test)
├── transactions_stress_test.csv  # Tệp CSV dữ liệu mẫu 10.000 dòng
├── script.md                     # Tài liệu đặc tả kiểm thử
├── main.py                       # Điểm khởi chạy chương trình (vòng lặp menu chính)
└── README.md                     # Tài liệu dự án
```

## Yêu cầu hệ thống

- **Python** 3.10 trở lên (chỉ sử dụng thư viện chuẩn, không cần cài thêm gói ngoài).
- Hệ điều hành: Windows, Linux, macOS đều hỗ trợ.
- Không yêu cầu cơ sở dữ liệu ngoài – dữ liệu được lưu dưới dạng tệp văn bản thuần tuý.

## Cài đặt và chạy

1. **Tải mã nguồn** (clone hoặc giải nén) vào một thư mục.
2. Mở terminal (Command Prompt, PowerShell, Terminal) và điều hướng vào thư mục dự án.
3. Chạy chương trình:
   ```bash
   python main.py
   ```
   Hoặc:
   ```bash
   python3 main.py
   ```
4. Ứng dụng sẽ khởi động, tự động nạp dữ liệu từ `storage/data.txt` (nếu có) và hiển thị menu chính.

## Hướng dẫn sử dụng

### Menu chính

```
================== MENU CHÍNH ==================
>> SỐ DƯ HIỆN TẠI: 0 đ <<
1. Quản lý Danh mục
2. Quản lý Giao dịch
3. Báo cáo thống kê
4. Nhập giao dịch từ CSV
0. Thoát và lưu dữ liệu
```

Nhập số tương ứng rồi nhấn Enter để chọn chức năng.

### Quản lý danh mục

Menu con cho phép:
- Xem danh sách danh mục (kèm trạng thái hoạt động).
- Thêm danh mục mới (nhập ID, tên, loại `income`/`expense`, hạn mức nếu là chi tiêu).
- Sửa danh mục (đổi tên, loại, hạn mức).
- Xoá mềm danh mục (dừng sử dụng nhưng vẫn giữ lại lịch sử giao dịch).

*Lưu ý:* Danh mục `income` không cần hạn mức (limit = 0), danh mục `expense` bắt buộc có hạn mức dương.

### Quản lý giao dịch

Menu con cho phép:
- Thêm giao dịch thủ công (nhập ID, số tiền, ngày `dd-mm-yyyy`, mã danh mục, ghi chú).
- Sửa giao dịch (thay đổi số tiền, ngày, danh mục, ghi chú) – tự động cập nhật số dư và kiểm tra ngân sách.
- Xoá giao dịch (xóa vĩnh viễn, cập nhật lại tổng thu/chi).
- Tìm kiếm giao dịch theo từ khoá trong ghi chú.
- Xem toàn bộ giao dịch của một tháng cụ thể.

### Báo cáo thống kê

- Báo cáo theo tháng: hiển thị tổng thu, tổng chi, số dư, biểu đồ tỷ trọng chi tiêu giữa các danh mục (bằng ký tự `■`), và danh sách các danh mục vượt hạn mức.
- Báo cáo theo năm: tương tự nhưng tổng hợp cả 12 tháng.

### Nhập CSV

Chức năng nhập giao dịch hàng loạt từ tệp CSV với cấu trúc cột:

```
Transaction_ID|Date|Category_ID|Category_Name|Type|Amount|Note
```

Ví dụ:
```
TX001|15-06-2025|C01|Ăn uống|expense|150000|Tiền ăn trưa
```

Chương trình tự động kiểm tra:
- **Lớp 1 (cú pháp):** đủ 7 cột, số tiền là số hợp lệ, ngày đúng định dạng `dd-mm-yyyy`.
- **Lớp 2 (nghiệp vụ):** danh mục tồn tại và đang hoạt động, số tiền > 0, ngày không ở tương lai, ID không trùng.

Các dòng lỗi sẽ bị bỏ qua và hiển thị nguyên nhân, không làm gián đoạn quá trình import.

## Kiểm thử

Dự án đi kèm bộ kiểm thử gồm **18 test case**, chia làm 4 nhóm:
- **White-box** (WT-01 → WT-03): kiểm tra HashMap tự cài đặt.
- **Black-box** (BT-01 → BT-03): kiểm tra nhập liệu menu CLI.
- **Business Logic** (LT-01 → LT-08): kiểm tra nghiệp vụ giao dịch, ngân sách, danh mục, báo cáo.
- **Integration & Stress** (IT-01 → IT-03, ST-01): kiểm tra đọc/ghi file và tải 10.000 giao dịch.

### Chạy toàn bộ bộ test

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Kết quả mong đợi: tất cả 18 test case đều **PASS**.

### Cấu trúc test case

Xem chi tiết từng test case trong tài liệu `script.md` hoặc trực tiếp trong các file `tests/test_*.py`.

## Cấu trúc dữ liệu & Kỹ thuật lập trình

- **HashMap tự cài đặt**: mảng bucket (kích thước 1024), xử lý va chạm bằng danh sách liên kết đơn (separate chaining), tự động rehash khi hệ số tải > 0.75.
- **Hàm băm**: polynomial rolling với hằng số 31, modulo kích thước bảng.
- **Chỉ mục dữ liệu**:
  - `MonthIndex`: băm theo chuỗi `"YYYY-MM"` → `MonthData`.
  - `TransactionIndex`: danh sách giao dịch trong tháng, sắp xếp theo ngày, chèn bằng **tìm kiếm nhị phân** (O(log N)).
  - `CategoryIndex`: băm `category_id` → `IncomeState`/`ExpenseState`.
  - `TransactionMap`: băm `transaction_id` → `(year, month)` để định vị nhanh giao dịch toàn cục.
- **Xóa mềm (Soft Delete)**: danh mục bị xóa chỉ chuyển cờ `is_active = False`, không xóa vật lý, cho phép phục hồi và giữ toàn vẹn lịch sử.
- **Kiểm soát lỗi 2 lớp**: khi nhập CSV, lớp cú pháp lọc lỗi định dạng, lớp nghiệp vụ kiểm tra ràng buộc tài chính.
- **Lưu trữ phẳng**: dữ liệu được tuần tự hóa thành văn bản, dùng cơ chế escape ký tự đặc biệt (`|` → `\|`, `\n` → `\\n`) để đảm bảo toàn vẹn.

## Thông tin nhóm


| Họ tên | MSSV | Vai trò / Công việc |
|--------|------|---------------------|
| ...    | ...  | ...                 |

## Giấy phép

Dự án được thực hiện cho mục đích học tập thuộc môn **Kỹ thuật lập trình**. Mã nguồn có thể được sử dụng tự do cho mục đích tham khảo, không bảo đảm cho mục đích thương mại.
```
