---

# 💰 HỆ THỐNG QUẢN LÝ TÀI CHÍNH CÁ NHÂN (PERSONAL FINANCE MANAGER)

Dự án này là một ứng dụng giao diện dòng lệnh (CLI) giúp người dùng quản lý thu chi cá nhân một cách có hệ thống và chi tiết. Hệ thống giải quyết bài toán theo dõi dòng tiền, kiểm soát ngân sách và cung cấp cái nhìn tổng quan về tình hình tài chính thông qua các báo cáo trực quan mà không cần phụ thuộc vào hệ quản trị cơ sở dữ liệu bên ngoài.

Ứng dụng đặc biệt chú trọng vào việc xây dựng nền tảng khoa học máy tính vững chắc bằng cách tự triển khai các cấu trúc dữ liệu từ đầu như Bảng băm (HashMap) và Thuật toán tìm kiếm nhị phân (Binary Search) để tối ưu hóa hiệu suất truy xuất.

---

## 🚀 CÁC TÍNH NĂNG NỔI BẬT

* **Quản lý Danh mục (Categories):** Hỗ trợ thêm mới, chỉnh sửa, và xóa mềm (soft delete) các danh mục thu/chi để bảo toàn tính toàn vẹn dữ liệu lịch sử.
* **Kiểm soát Ngân sách (Budgeting):** Cho phép thiết lập hạn mức chi tiêu cho từng danh mục và tự động phát cảnh báo khi giao dịch mới làm vượt ngân sách tháng.
* **Quản lý Giao dịch (Transactions):** Ghi nhận chi tiết số tiền, ngày tháng, danh mục và ghi chú; hỗ trợ tự động gợi ý danh mục dựa trên lịch sử ghi chú.
* **Hệ thống Báo cáo Đa dạng:** Trích xuất báo cáo tài chính theo ngày, tháng, năm, hoặc chu kỳ K tháng gần nhất kèm theo biểu đồ ASCII trực quan biểu diễn tỷ trọng chi tiêu.
* **Lưu trữ & Khôi phục Dữ liệu (I/O):** Serialize toàn bộ hệ thống object thành file text tùy chỉnh (`storage/data.txt`) và hỗ trợ tính năng Import giao dịch hàng loạt từ file CSV.
* **Tối ưu hóa Tra cứu:** Áp dụng thuật toán Binary Search để tra cứu giao dịch theo ngày và sử dụng Custom HashMap để quản lý trạng thái phân mục theo từng tháng.

---

## 🛠️ CÔNG NGHỆ & THƯ VIỆN SỬ DỤNG

Dự án được phát triển thuần túy bằng Python tiêu chuẩn, không sử dụng các framework hay thư viện bên thứ ba nhằm tối đa hóa khả năng di động và tập trung vào kỹ năng thiết kế thuật toán cốt lõi.

| Công nghệ / Thư viện | Phân loại | Mục đích / Chức năng trong dự án |
| --- | --- | --- |
| **Python 3.x** | Ngôn ngữ lập trình | Xây dựng toàn bộ logic, cấu trúc dữ liệu và giao diện CLI. |
| **datetime** | Thư viện chuẩn | Xử lý, phân tích định dạng chuỗi ngày tháng và tính toán chu kỳ thời gian. |
| **csv** | Thư viện chuẩn | Đọc và bóc tách dữ liệu từ file đầu vào để import giao dịch hàng loạt. |

---

## 📂 CẤU TRÚC THƯ MỤC

Dự án được phân tách thành các module độc lập, đảm bảo tính đóng gói và dễ dàng bảo trì.

```text
├── core/
│   ├── data_structure.py    # Triển khai HashMap và HashNode từ đầu
│   └── models.py            # Chứa các lớp thực thể (Transaction, Category, ExpenseState...)
├── data/
│   ├── file_io.py           # Logic đọc/ghi file lưu trữ persistent custom format
│   └── index_services.py    # Các lớp chỉ mục (MonthIndex, TransactionIndex, CategoryIndex)
├── services/
│   ├── category_manager.py  # Xử lý nghiệp vụ liên quan đến danh mục
│   ├── transaction_manager.py# Xử lý nghiệp vụ giao dịch, kiểm tra ngân sách, gợi ý
│   └── report_manager.py    # Tổng hợp số liệu và render giao diện báo cáo ASCII
├── storage/                 # Thư mục chứa dữ liệu sinh ra trong quá trình chạy
│   ├── data.txt             # File CSDL chính của hệ thống
│   └── inputoutput.txt      # File log ghi lại lịch sử thao tác của người dùng
└── main.py                  # Điểm neo khởi chạy ứng dụng CLI, chứa cấu trúc Menu

```

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY

**Yêu cầu hệ thống:**

* Hệ điều hành: Windows, macOS, hoặc Linux.
* Môi trường: Python 3.8 trở lên.

**Các bước cài đặt chi tiết:**

1. **Clone repository về máy local:**
```bash
git clone https://github.com/PhuPA26/Personal-Expense-Management.git
cd personal-finance-manager

```


2. **Khởi tạo cấu trúc lưu trữ (Tùy chọn nếu chưa có):**
Đảm bảo rằng thư mục `storage` đã tồn tại trong thư mục gốc của dự án để hệ thống có thể lưu file `data.txt` và `inputoutput.txt`.
```bash
mkdir storage

```


3. **Khởi chạy ứng dụng:**
Dự án không yêu cầu cài đặt gói phụ thuộc qua pip do sử dụng 100% thư viện chuẩn. Bạn chỉ cần chạy file chính:
```bash
python main.py

```



---

## 🧪 HƯỚNG DẪN SỬ DỤNG & DEMO

Sau khi khởi chạy `main.py`, hệ thống sẽ hiển thị **MENU CHÍNH** trên terminal với số dư hiện tại. Người dùng tương tác bằng cách nhập các phím số tương ứng.

**Ví dụ: Thêm một giao dịch mới**
Từ Menu Chính, chọn `2` (Quản lý Giao dịch), sau đó chọn `1` (Thêm giao dịch).

```text
  -- THÊM GIAO DỊCH --
  Số tiền (đ)      : 150000
  Ngày (dd-mm-yyyy): 18-06-2026
  Ghi chú          : An trua cung nhom
  -- Danh sách Danh mục hiện có --
   - An uong (expense)
   - Luong (income)
  Chọn danh mục (Nhập Tên): An uong
  KẾT QUẢ: Thêm giao dịch thanh cong. (ID=TX20260618175200, So tien=150,000d, Ngay=18-06-2026)

```

Tất cả các thao tác (Prompt và Input) đều được hệ thống tự động ghi log vào file `storage/inputoutput.txt` để hỗ trợ quá trình gỡ lỗi.

---

## 🗺️ KIẾN TRÚC HỆ THỐNG & SƠ ĐỒ LỚP

Cấu trúc module và mô tả dữ liệu của dự án được tổ chức chặt chẽ theo hướng đối tượng, phân tách rõ ràng giữa tầng lưu trữ, tầng nghiệp vụ và tầng giao diện hiển thị.

* **Tầng Models (Thực thể Dữ liệu):** Sử dụng tính kế thừa để quản lý trạng thái phân mục. Lớp cơ sở `CategoryState` được kế thừa bởi `IncomeState` và `ExpenseState` (chứa thêm thuộc tính `limit` để quản lý ngân sách). `MonthData` đóng vai trò là container tổng hợp giao dịch theo từng tháng.
* **Tầng Data Structures (Cấu trúc Dữ liệu):** Việc tổ chức dữ liệu dạng Đồ thị/Cây hoặc Bảng băm được đóng gói trong `core.data_structure.HashMap` với cơ chế xử lý va chạm (chaining) qua `HashNode` và tự động rehash khi hệ số tải vượt 75%.
* **Tầng Indexing (Chỉ mục):** `TransactionIndex` cung cấp cơ chế thêm mới theo thứ tự thời gian và duy trì mảng giao dịch luôn được sắp xếp, tạo tiền đề để áp dụng thuật toán `find_by_date` bằng Binary Search, đạt độ phức tạp $O(\log n)$.
* **Tầng Services (Nghiệp vụ):** `FinanceManager` là trung tâm điều phối, tương tác với các lớp Index để thực hiện thao tác CRUD, trong khi `ReportManager` đảm nhiệm việc quét dữ liệu qua bảng băm để kết xuất giao diện.

---

## 👥 THÀNH VIÊN THAM GIA & ĐÓNG GÓP

| Họ và Tên | Vai trò / Chuyên môn | Mã số sinh viên |
| --- | --- | --- |
| Phạm Anh Phú | Phân tích và phát triển hệ thống  | 202418960 |
| Mai Đức Hiếu | Phát triển và hoàn thiện phần mềm | 202418896 |
| Trần Hoàng Đức Linh | Tài liệu và báo cáo | 202418932 |

---

## 📄 GIẤY PHÉP (LICENSE)

Dự án này được phân phối dưới giấy phép **MIT License**. Bạn được tự do sử dụng, sao chép, sửa đổi, hợp nhất, xuất bản, phân phối và cấp phép lại các bản sao của phần mềm, với điều kiện giữ nguyên thông báo bản quyền gốc.
