# KỊCH BẢN KIỂM THỬ - DỰ ÁN QUẢN LÝ CHI TIÊU CÁ NHÂN

## Giới thiệu
Bộ kiểm thử này được thiết kế dành riêng cho dự án Quản lý chi tiêu cá nhân, dựa trên code thực tế của nhóm.  
Nó bao phủ toàn bộ các thành phần: cấu trúc dữ liệu tự cài đặt (HashMap), nhập liệu, logic nghiệp vụ (thêm/xóa/sửa giao dịch, ngân sách, danh mục), báo cáo, đọc/ghi file và kiểm tra tải.

**Tổng số test case:** 16

---

## I. KIỂM THỬ HỘP TRẮNG (WHITE-BOX) – HashMap tự cài đặt
*Mục đích: Kiểm tra tính toàn vẹn của cấu trúc HashMap (separate chaining, rehash).*

| ID | Chức năng kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi | Kỹ thuật áp dụng |
|----|-------------------|----------------|------------------|-------------------|
| WT-01 | Thêm cặp key‑value mới vào HashMap rỗng | HashMap rỗng. Thêm `("food", 100)` | `count` tăng lên 1; `get("food")` trả về `100`. Bucket chứa đúng 1 node, con trỏ `next` là `None`. | Kiểm tra tính bất biến (Invariants) |
| WT-02 | Cập nhật value cho key đã tồn tại | HashMap đã có `("food", 100)`. Gọi `insert("food", 200)` | `count` vẫn là 1 (không tăng). `get("food")` trả về `200`. Node cũ được cập nhật, không tạo node mới. | Kiểm tra tính bất biến & Thuộc tính lưu trữ (Conservation) |
| WT-03 | Xóa key trong bucket có xích (collision) | HashMap có 2 key "abc" và "xyz" **cùng bucket** (chọn key phù hợp để tạo collision). Xóa "abc". | Sau xóa, "xyz" vẫn truy xuất được; chuỗi liên kết trong bucket không đứt; `count` giảm 1. | Kiểm tra tính bất biến |

> **Gợi ý:** Để tạo collision, có thể dùng chính hàm hash trong code để tìm hai chuỗi khác nhau nhưng cùng chỉ mục.

---

## II. KIỂM THỬ HỘP ĐEN (BLACK-BOX) – Giao diện nhập liệu (Menu CLI)
*Mục đích: Đảm bảo chương trình không crash với dữ liệu nhập sai, kiểm tra điều kiện tiền đề.*

| ID | Chức năng kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi | Kỹ thuật áp dụng |
|----|-------------------|----------------|------------------|-------------------|
| BT-01 | Nhập lựa chọn menu không hợp lệ | Nhập `0`, `"abc"`, `-1` khi menu yêu cầu số 1-6 | Chương trình không crash, hiển thị thông báo "Lựa chọn không hợp lệ" và yêu cầu nhập lại. | Kiểm thử giá trị biên & Đoán lỗi |
| BT-02 | Nhập số tiền giao dịch không hợp lệ | Số tiền: `0`, `-50000` | Hệ thống từ chối, yêu cầu nhập số tiền lớn hơn 0. (Dựa vào `_check_amount` trong code) | Kiểm tra điều kiện trước (Pre-condition) |
| BT-03 | Nhập ngày sai định dạng hoặc trong tương lai | Ngày: `32/13/2026`, `15-03-2025`, hoặc ngày mai | Hệ thống báo lỗi "Định dạng ngày không hợp lệ" hoặc "Ngày không thể trong tương lai", yêu cầu nhập lại. (Dựa vào `_parse_and_validate_date`) | Đoán lỗi & Kiểm tra điều kiện trước |

---

## III. KIỂM THỬ LOGIC NGHIỆP VỤ (BUSINESS LOGIC)
*Mục đích: Kiểm tra các chức năng cốt lõi: thêm/xóa/sửa giao dịch, quản lý danh mục, cảnh báo ngân sách, báo cáo.*

| ID | Chức năng kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi | Kỹ thuật áp dụng |
|----|-------------------|----------------|------------------|-------------------|
| LT-01 | Thêm giao dịch chi vượt ngân sách (cảnh báo) | Danh mục "Ăn uống" (expense) có limit = 1.000.000đ. Hiện đã chi 800.000đ. Thêm giao dịch chi 300.000đ. | Giao dịch được lưu; `add_transaction` trả về `True` (vượt ngân sách). `ExpenseState.total_expense` = 1.100.000đ. | Kiểm thử lộ trình (Path Testing) |
| LT-02 | Cập nhật giao dịch làm vượt ngân sách (tăng số tiền) | Giao dịch "Đi lại" 500.000đ (limit 1.000.000đ, đã chi 600.000đ). Sửa số tiền thành 1.200.000đ. | Sau cập nhật, `total_expense` = 1.300.000đ → vượt ngân sách, hàm `update_transaction` trả về `True`. | Kiểm thử lộ trình + Giá trị biên |
| LT-03 | Xóa giao dịch và cập nhật lại số dư | Có 2 giao dịch: Thu 5.000.000đ, Chi 2.000.000đ. Xóa giao dịch Chi. | `get_total_balance()` trả về 5.000.000đ. `ExpenseState` tương ứng bị xóa nếu `total_expense = 0`. | Kiểm thử chức năng dựa trên đặc tả |
| LT-04 | Phục hồi danh mục bị xóa mềm (soft delete) | Danh mục "Giải trí" (id="GT") đã bị `remove_category` (is_active=False). Thêm lại với cùng id, name, type, limit. | Danh mục được kích hoạt trở lại (`is_active=True`), không tạo mới. Không báo lỗi trùng tên. | Kiểm thử lộ trình (Path Testing): nhánh phục hồi |
| LT-05 | Thêm danh mục với tên đã tồn tại (đang active) | Đã có danh mục "Ăn uống". Thêm danh mục mới cũng tên "Ăn uống". | Hệ thống từ chối, ném `ValueError("Category name already exists")`. | Đoán lỗi & Kiểm tra điều kiện trước |
| LT-06 | Cập nhật giao dịch: đổi category (cùng tháng) | Giao dịch "Đi lại" 500.000đ (tháng này, category cũ "Đi lại"). Sửa `category_id` sang "Ăn uống" (limit 1.000.000đ, hiện đã chi 800.000đ). | `total_expense` của "Đi lại" giảm 500.000đ; "Ăn uống" tăng 500.000đ → tổng 1.300.000đ, vượt ngân sách → hàm trả về `True`. | Kiểm thử lộ trình |
| LT-07 | Cập nhật giao dịch: đổi ngày tháng (chuyển tháng) | Giao dịch tháng 5 "Mua sách" 200.000đ. Sửa `date` sang tháng 6. | Giao dịch biến mất khỏi tháng 5, xuất hiện trong tháng 6 đúng vị trí theo ngày. `total_expense` tháng 5 giảm 200.000đ, tháng 6 tăng 200.000đ. | Kiểm thử lộ trình + Tích hợp |
| LT-08 | Báo cáo tháng có vượt ngân sách (kiểm tra output) | Tạo dữ liệu tháng: một danh mục vượt, một không. Gọi `generate_monthly_report(year, month)`. | Output in đúng tổng thu/chi, biểu đồ, và mục "DANH SÁCH DANH MỤC VƯỢT NGÂN SÁCH" liệt kê chính xác danh mục vượt kèm số tiền vượt. | Kiểm thử dựa trên đặc tả |

---

## IV. KIỂM THỬ TÍCH HỢP (INTEGRATION) & TẢI (STRESS)
*Mục đích: Kiểm tra đọc/ghi file, xử lý dữ liệu lỗi, và khả năng chịu tải của hệ thống.*

| ID | Chức năng kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi | Kỹ thuật áp dụng |
|----|-------------------|----------------|------------------|-------------------|
| IT-01 | Khởi động chương trình khi file dữ liệu không tồn tại hoặc trống | File `storage/data.txt` không tồn tại hoặc rỗng (0 byte) | Chương trình khởi tạo thành công, danh sách giao dịch và danh mục rỗng, không crash, số dư = 0. | Kiểm thử tích hợp dữ liệu vào |
| IT-02 | Lưu và tải lại dữ liệu đầy đủ | Thêm 5 giao dịch (cả thu và chi), 3 danh mục. Gọi `save_data`. Tắt chương trình, mở lại, dùng `load_data`. | Sau khi load, số dư, danh sách giao dịch (đúng thứ tự ngày), trạng thái danh mục (active/inactive) khớp hoàn toàn với trước khi lưu. | Kiểm thử tích hợp hệ thống |
| IT-03 | Load file có dòng lỗi định dạng | File `data.txt` chứa một dòng giao dịch thiếu cột, một dòng sai kiểu số. | Chương trình load thành công, bỏ qua các dòng lỗi, vẫn đọc được các dòng hợp lệ. Không crash. | Kiểm thử tích hợp dữ liệu vào |
| ST-01 | Stress test với 10.000 giao dịch | Import hoặc tạo vòng lặp 10.000 giao dịch. | Hệ thống không crash; HashMap tự động rehash khi cần; `get_total_balance()` trả về kết quả chính xác. | Kiểm thử tải / Áp lực |

---

## Hướng dẫn thực hiện và lưu ý khi bảo vệ

1. **Với các test case hộp trắng (WT-01 đến WT-03):**  
   - Chuẩn bị trước các cặp key để tạo collision.  
   - In thông tin bucket, `count`, hoặc dùng debug để xác minh liên kết.

2. **Với các test case logic nghiệp vụ:**  
   - Sử dụng dữ liệu cụ thể, tính toán trước tổng thu/chi.  
   - Đối với LT-06 và LT-07, kiểm tra cẩn thận `ExpenseState` của từng danh mục sau khi sửa.

3. **Với báo cáo (LT-08):**  
   - Chụp màn hình hoặc ghi log để đối chiếu với kết quả mong đợi.

4. **Với file lỗi (IT-03):**  
   - Tạo file mẫu có dòng: `"TK01|abc|2025-01-01|Food|expense|note"` (sai kiểu số) hoặc thiếu cột.

5. **Kết quả thực tế:**  
   - Trong báo cáo, bạn chỉ cần ghi **Đạt (Pass)** sau khi chạy và kiểm tra đúng.
