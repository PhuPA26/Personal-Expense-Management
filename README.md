---

# Personal Expense Management

Một ứng dụng quản lý chi tiêu cá nhân mạnh mẽ, được xây dựng trên nền tảng ngôn ngữ Python thuần với tư duy cấu trúc dữ liệu giải thuật nâng cao và mô hình kiến trúc sạch (Clean Architecture). Thay vì phụ thuộc vào các cấu trúc dữ liệu có sẵn của Python như `dict` hay `list`, dự án tự triển khai các bảng băm (HashMap) và cơ chế chỉ mục chuyên biệt để tối ưu hóa hiệu năng.

## 🏛️ Kiến Trúc Hệ Thống (System Architecture)

Dự án tuân thủ nghiêm ngặt nguyên lý phân rã trách nhiệm (Separation of Concerns), chia hệ thống thành các tầng xử lý riêng biệt:

```text
├── core/               # Cấu trúc dữ liệu lõi và mô hình thực thể
├── services/           # Tầng điều phối và logic nghiệp vụ tài chính
├── data/               # Tầng cơ chế chỉ mục và đọc/ghi dữ liệu
├── storage/            # Cơ sở dữ liệu vật lý dưới dạng file văn bản
├── tests/              # Hệ thống kiểm thử toàn diện
└── main.py             # Điểm chạy ứng dụng và điều hướng CLI

```

### 1. Tầng Dữ Liệu Cốt Lõi (`/core`)

Chịu trách nhiệm định nghĩa các cấu trúc lưu trữ nguyên thủy và các thực thể nghiệp vụ cốt lõi:

* 
**`data_structure.py`**: Triển khai cấu trúc **HashMap** tùy biến sử dụng phương pháp **Separate Chaining** (Linked List) để xử lý va chạm. Tự động mở rộng kích thước bảng (`__rehash`) khi hệ số tải vượt ngưỡng lý tưởng `load_factor > 0.75`. Hỗ trợ các Magic Methods (`__setitem__`, `__getitem__`, `__contains__`, `__delitem__`) giúp thao tác cú pháp tự nhiên như Dictionary mặc định.


* 
**`models.py`**: Định nghĩa mô hình trạng thái tài chính. Sử dụng lớp `MonthData` để đóng gói trạng thái danh mục (`category_states`) và danh sách giao dịch (`transactions`) theo từng lát cắt thời gian tháng. Tận dụng kế thừa qua lớp cha `CategoryState` kết hợp các lớp con `IncomeState` và `ExpenseState` để tối ưu hóa việc cập nhật dòng tiền.



### 2. Tầng Nghiệp Vụ Tài Chính (`/services`)

Nơi tập trung toàn bộ các quy tắc và logic xử lý luồng tiền:

* 
**`category_manager.py` (`CategoryManager` / `CategoryFinance`)**: Quản lý vòng đời danh mục thu/chi, kiểm soát chặt chẽ hạn mức (limit) và áp dụng cơ chế xóa mềm (**Soft Delete** - `is_active = False`) để bảo toàn dữ liệu lịch sử.


* 
**`transaction_manager.py` (`FinanceManager`)**: Bộ điều phối trung tâm xử lý các tác vụ CRUD giao dịch phức tạp, tự động dịch chuyển giao dịch giữa các tháng/danh mục, đồng thời tích hợp tính năng gợi ý danh mục thông minh dựa trên lịch sử ghi chú (`suggest_category_by_note`).


* 
**`report_manager.py` (`ReportManager`)**: Tổng hợp dữ liệu tài chính theo Ngày, Tháng, Năm hoặc $K$ tháng gần nhất, hỗ trợ kết xuất báo cáo trực quan bằng đồ họa chữ (**ASCII chart**) kèm bộ lọc cảnh báo vượt hạn mức.



### 3. Tầng Chỉ Mục & Lưu Trữ (`/data` & `/storage`)

Đảm bảo hiệu năng truy vấn cao và duy trì trạng thái bền vững của dữ liệu:

* 
**`index_services.py`**: Hoạt động như một bộ Index Database thực thụ. `MonthIndex` quản lý các khóa thời gian kiểu `"YYYY-MM"`, trong khi `TransactionMap` giúp định vị nhanh tháng của giao dịch bất kỳ với độ phức tạp $O(1)$. Điểm sáng là `TransactionIndex` ứng dụng **Tìm kiếm nhị phân (Binary Search)** để chèn và lọc giao dịch theo ngày một cách tối ưu.


* 
**`file_io.py`**: Đóng vai trò Persistence Layer. Thực hiện tuần tự hóa (Serialization) dữ liệu ra định dạng file văn bản thuần tùy biến thông qua các thẻ phân vùng (`BEGIN_CATEGORIES`, `END_CATEGORIES`,...) và phân tách bằng dấu `|`. Cơ chế xử lý chuỗi an toàn tự động escape ký tự đặc biệt (`|` thành `\|` và xuống dòng thành `\n`). Hàm `load_data` chịu trách nhiệm tự động tính toán lại và nạp dòng tiền vào đúng các State khi khởi chạy.


* 
**`/storage`**: Chứa cơ sở dữ liệu vật lý `data.txt` và tệp kịch bản kiểm thử/nhật ký log mẫu `inputoutput.txt`.



### 4. Điểm Điều Phối Trung Tâm (`main.py`)

* Đóng vai trò là "nhà trưởng điều phối" toàn bộ vòng đời ứng dụng.


* Thiết lập vòng lặp giao diện dòng lệnh (CLI Menu Loop) thân thiện.


* Quản lý bẫy ngoại lệ tập trung (Exception Handling) để bảo vệ trải nghiệm người dùng, tránh gây crash hệ thống và tự động lưu/tải dữ liệu an toàn ở hai đầu vòng đời.



---

## ⚡ Các Tính Năng Kỹ Thuật Nổi Bật (Technical Highlights)

* 
**Cấu trúc dữ liệu tự chế (Custom Data Structure)**: Đạt quyền kiểm soát hệ thống ở cấp độ thuật toán thấp nhất nhờ việc tự cài đặt HashMap Separate Chaining và danh sách liên kết.


* 
**Tối ưu hóa tìm kiếm nhị phân**: Duy trì danh sách giao dịch luôn có thứ tự theo thời gian, giúp các thao tác chèn mới (`add`), dịch chuyển ngày (`relocate`) hoặc lọc khoảng ngày đạt hiệu năng vượt trội so với duyệt tuần tự.


* 
**Mã hóa an toàn (Custom Serialization)**: Không phụ thuộc thư viện bên ngoài, tự định nghĩa cấu trúc phân vùng dữ liệu an toàn, chống phân rã cấu trúc dòng dữ liệu khi parse.



---

## 🧪 Hệ Thống Kiểm Thử Toàn Diện (`/tests`)

Dự án đi kèm một bộ test suite vô cùng hoành tráng đảm bảo tính phòng vệ và độ ổn định cao:

* 
**`test_hashmap.py`**: Unit test chuyên sâu cho cấu trúc `HashMap`, kiểm thử biên độ va chạm (collision), hàm băm và cơ chế tự động tăng kích thước bảng (`rehash`).


* 
**`test_business_logic.py`**: Đảm bảo các quy tắc ràng buộc tài chính (hạn mức âm/dương, logic cộng trừ dòng tiền, dịch chuyển tháng) vận hành đúng thiết kế.


* 
**`test_blackbox.py`**: Kiểm thử hộp đen giả lập chuỗi hành vi thực tế của người dùng để nghiệm thu luồng đi tổng thể của dữ liệu.


* 
**`test_integration_stress.py`**: Kiểm thử tích hợp và kiểm thử áp lực (Stress Test) nhằm đánh giá độ "chịu nhiệt" của hệ thống khi dữ liệu phình to.


* 
**`gen_data.py`**: Bộ công cụ tự động sinh dữ liệu giả lập (Mock Data) số lượng lớn để phục vụ đắc lực cho Stress Test và File I/O.


* 
**`script.md`**: Tài liệu hướng dẫn phối hợp và các bước thực hiện kịch bản test manual.



---

## 🚀 Hướng Dẫn Cài Đặt và Sử Dụng

### Yêu cầu hệ thống

* Python 3.8 trở lên (Không yêu cầu thêm thư viện bên ngoài).

### Cài đặt

1. Clone dự án từ GitHub:
```bash
git clone https://github.com/your-username/Personal-Expense-Management.git
cd Personal-Expense-Management

```


2. Khởi chạy ứng dụng:
```bash
python main.py

```



### Chạy Kiểm Thử (Testing)

Để thực thi toàn bộ hệ thống kiểm thử tự động, sử dụng lệnh:

```bash
python -m unittest discover -s tests

```
