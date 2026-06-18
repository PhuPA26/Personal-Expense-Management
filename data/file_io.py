import datetime
from services import transaction_manager
from services import category_manager
from data import index_services
from core import models

_SAVE_FILE = "storage/data.txt"

def _ser_category(cat):
    active = "1" if cat.is_active else "0"
    return f"{cat.id}|{cat.name}|{cat.type}|{cat.limit}|{active}"

def _ser_transaction(tx):
    date_str = tx.date.strftime("%Y-%m-%d") if hasattr(tx.date, "strftime") else str(tx.date)
    note = tx.note.replace("|", "\\|").replace("\n", "\\n")
    return f"{tx.transaction_id}|{tx.amount}|{date_str}|{tx.category_id}|{tx.transaction_type}|{note}"

def save_data(finance_manager, category_finance):
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

def load_data():
    cf = category_manager.CategoryFinance()
    fm = transaction_manager.FinanceManager(cf)

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
            cat = models.Category(
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
            transaction_index = index_services.TransactionIndex(month_data)
            category_index    = index_services.CategoryIndex(month_data)

            tx = models.Transaction(tx_id, amount, date, category_id, tx_type, note)
            transaction_index.add(tx)
            fm._transaction_map.add(tx_id, year, month)

            idx = cf.find_by_id(cf.categories, category_id)
            if idx == -1:
                continue
            cat = cf.categories[idx]
            category_state = category_index.get(cat.id)
            if category_state is None:
                if cat.type.upper() == "INCOME":
                    category_state = models.IncomeState(cat, year, month)
                else:
                    category_state = models.ExpenseState(cat, year, month, cat.limit)
                category_index.add(category_state)
            category_state.update_transaction(new_amount=amount, mode="add")

    return fm, cf
