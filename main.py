import datetime
import csv
from services import transaction_manager
from services import category_manager as CatMgr
from data import index_services
from core import models
from services import report_manager
from data import file_io
# ================================================================
# LOG — chỉ ghi đầu vào người dùng nhập + đầu ra kết quả
_LOG_FILE = "storage/inputoutput.txt"
def _log(text):
    f = open(_LOG_FILE, "a", encoding="utf-8")
    f.write(text + "\n")
    f.close()


# In ra terminal (không log)
def _print(text=""):
    print(text)


# Ghi kết quả đầu ra vào log (và in ra terminal)
def _print_result(text=""):
    print(text)
    _log(text)


# Nhập từ người dùng — log cả prompt lẫn giá trị nhập
def _input(prompt=""):
    value = input(prompt)
    _log(f"INPUT  >> {prompt}{value}")
    return value


# Ghi nhãn hành động (người dùng chọn menu gì)
def _log_action(action_label):
    _log(f"\n[HANH DONG] {action_label}")
    _log("-" * 40)




# TIỆN ÍCH HIỂN THỊ
_SEP  = "=" * 58
_LINE = "-" * 58

def _date_str(date):
    return date.strftime("%d-%m-%Y") if hasattr(date, "strftime") else str(date)


def _fmt_category(cat):
    status    = "Hoạt động" if cat.is_active else "Đã xóa"
    limit_str = f"{cat.limit:,.0f} d" if cat.type == "expense" else "---"
    return (f"  ID: {cat.id:<12} | Tên: {cat.name:<15} | "
            f"Loại: {cat.type:<8} | Hạn mức: {limit_str:<15} | {status}")


def _fmt_transaction(tx):
    return (f"  ID: {tx.transaction_id:<12} | Ngày: {_date_str(tx.date)} | "
            f"Số tiền: {tx.amount:>15,.0f} d | Cat: {tx.category_id:<12} | Ghi chú: {tx.note}")


# In + log kết quả category / transaction
def _print_category(cat):
    line = _fmt_category(cat)
    print(line)
    _log(line)


def _print_transaction(tx):
    line = _fmt_transaction(tx)
    print(line)
    _log(line)

# DANH MUC (CATEGORY)
def _menu_category(finance_manager, category_finance):
    while True:
        _print()
        _print(_SEP)
        _print("  QUẢN LÝ DANH MỤC")
        _print(_SEP)
        _print("  1. Thêm danh mục")
        _print("  2. Sửa danh mục")
        _print("  3. Xóa danh mục (soft delete)")
        _print("  4. Tìm kiếm danh mục")
        _print("  5. Xem tất cả danh mục")
        _print("  6. Đặt lại hạn mức cho tháng cụ thể")
        _print("  0. Quay lại")
        _print(_LINE)
        choice = _input("  Chọn: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            _log_action("Thêm danh mục")
            _add_category(category_finance)
            file_io.save_data(finance_manager, category_finance)
        elif choice == "2":
            _log_action("Sửa danh mục")
            _update_category(category_finance)
            file_io.save_data(finance_manager, category_finance)
        elif choice == "3":
            _log_action("Xóa danh mục")
            _remove_category(category_finance)
            file_io.save_data(finance_manager, category_finance)
        elif choice == "4":
            _log_action("Tìm kiếm danh mục")
            _search_category(category_finance)
        elif choice == "5":
            _log_action("Xem tất cả danh mục")
            _list_all_categories(category_finance)
        elif choice == "6":
            _log_action("Đặt lại hạn mức cho tháng cụ thể")
            _set_monthly_budget(finance_manager)
            file_io.save_data(finance_manager, category_finance)
        else:
            _print("  Lựa chọn không hợp lệ.")


def _add_category(category_finance):
    _print()
    _print("  -- THÊM DANH MỤC --")
    name     = _input("  Tên danh mục         : ").strip()
    cat_id   = name
    cat_type = _input("  Loại (income/expense): ").strip().lower()
    limit    = 0
    if cat_type == "expense":
        raw = _input("  Hạn mức (đ)          : ").strip()
        try:
            limit = float(raw)
        except ValueError:
            _print_result("  KẾT QUẢ: Hạn mức không hợp lệ.")
            return

    cat = models.Category(id=cat_id, name=name, type=cat_type, limit=limit)
    try:
        category_finance.add_category(cat)
        _print_result(f"  KẾT QUẢ: Thêm danh mục thanh cong. (ID={cat_id}, Ten={name}, Loai={cat_type})")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _update_category(category_finance):
    _print()
    _print("  -- SỬA DANH MỤC --")
    cat_id = _input("  Nhập tên danh mục cần sửa: ").strip()

    _print("  Trường có thể sửa: 1.Tên  2.Loại  3.Hạn mức")
    fields_raw = _input("  Chọn trường (VD: 1,3): ").strip()
    fields = [f.strip() for f in fields_raw.split(",")]

    new_name  = None
    new_type  = None
    new_limit = None

    if "1" in fields:
        new_name = _input("  Tên mới: ").strip()
    if "2" in fields:
        new_type = _input("  Loại mới (income/expense): ").strip().lower()
    if "3" in fields:
        raw = _input("  Hạn mức mới (đ): ").strip()
        try:
            new_limit = float(raw)
        except ValueError:
            _print_result("  KẾT QUẢ: Hạn mức không hợp lệ.")
            return

    try:
        category_finance.update_category(
            category_id=cat_id,
            new_name=new_name,
            new_type=new_type,
            new_limit=new_limit
        )
        _print_result(f"  KẾT QUẢ: Cập nhật danh mục {cat_id} thanh cong.")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _remove_category(category_finance):
    _print()
    _print("  -- XÓA DANH MỤC --")
    cat_id = _input("  Nhập tên danh mục cần xóa: ").strip()
    try:
        category_finance.remove_category(cat_id)
        _print_result(f"  KẾT QUẢ: Đã xóa (soft delete) danh mục {cat_id}.")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _search_category(category_finance):
    _print()
    _print("  -- TÌM KIẾM DANH MỤC --")
    _print("  Tìm theo: 1.ID  2.Tên  3.Loại")
    choice = _input("  Chọn: ").strip()
    cats   = category_finance.categories

    if choice == "1":
        cat_id = _input("  Nhập ID: ").strip()
        idx = category_finance.find_by_id(cats, cat_id)
        if idx == -1:
            _print_result("  KẾT QUẢ: Không tìm thấy.")
        else:
            _print_result("  KẾT QUẢ:")
            _print_category(cats[idx])

    elif choice == "2":
        name = _input("  Nhập tên: ").strip()
        idx = category_finance.find_by_name(cats, name)
        if idx == -1 or not cats[idx].is_active:
            _print_result("  KẾT QUẢ: Không tìm thấy.")
        else:
            _print_result("  KẾT QUẢ:")
            _print_category(cats[idx])

    elif choice == "3":
        cat_type = _input("  Nhập loại (income/expense): ").strip().lower()
        indices  = category_finance.find_by_type(cats, cat_type)
        if not indices:
            _print_result("  KẾT QUẢ: Không tìm thấy.")
        else:
            _print_result(f"  KẾT QUẢ: Tim thay {len(indices)} danh mục:")
            for i in indices:
                _print_category(cats[i])
    else:
        _print("  Lựa chọn không hợp lệ.")


def _list_all_categories(category_finance):
    _print()
    cats = [c for c in category_finance.categories if c.is_active]
    if not cats:
        _print_result("  KẾT QUẢ: Chua co danh muc nao.")
        return
    _print_result(f"  KẾT QUẢ: Danh sach {len(cats)} danh mục:")
    for cat in cats:
        _print_category(cat)

def _set_monthly_budget(finance_manager):
    _print()
    _print("  -- ĐẶT LẠI HẠN MỨC CHO THÁNG CỤ THỂ --")
    raw_year  = _input("  Năm  : ").strip()
    raw_month = _input("  Tháng: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KẾT QUẢ: Nam/thang khong hop le.")
        return
        
    _print("  -- Danh sách Danh mục chi tiêu --")
    active_cats = finance_manager._category_manager.get_active_categories()
    has_expense = False
    for c in active_cats:
        if c.is_active and c.type == "expense":
            _print(f"   - {c.name} (Hạn mức gốc: {c.limit:,.0f} d)")
            has_expense = True
            
    if not has_expense:
        _print("  (Chưa có danh mục chi tiêu nào)")
        return
        
    cat_id = _input("  Chọn danh mục (Nhập Tên): ").strip()
    raw_limit = _input("  Hạn mức mới (đ): ").strip()
    try:
        new_limit = float(raw_limit)
        finance_manager.set_monthly_budget(cat_id, year, month, new_limit)
        _print_result(f"  KẾT QUẢ: Da cap nhat han muc {new_limit:,.0f} d cho '{cat_id}' trong {month:02d}/{year}.")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")

# GIAO DICH (TRANSACTION)
def _menu_transaction(finance_manager):
    while True:
        _print()
        _print(_SEP)
        _print("  QUẢN LÝ GIAO DỊCH")
        _print(_SEP)
        _print("  1. Thêm giao dịch")
        _print("  2. Sửa giao dịch")
        _print("  3. Xóa giao dịch")
        _print("  4. Tìm kiếm giao dịch")
        _print("  5. Xem giao dịch theo tháng")
        _print("  6. Import giao dịch từ file (CSV)")
        _print("  0. Quay lại")
        _print(_LINE)
        choice = _input("  Chọn: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            _log_action("Thêm giao dịch")
            _add_transaction(finance_manager)
            file_io.save_data(finance_manager, finance_manager._category_manager)
        elif choice == "2":
            _log_action("Sửa giao dịch")
            _update_transaction(finance_manager)
            file_io.save_data(finance_manager, finance_manager._category_manager)
        elif choice == "3":
            _log_action("Xóa giao dịch")
            _delete_transaction(finance_manager)
            file_io.save_data(finance_manager, finance_manager._category_manager)
        elif choice == "4":
            _log_action("Tìm kiếm giao dịch")
            _search_transaction(finance_manager)
        elif choice == "5":
            _log_action("Xem giao dịch theo tháng")
            _view_monthly_transactions(finance_manager)
        elif choice == "6":
            _log_action("Import giao dịch từ file (CSV)")
            _import_transactions(finance_manager, finance_manager._category_manager)
        else:
            _print("  Lựa chọn không hợp lệ.")


def _add_transaction(finance_manager):
    _print()
    _print("  -- THÊM GIAO DỊCH --")
    
    # Tự động sinh mã giao dịch
    tx_id  = "TX" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    raw    = _input("  Số tiền (đ)      : ").strip()
    try:
        amount = float(raw)
    except ValueError:
        _print_result("  KẾT QUẢ: So tien khong hop le.")
        return
    date   = _input("  Ngày (dd-mm-yyyy): ").strip()
    note   = _input("  Ghi chú          : ").strip()
    
    suggested_cat = finance_manager.suggest_category_by_note(note)
    cat_id = None
    
    if suggested_cat:
        ans = _input(f"  ? Gợi ý: Ghi chú này có vẻ thuộc danh mục '{suggested_cat}'.\n  Bạn có muốn chọn mục '{suggested_cat}' không? (Enter/y để đồng ý, n để chọn mục khác): ").strip().lower()
        if ans == '' or ans == 'y':
            cat_id = suggested_cat
            
    if not cat_id:
        _print("  -- Danh sách Danh mục hiện có --")
        active_cats = finance_manager._category_manager.get_active_categories()
        has_active = False
        for c in active_cats:
            if c.is_active:
                _print(f"   - {c.name} ({c.type})")
                has_active = True
                
        if not has_active:
            _print("  (Chưa có danh mục nào, vui lòng tạo danh mục trước)")
            
        cat_id = _input("  Chọn danh mục (Nhập Tên): ").strip()

    try:
        is_exceeded = finance_manager.add_transaction(tx_id, amount, date, cat_id, note)
        _print_result(f"  KẾT QUẢ: Thêm giao dịch thanh cong. (ID={tx_id}, So tien={amount:,.0f}d, Ngay={date})")
        if is_exceeded:
            _print_result("  ⚠️ CẢNH BÁO: Giao dịch này làm vượt ngân sách tháng!")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _delete_transaction(finance_manager):
    _print()
    _print("  -- XÓA GIAO DỊCH --")
    tx_id = _input("  ID giao dịch cần xóa: ").strip()
    try:
        finance_manager.delete_transaction(tx_id)
        _print_result(f"  KẾT QUẢ: Đã xóa giao dich {tx_id}.")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _update_transaction(finance_manager):
    _print()
    _print("  -- SỬA GIAO DỊCH --")
    tx_id    = _input("  ID giao dịch cần sửa: ").strip()
    location = finance_manager._transaction_map.get(tx_id)

    if location is None:
        _print_result("  KẾT QUẢ: Lỗi - Transaction does not exist.")
        return

    year, month = location
    month_data  = finance_manager._month_index.get(year, month)
    tx_index    = index_services.TransactionIndex(month_data)
    idx         = tx_index.find_by_id(tx_id)
    old_tx      = tx_index._transactions[idx]

    _print("  Giao dịch hiện tại:")
    _print(_fmt_transaction(old_tx))

    _print("  Trường có thể sửa: 1.Số tiền  2.Ngày  3.Danh mục  4.Ghi chú")
    fields_raw = _input("  Chon truong (VD: 1,2): ").strip()
    fields = [f.strip() for f in fields_raw.split(",")]

    new_amount = old_tx.amount
    new_date   = _date_str(old_tx.date)
    new_cat_id = old_tx.category_id
    new_note   = old_tx.note

    if "1" in fields:
        raw = _input("  Số tiền mới (đ): ").strip()
        try:
            new_amount = float(raw)
        except ValueError:
            _print_result("  KẾT QUẢ: So tien khong hop le.")
            return
    if "2" in fields:
        new_date = _input("  Ngày mới (dd-mm-yyyy): ").strip()
    if "3" in fields:
        new_cat_id = _input("  ID danh mục mới: ").strip()
    if "4" in fields:
        new_note = _input("  Ghi chú mới: ").strip()

    try:
        is_exceeded = finance_manager.update_transaction(tx_id, new_amount, new_date, new_cat_id, new_note)
        _print_result(f"  KẾT QUẢ: Cap nhat giao dich {tx_id} thanh cong.")
        if is_exceeded:
            _print_result("  ⚠️ CẢNH BÁO: Giao dịch này làm vượt ngân sách tháng!")
    except ValueError as e:
        _print_result(f"  KẾT QUẢ: Lỗi - {e}")


def _search_transaction(finance_manager):
    _print()
    _print("  -- TÌM KIẾM GIAO DỊCH --")
    raw_year  = _input("  Năm  : ").strip()
    raw_month = _input("  Tháng: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KẾT QUẢ: Nam/thang khong hop le.")
        return

    month_data = finance_manager._month_index.get(year, month)
    if month_data is None:
        _print_result(f"  KẾT QUẢ: Khong co du lieu cho thang {month:02d}/{year}.")
        return

    tx_index = index_services.TransactionIndex(month_data)

    _print("  Tìm theo: 1.ID  2.Danh mục  3.Số tiền  4.Ghi chú  5.Ngày")
    choice = _input("  Chọn: ").strip()

    results = []

    if choice == "1":
        tx_id = _input("  Nhập ID giao dịch: ").strip()
        i = tx_index.find_by_id(tx_id)
        if i != -1:
            results = [tx_index._transactions[i]]

    elif choice == "2":
        cat_id  = _input("  Nhap ID danh mục: ").strip()
        results = [tx_index._transactions[i] for i in tx_index.find_by_category(cat_id)]

    elif choice == "3":
        raw = _input("  Nhập số tiền: ").strip()
        try:
            amount = float(raw)
        except ValueError:
            _print_result("  KẾT QUẢ: So tien khong hop le.")
            return
        results = [tx_index._transactions[i] for i in tx_index.find_by_amount(amount)]

    elif choice == "4":
        keyword = _input("  Nhập từ khóa ghi chú: ").strip()
        results = [tx_index._transactions[i] for i in tx_index.find_by_note(keyword)]

    elif choice == "5":
        date_str = _input("  Nhập ngày (dd-mm-yyyy): ").strip()
        try:
            search_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            _print_result("  KẾT QUẢ: Ngay khong hop le.")
            return
        first, last = tx_index.find_by_date(search_date)
        if first >= 0:
            results = tx_index._transactions[first:last + 1]
    else:
        _print("  Lựa chọn không hợp lệ.")
        return

    if not results:
        _print_result("  KẾT QUẢ: Không tìm thấy giao dich nao.")
    else:
        _print_result(f"  KẾT QUẢ: Tim thay {len(results)} giao dich:")
        for tx in results:
            _print_transaction(tx)


def _view_monthly_transactions(finance_manager):
    _print()
    _print("  -- XEM GIAO DỊCH THEO THÁNG --")
    raw_year  = _input("  Năm  : ").strip()
    raw_month = _input("  Tháng: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KẾT QUẢ: Nam/thang khong hop le.")
        return

    month_data = finance_manager._month_index.get(year, month)
    if month_data is None:
        _print_result(f"  KẾT QUẢ: Khong co du lieu cho thang {month:02d}/{year}.")
        return

    transactions = index_services.TransactionIndex(month_data).get_monthly_transactions(year, month)
    if not transactions:
        _print_result("  KẾT QUẢ: Khong co giao dich nao.")
    else:
        _print_result(f"  KẾT QUẢ: {len(transactions)} giao dịch trong tháng {month:02d}/{year}:")
        for tx in transactions:
            _print_transaction(tx)


def _import_transactions(finance_manager, category_finance):
    _print()
    _print("  -- IMPORT GIAO DICH TU FILE CSV --")
    file_path = _input("  Nhập đường dẫn file CSV (VD: import.csv): ").strip()
    
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            # Read first line to detect delimiter and header
            first_line = file.readline()
            file.seek(0)
            
            delimiter = ','
            if '|' in first_line:
                delimiter = '|'
                
            reader = csv.reader(file, delimiter=delimiter)
            success_count = 0
            
            header = next(reader, None)
            if not header:
                _print_result("  KẾT QUẢ: File CSV trống.")
                return
                
            header_clean = [col.strip().lower() for col in header]
            
            # Map column indices from header
            idx_date = -1
            idx_amount = -1
            idx_cat_name = -1
            idx_note = -1
            idx_tx_id = -1
            
            for idx, col in enumerate(header_clean):
                if 'date' in col or 'ngay' in col or 'ngày' in col:
                    idx_date = idx
                elif 'amount' in col or 'sotien' in col or 'số tiền' in col or 'so tien' in col:
                    idx_amount = idx
                elif 'category_name' in col or 'ten danh muc' in col or 'tên danh mục' in col or 'category name' in col:
                    idx_cat_name = idx
                elif 'note' in col or 'ghi chu' in col or 'ghi chú' in col:
                    idx_note = idx
                elif 'transaction_id' in col or 'ma gd' in col or 'mã gd' in col:
                    idx_tx_id = idx
            
            has_valid_mapping = (idx_date != -1 and idx_amount != -1 and idx_cat_name != -1)
            
            # Check if header is actually a data row (doesn't contain header keywords)
            is_header_actual_data = False
            first_cell = header_clean[0]
            if not (first_cell.startswith('#') or first_cell in ['transaction_id', 'date', 'ngay', 'ngày', 'ma gd', 'mã gd']):
                is_header_actual_data = True
                file.seek(0)
                reader = csv.reader(file, delimiter=delimiter)
                
            for line_num, row in enumerate(reader, 1 if is_header_actual_data else 2):
                if not row or len(row) < 3:
                    continue
                
                try:
                    if has_valid_mapping and not is_header_actual_data:
                        date_str = row[idx_date].strip()
                        amount_str = row[idx_amount].strip()
                        category_name = row[idx_cat_name].strip()
                        note = row[idx_note].strip() if idx_note != -1 and idx_note < len(row) else ""
                        tx_id_from_file = row[idx_tx_id].strip() if idx_tx_id != -1 and idx_tx_id < len(row) else None
                    else:
                        # Fallback based on column count
                        if len(row) >= 7:
                            tx_id_from_file = row[0].strip()
                            date_str = row[1].strip()
                            category_name = row[3].strip()
                            amount_str = row[5].strip()
                            note = row[6].strip()
                        else:
                            tx_id_from_file = None
                            date_str = row[0].strip()
                            amount_str = row[1].strip()
                            category_name = row[2].strip()
                            note = row[3].strip() if len(row) > 3 else ""
                except IndexError:
                    _print(f"  [Lỗi Dòng {line_num}] Thiếu cột dữ liệu. Bỏ qua.")
                    continue
                
                if date_str.lower() in ['date', 'ngay', 'ngày']:
                    continue
                
                # Normalize date separator from / to -
                date_str = date_str.replace('/', '-')
                
                cat_idx = category_finance.find_by_name(category_finance.categories, category_name)
                if cat_idx == -1:
                    _print(f"  [Lỗi Dòng {line_num}] Danh mục '{category_name}' không tồn tại. Bỏ qua.")
                    continue
                
                category_id = category_finance.categories[cat_idx].id
                
                try:
                    amount = float(amount_str)
                except ValueError:
                    _print(f"  [Lỗi Dòng {line_num}] Số tiền '{amount_str}' không hợp lệ. Bỏ qua.")
                    continue
                
                if tx_id_from_file:
                    transaction_id = tx_id_from_file
                else:
                    transaction_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                
                try:
                    finance_manager.add_transaction(transaction_id, amount, date_str, category_id, note)
                    success_count += 1
                except ValueError as e:
                    _print(f"  [Lỗi Dòng {line_num}] Thêm giao dịch thất bại: {e}")
            
            if success_count > 0:
                file_io.save_data(finance_manager, category_finance)
                
            _print_result(f"  KẾT QUẢ: Đã import thành công {success_count} giao dịch.")
            
    except FileNotFoundError:
        _print_result(f"  KẾT QUẢ: Lỗi - Không tìm thấy file '{file_path}'. Vui lòng kiểm tra lại.")
    except Exception as e:
        _print_result(f"  KẾT QUẢ: Lỗi hệ thống trong quá trình đọc file - {e}")


# BAO CAO
def _menu_report(finance_manager):
    _print()
    _print("  -- BÁO CÁO TÀI CHÍNH --")
    _print("  1. Báo cáo Ngày")
    _print("  2. Báo cáo Tháng")
    _print("  3. Báo cáo Năm")
    _print("  4. Báo cáo Tổng quan K tháng gần nhất")
    _print("  5. Chi tiết toàn bộ giao dịch K tháng gần nhất")
    choice = _input("  Chọn: ").strip()
    
    if choice not in ["1", "2", "3", "4", "5"]:
        _print("  Lựa chọn không hợp lệ.")
        return
        
    if choice == "4":
        raw_k = _input("  Nhập số tháng K (Mặc định 3): ").strip()
        if raw_k == "":
            k_months = 3
        else:
            try:
                k_months = int(raw_k)
                if k_months <= 0:
                    raise ValueError
            except ValueError:
                _print_result("  KẾT QUẢ: Số tháng phải là số nguyên dương.")
                return
                
        import builtins
        original_print = builtins.print
        report_lines   = []

        def _capture_print(*args, **kwargs):
            text = " ".join(str(a) for a in args)
            original_print(text)
            report_lines.append(text)

        builtins.print = _capture_print
        
        report_manager.ReportManager(finance_manager._month_index).generate_k_months_report(k_months)
        
        builtins.print = original_print
        for line in report_lines:
            _log(line)
        return
        
    elif choice == "5":
        raw_k = _input("  Nhập số tháng K (Mặc định 3): ").strip()
        if raw_k == "":
            k_months = 3
        else:
            try:
                k_months = int(raw_k)
                if k_months <= 0:
                    raise ValueError
            except ValueError:
                _print_result("  KẾT QUẢ: Số tháng phải là số nguyên dương.")
                return
                
        transactions = report_manager.ReportManager(finance_manager._month_index).get_k_months_transactions(k_months)
        
        _print()
        _print(f"  -- LỊCH SỬ GIAO DỊCH {k_months} THÁNG GẦN NHẤT --")
        if not transactions:
            _print_result("  KẾT QUẢ: Không có giao dịch nào trong khoảng thời gian này.")
            return
            
        category_mgr = finance_manager._category_manager
        
        for tx in transactions:
            date_str = _date_str(tx.date)
            sign = "+" if tx.transaction_type.lower() == "income" else "-"
            amt_str = f"{sign}{tx.amount:,.0f} đ"
            
            cat_idx = category_mgr.find_by_id(category_mgr.categories, tx.category_id)
            cat_name = category_mgr.categories[cat_idx].name if cat_idx != -1 else tx.category_id
            
            line = f"  {date_str} | {amt_str:<15} | {cat_name:<15} | {tx.note}"
            _print(line)
            _log(line)
        _print("-" * 55)
        return
        
    raw_year  = _input("  Năm  : ").strip()
    try:
        year  = int(raw_year)
    except ValueError:
        _print_result("  KẾT QUẢ: Nam khong hop le.")
        return

    import builtins
    original_print = builtins.print
    report_lines   = []

    def _capture_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        original_print(text)
        report_lines.append(text)

    builtins.print = _capture_print
        
    if choice == "1":
        raw_month = _input("  Tháng: ").strip()
        raw_day = _input("  Ngày : ").strip()
        try:
            month = int(raw_month)
            day = int(raw_day)
            report_manager.ReportManager(finance_manager._month_index).generate_daily_report(year, month, day)
        except ValueError:
            builtins.print = original_print
            _print_result("  KẾT QUẢ: Thang/ngay khong hop le.")
            return
    elif choice == "2":
        raw_month = _input("  Tháng: ").strip()
        try:
            month = int(raw_month)
            report_manager.ReportManager(finance_manager._month_index).generate_monthly_report(year, month)
        except ValueError:
            builtins.print = original_print
            _print_result("  KẾT QUẢ: Thang khong hop le.")
            return
    elif choice == "3":
        report_manager.ReportManager(finance_manager._month_index).generate_yearly_report(year)
        
    builtins.print = original_print

    for line in report_lines:
        _log(line)

# MENU CHÍNH
def main():
    finance_manager, category_finance = file_io.load_data()

    _print(_SEP)
    _print("  HỆ THỐNG QUẢN LÝ TÀI CHÍNH CÁ NHÂN")
    _print(_SEP)

    while True:
        total_balance = finance_manager.get_total_balance()
        
        _print()
        _print(_SEP)
        _print("  MENU CHÍNH")
        _print(f"  >> SỐ DƯ TÀI KHOẢN HIỆN TẠI: {total_balance:,.0f} đ <<")
        _print(_SEP)
        _print("  1. Quản lý Danh mục")
        _print("  2. Quản lý Giao dịch")
        _print("  3. Báo cáo tháng")
        _print("  0. Thoát")
        _print(_LINE)
        choice = _input("  Chọn: ").strip()

        if choice == "0":
            _print("  Thoát chương trình. Tạm biệt!")
            break
        elif choice == "1":
            _log_action("Menu: Quản lý Danh mục")
            _menu_category(finance_manager, category_finance)
        elif choice == "2":
            _log_action("Menu: Quản lý Giao dịch")
            _menu_transaction(finance_manager)
        elif choice == "3":
            _log_action("Menu: Báo cáo tháng")
            _menu_report(finance_manager)
        else:
            _print("  Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
