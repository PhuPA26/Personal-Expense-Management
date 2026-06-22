
---

```markdown
# 💰 Personal Expense Management (Quản lý Chi tiêu Cá nhân)

> **Dự án cuối khóa môn học:** Kỹ thuật lập trình (MI3310) - Viện Toán ứng dụng và Tin học (SAMI)
> **Nền tảng phát triển:** Python 3.10+ thuần (Không phụ thuộc vào các thư viện bên ngoài)
> **Điểm nhấn công nghệ:** Tự thiết kế cấu trúc dữ liệu HashMap, Indexing Layer và Pipeline kiểm thử phòng thủ toàn diện.

---

## 🏛️ Kiến Trúc Hệ Thống (System Architecture)

Dự án được xây dựng dựa trên nguyên lý phân rã trách nhiệm (**Separation of Concerns**) với mô hình kiến trúc phân tầng sạch sẽ giúp hệ thống có khả năng mở rộng tốt và dễ bảo trì.

```text
.
├── core/                  # Tầng dữ liệu cốt lõi (Mô hình thực thể & CTDL tự chế)
│   ├── data_structure.py  # HashMap, HashNode tự cài đặt qua Separate Chaining
│   └── models.py          # Khối trạng thái tài chính (Transaction, MonthData, State)
├── data/                  # Tầng lưu trữ & Chỉ mục (Database Indexing & Persistence)
│   ├── file_io.py         # Bộ mã hóa/Giải mã văn bản phẳng (Escape String Layer)
│   └── index_services.py  # Chỉ mục hiệu năng cao (Binary Search Index, O(1) Map)
├── services/              # Tầng nghiệp vụ (Bảo toàn luồng tiền & Tính toán ràng buộc)
│   ├── category_manager.py# Điều phối danh mục (Hạn mức, Soft Delete)
│   ├── transaction_manager.py # Quản lý CRUD giao dịch, kiểm soát ngân sách tháng
│   └── report_manager.py  # Công cụ kết xuất báo cáo & Render đồ họa chữ ASCII
├── storage/               # Phân vùng vật lý lưu trữ dữ liệu bền vững
│   ├── data.txt           # Cơ sở dữ liệu văn bản phẳng hóa
│   └── inputoutput.txt    # Nhật ký luồng hoạt động CLI
├── tests/                 # Hệ thống phòng vệ & Cam kết chất lượng mã nguồn
│   ├── test_hashmap.py    # Unit Test hộp trắng cấu trúc HashMap
│   ├── test_blackbox.py   # Kiểm thử hộp đen giao diện nhập liệu
│   ├── test_business_logic.py # Kiểm thử logic ràng buộc dòng tiền nghiệp vụ
│   └── test_integration_stress.py # Kiểm thử tích hợp & Tải cực đại (Stress Test)
├── gen_data.py            # Công cụ sinh Mock Data tự động (Phục vụ stress test)
├── main.py                # Nhà trưởng điều phối vòng đời ứng dụng (Global Exception CLI Loop)
└── README.md              # Tài liệu hướng dẫn & Đặc tả kỹ thuật dự án

```

---

## ⚡ Các Tính Năng Kỹ Thuật Nổi Bật (Technical Highlights)

### 1. Cấu Trúc Dữ Liệu Tự Chế (Custom HashMap)

* **Xử lý va chạm thông minh:** Triển khai phương pháp chuỗi phân tách (**Separate Chaining**) bằng danh sách liên kết đơn. Khi xảy ra va chạm băm, phần tử mới được chèn lên đầu chuỗi (`prepend`) để tối ưu hóa thời gian.
* **Cơ chế Tự động Rehashing:** Hệ thống giám sát hệ số tải thực tế. Khi vượt ngưỡng lý tưởng `load_factor > 0.75`, mảng buckets tự động nhân đôi kích thước và tiến hành băm lại toàn bộ dữ liệu để duy trì độ phức tạp tiệm cận `O(1)`.
* **Magic Methods:** Nạp chồng toán tử (`__setitem__`, `__getitem__`, `__contains__`, `__delitem__`) giúp các tầng xử lý phía trên thao tác dữ liệu với cú pháp trực quan như Dictionary nguyên bản của Python.

### 2. Bộ Chỉ Mục Hiệu Năng Cao (Database Indexing Layer)

* **Tìm kiếm Nhị phân (Binary Search):** Lớp `TransactionIndex` duy trì danh sách giao dịch luôn có thứ tự theo dòng thời gian một cách tự nhiên. Thao tác tìm kiếm khoảng ngày và định vị vị trí chèn mới đạt hiệu năng tối ưu `O(log n)`.
* **Định vị Thời gian Thực:** `MonthIndex` và `TransactionMap` giúp liên kết các giao dịch đơn lẻ tới lát cắt dữ liệu tháng tương ứng ngay lập tức với chi phí xử lý là `O(1)`.

### 3. Cơ Chế Mã Hóa An Toàn & Lưu Trữ Bền Vững (Persistence Layer)

* **Serialization/Deserialization:** Dữ liệu được lưu trữ trực tiếp xuống tệp phẳng `storage/data.txt` thông qua cơ chế phân vùng bằng các thẻ block dữ liệu (`BEGIN_...` / `END_...`) ngăn cách bởi Delimiter `|`.
* **Xử lý chuỗi phòng thủ (Escape Character):** Tự động chuyển đổi các ký tự nguy hiểm do người dùng nhập vào để bảo toàn cấu trúc dữ liệu (`|` thành `\|` và dấu xuống dòng `\n` thành `\\n`), loại bỏ hoàn toàn rủi ro vỡ cấu trúc cột thuộc tính khi nạp lại dữ liệu.

---

## ✨ Tính Năng Nghiệp Vụ Thực Tế

* 🔹 **Quản lý danh mục chuyên sâu:** Phân tách rõ ràng loại hình dòng tiền (`income` / `expense`). Áp dụng cơ chế **Xóa mềm (Soft Delete - `is_active = False`)** giúp ẩn danh mục khỏi giao diện nhưng bảo toàn nguyên vẹn lịch sử giao dịch tài chính quá khứ.
* 🔹 **Cảnh báo Ngân sách Tự động (Budget Alert):** Hệ thống tự động chặn và đưa ra cảnh báo tức thời khi có giao dịch chi tiêu mới vượt quá hạn mức ngân sách tháng đã thiết lập cho danh mục đó.
* 🔹 **Gợi ý Danh mục Thông minh:** Hàm `suggest_category_by_note` phân tích thói quen ghi chú lịch sử để đưa ra đề xuất danh mục chính xác khi người dùng nhập giao dịch mới.
* 🔹 **Báo cáo Trực quan (ASCII Chart):** Kết xuất báo cáo phân bổ tỷ trọng dòng tiền theo Ngày/Tháng/Năm trực tiếp ngay trên Terminal bằng đồ họa chữ đơn cách.
* 🔹 **Pipeline Nhập liệu CSV 2 Lớp:** Lớp 1 kiểm tra cú pháp cấu trúc file (Định dạng ngày, kiểu dữ liệu số tiền). Lớp 2 kiểm tra logic ràng buộc (Sự tồn tại của danh mục, tính duy nhất của ID, chặn ngày ở tương lai).

---

## 🧪 Hệ Thống Kiểm Thử Toàn Diện (Testing Suite)

Dự án tích hợp bộ kiểm thử tự động gồm **18 ca kiểm thử (Test Cases)** chuyên sâu, cam kết tính ổn định tuyệt đối trước khi bàn giao:

| Mã Case | Phân Nhóm Kiểm Thử | Mục Tiêu Khảo Sát | Trạng Thái |
| --- | --- | --- | --- |
| **WT-01 → WT-03** | Hộp trắng (White-box) | Kiểm thử Collision, Rehashing, Magic Methods trên HashMap. | **PASS** |
| **BT-01 → BT-03** | Hộp đen (Black-box) | Kiểm thử luồng nhập liệu, tính toàn vẹn menu CLI. | **PASS** |
| **LT-01 → LT-08** | Logic Nghiệp vụ (Business) | Kiểm thử tính toán dòng tiền, bẫy hạn mức, dịch chuyển tháng. | **PASS** |
| **IT-01 → IT-03** | Tích hợp (Integration) | Kiểm thử đồng bộ luồng Đọc/Ghi (I/O File) dữ liệu vật lý. | **PASS** |
| **ST-01** | Kiểm thử áp lực (Stress Test) | Chạy tải cực đại hệ thống với bộ dữ liệu **10.000 giao dịch** mẫu. | **PASS** |

---

## 🚀 Hướng Dẫn Cài Đặt và Khởi Chạy

### Yêu cầu hệ thống

* Máy tính đã cài đặt **Python 3.10** hoặc các phiên bản cao hơn.

### Các bước khởi chạy

1. **Tải mã nguồn về máy cục bộ:**
```bash
git clone [https://github.com/yourusername/Personal-Expense-Management.git](https://github.com/yourusername/Personal-Expense-Management.git)
cd Personal-Expense-Management

```


2. **Khởi chạy ứng dụng chính:**
```bash
python main.py

```


> *Hệ thống sẽ tự động tìm kiếm và nạp tệp `storage/data.txt`. Nếu chưa có, ứng dụng sẽ tự khởi tạo cơ sở dữ liệu mới tinh.*


3. **Thực thi toàn bộ hệ thống kiểm thử tự động:**
```bash
python -m unittest discover -s tests -p "test_*.py" -v

```



---

## 👥 Thông Tin Thành Viên & Phân Công Nhiệm Vụ

### Nhóm 16 - Lớp học phần MI3310

| Họ và Tên | Mã Số Sinh Viên | Vai Trò / Nhiệm Vụ Đảm Nhận | Tỷ Lệ Đóng Góp |
| --- | --- | --- | --- |
| **Mai Đức Hiếu** | *[Điền MSSV]* | Phát triển Tầng Dữ liệu Cốt lõi (`/core`), HashMap & Cấu trúc Mô hình State. | 33.3% |
| **Trần Hoàng Đức Linh** | *[Điền MSSV]* | Phát triển Tầng Chỉ mục & Lưu trữ (`/data`), Bộ giải mã File I/O & Index Services. | 33.3% |
| **Phạm Anh Phú** | *[Điền MSSV]* | Phát triển Tầng Nghiệp vụ (`/services`), Quản lý Menu Điều phối (`main.py`) & Hệ thống Tests. | 33.3% |

---

## 📄 Giấy Phép

Dự án được phân phối và lưu trữ dưới dạng mã nguồn mở phục vụ cho mục đích học tập và nghiên cứu học phần **Kỹ thuật lập trình**.

```
***

```
