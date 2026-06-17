import datetime
import TransactionManager
import CategoryManager as CatMgr
import HashMap
import model
import Report

# ================================================================
# LOG — chỉ ghi đầu vào người dùng nhập + đầu ra kết quả
_LOG_FILE = "InputOutput.txt"
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


# ================================================================
# LƯU / NẠP DỮ LIỆU (ROM)
# ================================================================

_SAVE_FILE = "data.txt"


def _ser_category(cat):
    active = "1" if cat.is_active else "0"
    return f"{cat.id}|{cat.name}|{cat.type}|{cat.limit}|{active}"


def _ser_transaction(tx):
    date_str = tx.date.strftime("%Y-%m-%d") if hasattr(tx.date, "strftime") else str(tx.date)
    note = tx.note.replace("|", "\\|").replace("\n", "\\n")
    return f"{tx.transaction_id}|{tx.amount}|{date_str}|{tx.category_id}|{tx.transaction_type}|{note}"


def _save(finance_manager, category_finance):
    lines = []
    lines.append("BEGIN_CATEGORIES")
    for cat in category_finance.categories:
        lines.append(_ser_category(cat))
    lines.append("END_CATEGORIES")

    lines.append("BEGIN_TRANSACTIONS")
    month_hm = finance_manager._month_index._months
    for key in month_hm.keys():
        month_data = month_hm.get(key)
        for tx in month_data.transactions:
            lines.append(_ser_transaction(tx))
    lines.append("END_TRANSACTIONS")

    f = open(_SAVE_FILE, "w", encoding="utf-8")
    f.write("\n".join(lines))
    f.close()


def _load():
    fm = TransactionManager.FinanceManager()
    cf = CatMgr.CategoryFinance()
    fm._category_manager = cf

    try:
        f = open(_SAVE_FILE, "r", encoding="utf-8")
        content = f.read()
        f.close()
    except IOError:
        return fm, cf

    lines = content.splitlines()
    mode = None

    for line in lines:
        line = line.strip()
        if line == "BEGIN_CATEGORIES":
            mode = "cat"; continue
        if line == "END_CATEGORIES":
            mode = None; continue
        if line == "BEGIN_TRANSACTIONS":
            mode = "tx"; continue
        if line == "END_TRANSACTIONS":
            mode = None; continue

        if mode == "cat" and line:
            parts = line.split("|")
            if len(parts) < 5:
                continue
            cat_id, name, cat_type, limit_str, active_str = parts[0], parts[1], parts[2], parts[3], parts[4]
            try:
                limit = float(limit_str)
            except ValueError:
                limit = 0
            cat = model.Category(
                id=cat_id, name=name, type=cat_type,
                limit=limit, is_active=(active_str == "1")
            )
            cf.categories.append(cat)

        elif mode == "tx" and line:
            parts = line.split("|")
            if len(parts) < 6:
                continue
            tx_id       = parts[0]
            amount_str  = parts[1]
            date_str    = parts[2]
            category_id = parts[3]
            tx_type     = parts[4]
            note        = "|".join(parts[5:]).replace("\\|", "|").replace("\\n", "\n")
            try:
                amount = float(amount_str)
                date   = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            year  = date.year
            month = date.month
            month_data        = fm._month_index.get_or_create(year, month)
            transaction_index = HashMap.TransactionIndex(month_data)
            category_index    = HashMap.CategoryIndex(month_data)

            tx = model.Transaction(tx_id, amount, date, category_id, tx_type, note)
            transaction_index.add(tx)
            fm._transaction_map.add(tx_id, year, month)

            idx = cf.find_by_id(cf.categories, category_id)
            if idx == -1:
                continue
            cat = cf.categories[idx]
            category_state = category_index.get(cat.id)
            if category_state is None:
                if cat.type.upper() == "INCOME":
                    category_state = model.IncomeState(cat, year, month)
                else:
                    category_state = model.ExpenseState(cat, year, month, cat.limit)
                category_index.add(category_state)
            category_state.update_transaction(new_amount=amount, mode="add")

    return fm, cf

# TIỆN ÍCH HIỂN THỊ
_SEP  = "=" * 58
_LINE = "-" * 58

def _date_str(date):
    return date.strftime("%d-%m-%Y") if hasattr(date, "strftime") else str(date)


def _fmt_category(cat):
    status    = "Hoat dong" if cat.is_active else "Da xoa"
    limit_str = f"{cat.limit:,.0f} d" if cat.type == "expense" else "---"
    return (f"  ID: {cat.id:<12} | Ten: {cat.name:<15} | "
            f"Loai: {cat.type:<8} | Han muc: {limit_str:<15} | {status}")


def _fmt_transaction(tx):
    return (f"  ID: {tx.transaction_id:<12} | Ngay: {_date_str(tx.date)} | "
            f"So tien: {tx.amount:>15,.0f} d | Cat: {tx.category_id:<12} | Ghi chu: {tx.note}")


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
        _print("  QUAN LY DANH MUC")
        _print(_SEP)
        _print("  1. Them danh muc")
        _print("  2. Sua danh muc")
        _print("  3. Xoa danh muc (soft delete)")
        _print("  4. Tim kiem danh muc")
        _print("  5. Xem tat ca danh muc")
        _print("  0. Quay lai")
        _print(_LINE)
        choice = _input("  Chon: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            _log_action("Them danh muc")
            _add_category(category_finance)
            _save(finance_manager, category_finance)
        elif choice == "2":
            _log_action("Sua danh muc")
            _update_category(category_finance)
            _save(finance_manager, category_finance)
        elif choice == "3":
            _log_action("Xoa danh muc")
            _remove_category(category_finance)
            _save(finance_manager, category_finance)
        elif choice == "4":
            _log_action("Tim kiem danh muc")
            _search_category(category_finance)
        elif choice == "5":
            _log_action("Xem tat ca danh muc")
            _list_all_categories(category_finance)
        else:
            _print("  Lua chon khong hop le.")


def _add_category(category_finance):
    _print()
    _print("  -- THEM DANH MUC --")
    cat_id   = _input("  ID danh muc          : ").strip()
    name     = _input("  Ten danh muc         : ").strip()
    cat_type = _input("  Loai (income/expense): ").strip().lower()
    limit    = 0
    if cat_type == "expense":
        raw = _input("  Han muc (d)          : ").strip()
        try:
            limit = float(raw)
        except ValueError:
            _print_result("  KET QUA: Han muc khong hop le.")
            return

    cat = model.Category(id=cat_id, name=name, type=cat_type, limit=limit)
    try:
        category_finance.add_category(cat)
        _print_result(f"  KET QUA: Them danh muc thanh cong. (ID={cat_id}, Ten={name}, Loai={cat_type})")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _update_category(category_finance):
    _print()
    _print("  -- SUA DANH MUC --")
    cat_id = _input("  ID danh muc can sua: ").strip()

    _print("  Truong co the sua: 1.Ten  2.Loai  3.Han muc")
    fields_raw = _input("  Chon truong (VD: 1,3): ").strip()
    fields = [f.strip() for f in fields_raw.split(",")]

    new_name  = None
    new_type  = None
    new_limit = None

    if "1" in fields:
        new_name = _input("  Ten moi: ").strip()
    if "2" in fields:
        new_type = _input("  Loai moi (income/expense): ").strip().lower()
    if "3" in fields:
        raw = _input("  Han muc moi (d): ").strip()
        try:
            new_limit = float(raw)
        except ValueError:
            _print_result("  KET QUA: Han muc khong hop le.")
            return

    try:
        category_finance.update_category(
            category_id=cat_id,
            new_name=new_name,
            new_type=new_type,
            new_limit=new_limit
        )
        _print_result(f"  KET QUA: Cap nhat danh muc {cat_id} thanh cong.")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _remove_category(category_finance):
    _print()
    _print("  -- XOA DANH MUC --")
    cat_id = _input("  ID danh muc can xoa: ").strip()
    try:
        category_finance.remove_category(cat_id)
        _print_result(f"  KET QUA: Da xoa (soft delete) danh muc {cat_id}.")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _search_category(category_finance):
    _print()
    _print("  -- TIM KIEM DANH MUC --")
    _print("  Tim theo: 1.ID  2.Ten  3.Loai")
    choice = _input("  Chon: ").strip()
    cats   = category_finance.categories

    if choice == "1":
        cat_id = _input("  Nhap ID: ").strip()
        idx = category_finance.find_by_id(cats, cat_id)
        if idx == -1:
            _print_result("  KET QUA: Khong tim thay.")
        else:
            _print_result("  KET QUA:")
            _print_category(cats[idx])

    elif choice == "2":
        name = _input("  Nhap ten: ").strip()
        idx = category_finance.find_by_name(cats, name)
        if idx == -1 or not cats[idx].is_active:
            _print_result("  KET QUA: Khong tim thay.")
        else:
            _print_result("  KET QUA:")
            _print_category(cats[idx])

    elif choice == "3":
        cat_type = _input("  Nhap loai (income/expense): ").strip().lower()
        indices  = category_finance.find_by_type(cats, cat_type)
        if not indices:
            _print_result("  KET QUA: Khong tim thay.")
        else:
            _print_result(f"  KET QUA: Tim thay {len(indices)} danh muc:")
            for i in indices:
                _print_category(cats[i])
    else:
        _print("  Lua chon khong hop le.")


def _list_all_categories(category_finance):
    _print()
    cats = [c for c in category_finance.categories if c.is_active]
    if not cats:
        _print_result("  KET QUA: Chua co danh muc nao.")
        return
    _print_result(f"  KET QUA: Danh sach {len(cats)} danh muc:")
    for cat in cats:
        _print_category(cat)

# GIAO DICH (TRANSACTION)
def _menu_transaction(finance_manager):
    while True:
        _print()
        _print(_SEP)
        _print("  QUAN LY GIAO DICH")
        _print(_SEP)
        _print("  1. Them giao dich")
        _print("  2. Sua giao dich")
        _print("  3. Xoa giao dich")
        _print("  4. Tim kiem giao dich")
        _print("  5. Xem giao dich theo thang")
        _print("  0. Quay lai")
        _print(_LINE)
        choice = _input("  Chon: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            _log_action("Them giao dich")
            _add_transaction(finance_manager)
            _save(finance_manager, finance_manager._category_manager)
        elif choice == "2":
            _log_action("Sua giao dich")
            _update_transaction(finance_manager)
            _save(finance_manager, finance_manager._category_manager)
        elif choice == "3":
            _log_action("Xoa giao dich")
            _delete_transaction(finance_manager)
            _save(finance_manager, finance_manager._category_manager)
        elif choice == "4":
            _log_action("Tim kiem giao dich")
            _search_transaction(finance_manager)
        elif choice == "5":
            _log_action("Xem giao dich theo thang")
            _view_monthly_transactions(finance_manager)
        else:
            _print("  Lua chon khong hop le.")


def _add_transaction(finance_manager):
    _print()
    _print("  -- THEM GIAO DICH --")
    tx_id  = _input("  ID giao dich     : ").strip()
    raw    = _input("  So tien (d)      : ").strip()
    try:
        amount = float(raw)
    except ValueError:
        _print_result("  KET QUA: So tien khong hop le.")
        return
    date   = _input("  Ngay (dd-mm-yyyy): ").strip()
    cat_id = _input("  ID danh muc      : ").strip()
    note   = _input("  Ghi chu          : ").strip()

    try:
        finance_manager.add_transaction(tx_id, amount, date, cat_id, note)
        _print_result(f"  KET QUA: Them giao dich thanh cong. (ID={tx_id}, So tien={amount:,.0f}d, Ngay={date})")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _delete_transaction(finance_manager):
    _print()
    _print("  -- XOA GIAO DICH --")
    tx_id = _input("  ID giao dich can xoa: ").strip()
    try:
        finance_manager.delete_transaction(tx_id)
        _print_result(f"  KET QUA: Da xoa giao dich {tx_id}.")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _update_transaction(finance_manager):
    _print()
    _print("  -- SUA GIAO DICH --")
    tx_id    = _input("  ID giao dich can sua: ").strip()
    location = finance_manager._transaction_map.get(tx_id)

    if location is None:
        _print_result("  KET QUA: Loi - Transaction does not exist.")
        return

    year, month = location
    month_data  = finance_manager._month_index.get(year, month)
    tx_index    = HashMap.TransactionIndex(month_data)
    idx         = tx_index.find_by_id(tx_id)
    old_tx      = tx_index._transactions[idx]

    _print("  Giao dich hien tai:")
    _print(_fmt_transaction(old_tx))

    _print("  Truong co the sua: 1.So tien  2.Ngay  3.Danh muc  4.Ghi chu")
    fields_raw = _input("  Chon truong (VD: 1,2): ").strip()
    fields = [f.strip() for f in fields_raw.split(",")]

    new_amount = old_tx.amount
    new_date   = _date_str(old_tx.date)
    new_cat_id = old_tx.category_id
    new_note   = old_tx.note

    if "1" in fields:
        raw = _input("  So tien moi (d): ").strip()
        try:
            new_amount = float(raw)
        except ValueError:
            _print_result("  KET QUA: So tien khong hop le.")
            return
    if "2" in fields:
        new_date = _input("  Ngay moi (dd-mm-yyyy): ").strip()
    if "3" in fields:
        new_cat_id = _input("  ID danh muc moi: ").strip()
    if "4" in fields:
        new_note = _input("  Ghi chu moi: ").strip()

    try:
        finance_manager.update_transaction(tx_id, new_amount, new_date, new_cat_id, new_note)
        _print_result(f"  KET QUA: Cap nhat giao dich {tx_id} thanh cong.")
    except ValueError as e:
        _print_result(f"  KET QUA: Loi - {e}")


def _search_transaction(finance_manager):
    _print()
    _print("  -- TIM KIEM GIAO DICH --")
    raw_year  = _input("  Nam  : ").strip()
    raw_month = _input("  Thang: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KET QUA: Nam/thang khong hop le.")
        return

    month_data = finance_manager._month_index.get(year, month)
    if month_data is None:
        _print_result(f"  KET QUA: Khong co du lieu cho thang {month:02d}/{year}.")
        return

    tx_index = HashMap.TransactionIndex(month_data)

    _print("  Tim theo: 1.ID  2.Danh muc  3.So tien  4.Ghi chu  5.Ngay")
    choice = _input("  Chon: ").strip()

    results = []

    if choice == "1":
        tx_id = _input("  Nhap ID giao dich: ").strip()
        i = tx_index.find_by_id(tx_id)
        if i != -1:
            results = [tx_index._transactions[i]]

    elif choice == "2":
        cat_id  = _input("  Nhap ID danh muc: ").strip()
        results = [tx_index._transactions[i] for i in tx_index.find_by_category(cat_id)]

    elif choice == "3":
        raw = _input("  Nhap so tien: ").strip()
        try:
            amount = float(raw)
        except ValueError:
            _print_result("  KET QUA: So tien khong hop le.")
            return
        results = [tx_index._transactions[i] for i in tx_index.find_by_amount(amount)]

    elif choice == "4":
        keyword = _input("  Nhap tu khoa ghi chu: ").strip()
        results = [tx_index._transactions[i] for i in tx_index.find_by_note(keyword)]

    elif choice == "5":
        date_str = _input("  Nhap ngay (dd-mm-yyyy): ").strip()
        try:
            search_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            _print_result("  KET QUA: Ngay khong hop le.")
            return
        first, last = tx_index.find_by_date(search_date)
        if first >= 0:
            results = tx_index._transactions[first:last + 1]
    else:
        _print("  Lua chon khong hop le.")
        return

    if not results:
        _print_result("  KET QUA: Khong tim thay giao dich nao.")
    else:
        _print_result(f"  KET QUA: Tim thay {len(results)} giao dich:")
        for tx in results:
            _print_transaction(tx)


def _view_monthly_transactions(finance_manager):
    _print()
    _print("  -- XEM GIAO DICH THEO THANG --")
    raw_year  = _input("  Nam  : ").strip()
    raw_month = _input("  Thang: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KET QUA: Nam/thang khong hop le.")
        return

    month_data = finance_manager._month_index.get(year, month)
    if month_data is None:
        _print_result(f"  KET QUA: Khong co du lieu cho thang {month:02d}/{year}.")
        return

    transactions = HashMap.TransactionIndex(month_data).get_monthly_transactions(year, month)
    if not transactions:
        _print_result("  KET QUA: Khong co giao dich nao.")
    else:
        _print_result(f"  KET QUA: {len(transactions)} giao dich trong thang {month:02d}/{year}:")
        for tx in transactions:
            _print_transaction(tx)

# BAO CAO
def _menu_report(finance_manager):
    _print()
    _print("  -- BAO CAO TAI CHINH --")
    raw_year  = _input("  Nam  : ").strip()
    raw_month = _input("  Thang: ").strip()
    try:
        year  = int(raw_year)
        month = int(raw_month)
    except ValueError:
        _print_result("  KET QUA: Nam/thang khong hop le.")
        return

    _log(f"\n[KET QUA] Bao cao thang {month:02d}/{year}")
    _log("-" * 40)

    # Capture output của Report bằng cách override print tạm thời
    import builtins
    original_print = builtins.print
    report_lines   = []

    def _capture_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        original_print(text)
        report_lines.append(text)

    builtins.print = _capture_print
    Report.ReportManager(finance_manager._month_index).generate_monthly_report(year, month)
    builtins.print = original_print

    for line in report_lines:
        _log(line)

# MENU CHINH
def main():
    finance_manager, category_finance = _load()

    _print(_SEP)
    _print("  HE THONG QUAN LY TAI CHINH CA NHAN")
    _print(_SEP)

    while True:
        _print()
        _print(_SEP)
        _print("  MENU CHINH")
        _print(_SEP)
        _print("  1. Quan ly Danh muc")
        _print("  2. Quan ly Giao dich")
        _print("  3. Bao cao thang")
        _print("  0. Thoat")
        _print(_LINE)
        choice = _input("  Chon: ").strip()

        if choice == "0":
            _print("  Thoat chuong trinh. Tam biet!")
            break
        elif choice == "1":
            _log_action("Menu: Quan ly Danh muc")
            _menu_category(finance_manager, category_finance)
        elif choice == "2":
            _log_action("Menu: Quan ly Giao dich")
            _menu_transaction(finance_manager)
        elif choice == "3":
            _log_action("Menu: Bao cao thang")
            _menu_report(finance_manager)
        else:
            _print("  Lua chon khong hop le.")


if __name__ == "__main__":
    main()