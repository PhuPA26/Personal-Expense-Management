from data import index_services
from core import models
import datetime


class FinanceManager:
    def __init__(self, category_manager):
        self._month_index = index_services.MonthIndex()
        self._transaction_map = index_services.TransactionMap()
        self._category_manager = category_manager

    def _get_or_create_category_state(self, category_index, category, year, month):
        state = category_index.get(category.id)
        if state is None:
            if category.type.lower() == "income":
                state = models.IncomeState(category, year, month)
            else:
                state = models.ExpenseState(category, year, month, category.limit)
            category_index.add(state)
        return state

    def _is_state_empty(self, state):
        if isinstance(state, models.ExpenseState):
            return state.total_expense == 0
        elif isinstance(state, models.IncomeState):
            return state.total_income == 0
        return False

    def get_total_balance(self):
        total_income = 0
        total_expense = 0
        
        for month_data in self._month_index._months.values():
            for state_id in month_data.category_states.keys():
                state = month_data.category_states.get(state_id)
                if isinstance(state, models.IncomeState):
                    total_income += state.total_income
                elif isinstance(state, models.ExpenseState):
                    total_expense += state.total_expense
                    
        return total_income - total_expense

    def set_monthly_budget(self, category_id, year, month, new_limit):
        if new_limit < 0:
            raise ValueError("Limit cannot be negative.")
            
        category = self._check_category(category_id)
        if category.type.lower() != "expense":
            raise ValueError("Can only set budget for expense categories.")
            
        month_data = self._month_index.get_or_create(year, month)
        category_index = index_services.CategoryIndex(month_data)
        
        category_state = self._get_or_create_category_state(category_index, category, year, month)
        if isinstance(category_state, models.ExpenseState):
            category_state.set_limit(new_limit)

    def suggest_category_by_note(self, note):
        if not note or not note.strip():
            return None
            
        note_lower = note.strip().lower()
        keys = self._month_index._months.keys()
        
        parsed_keys = []
        for k in keys:
            if k:
                parts = k.split("-")
                if len(parts) == 2:
                    parsed_keys.append((int(parts[0]), int(parts[1]), k))
                    
        parsed_keys.sort(reverse=True)
        
        for y, m, k in parsed_keys:
            month_data = self._month_index._months.get(k)
            if month_data and hasattr(month_data, 'transactions'):
                for tx in reversed(month_data.transactions):
                    if tx.note:
                        tx_note_lower = tx.note.strip().lower()
                        if tx_note_lower and (note_lower in tx_note_lower or tx_note_lower in note_lower):
                            return tx.category_id
        return None

    def _check_transaction_id(self, transaction_id):

        if self._transaction_map.exists(transaction_id):
            raise ValueError("Transaction ID already exists.")

    def _check_amount(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

    def _parse_and_validate_date(self, date_str):

        try:
            parsed_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Date must be in format dd-mm-yyyy and be valid.")

        if parsed_date > datetime.date.today():
            raise ValueError("Date cannot be in the future.")

        return parsed_date
    
    def _check_category(self, category_id):

        index = self._category_manager.find_by_id(
            self._category_manager.categories,
            category_id
        )

        if index == -1:
            raise ValueError("Category does not exist.")

        category = self._category_manager.categories[index]
        if not category.is_active:
            raise ValueError("Category is inactive.")

        return category
    
    def add_transaction(
            self,
            transaction_id,
            amount,
            date,
            category_id,
            note=""
    ):
        # Kiểm tra dữ liệu
        self._check_transaction_id(transaction_id)

        self._check_amount(amount)
        parsed_date = self._parse_and_validate_date(date)
        category = self._check_category(category_id)

        year = parsed_date.year
        month = parsed_date.month

        # Lấy dữ liệu tháng
        month_data = self._month_index.get_or_create(year, month)

        transaction_index = index_services.TransactionIndex(month_data)
        category_index = index_services.CategoryIndex(month_data)

        # Tạo Transaction
        transaction = models.Transaction(
            transaction_id,
            amount,
            parsed_date,
            category_id,
            category.type,
            note
        )

        # Thêm Transaction
        transaction_index.add(transaction)

        # Thêm vào TransactionMap
        self._transaction_map.add(
            transaction_id,
            year,
            month
        )

        # Lấy hoặc tạo CategoryState
        category_state = self._get_or_create_category_state(category_index, category, year, month)

        # Cập nhật thống kê
        category_state.update_transaction(
            new_amount=amount,
            mode="add"
        )

        is_budget_exceeded = False
        if (
            isinstance(category_state, models.ExpenseState)
            and category_state.total_expense > category_state.limit
        ):
            is_budget_exceeded = True

        return is_budget_exceeded

    def delete_transaction(self, transaction_id):

        # Kiểm tra Transaction
        location = self._transaction_map.get(transaction_id)

        if location is None:
            raise ValueError("Transaction does not exist.")

        year, month = location

        # Lấy dữ liệu tháng
        month_data = self._month_index.get(year, month)

        transaction_index = index_services.TransactionIndex(month_data)
        category_index = index_services.CategoryIndex(month_data)


        # Tìm Transaction
        transaction = transaction_index.get_transaction(transaction_id)
        if transaction is None:
            raise ValueError("Transaction not found in index.")

        # Cập nhật CategoryState
        category_state = category_index.get(transaction.category_id)

        category_state.update_transaction(
            old_amount=transaction.amount,
            mode="delete"
        )

        if self._is_state_empty(category_state):
            category_index.remove(transaction.category_id)

        # Xóa Transaction
        transaction_index.remove(transaction_id)

        # Xóa khỏi TransactionMap
        self._transaction_map.remove(transaction_id)

        print("Transaction deleted successfully.")

    def update_transaction(
            self,
            transaction_id,
            amount=None,
            date=None,
            category_id=None,
            note=None
    ):


        # Kiểm tra transaction tồn tại
        location = self._transaction_map.get(transaction_id)

        if location is None:
            raise ValueError("Transaction does not exist.")

        old_year, old_month = location

        # Lấy transaction cũ
        old_month_data = self._month_index.get(old_year, old_month)

        old_transaction_index = index_services.TransactionIndex(old_month_data)
        old_category_index = index_services.CategoryIndex(old_month_data)

        transaction = old_transaction_index.get_transaction(transaction_id)
        if transaction is None:
            raise ValueError("Transaction does not exist in index.")

        old_amount = transaction.amount
        old_date = transaction.date
        old_category_id = transaction.category_id

        old_category_state = old_category_index.get(old_category_id)

        # VALIDATE UPDATE FIELDS
        if amount is not None:
            self._check_amount(amount)

        if date is not None:
            parsed_date = self._parse_and_validate_date(date)
        else:
            parsed_date = old_date

        if category_id is not None:
            new_category = self._check_category(category_id)
        else:
            new_category = self._check_category(transaction.category_id)

        new_year = parsed_date.year
        new_month = parsed_date.month

        # RESET DEFAULT VALUES
        new_amount = amount if amount is not None else old_amount
        new_note = note if note is not None else transaction.note

        # TRƯỜNG HỢP ĐỔI THÁNG
        is_budget_exceeded = False
        if old_year != new_year or old_month != new_month:

            # remove old stats
            old_category_state.update_transaction(
                old_amount=old_amount,
                mode="delete"
            )

            if self._is_state_empty(old_category_state):
                old_category_index.remove(old_category_id)

            old_transaction_index.remove(transaction_id)

            new_month_data = self._month_index.get_or_create(new_year, new_month)

            new_transaction_index = index_services.TransactionIndex(new_month_data)
            new_category_index = index_services.CategoryIndex(new_month_data)

            # update transaction
            transaction.amount = new_amount
            transaction.date = parsed_date
            transaction.category_id = new_category.id
            transaction.transaction_type = new_category.type
            transaction.note = new_note

            new_transaction_index.add(transaction)

            self._transaction_map.add(transaction_id, new_year, new_month)

            # category state new month
            new_category_state = self._get_or_create_category_state(
                new_category_index, new_category, new_year, new_month
            )

            new_category_state.update_transaction(
                new_amount=new_amount,
                mode="add"
            )

            if isinstance(new_category_state, models.ExpenseState):
                if new_category_state.total_expense > new_category_state.limit:
                    is_budget_exceeded = True


        # KHÔNG ĐỔI THÁNG
        else:

            # đổi category
            if old_category_id != new_category.id:

                old_category_state.update_transaction(
                    old_amount=old_amount,
                    mode="delete"
                )

                if self._is_state_empty(old_category_state):
                    old_category_index.remove(old_category_id)

                new_category_state = self._get_or_create_category_state(
                    old_category_index, new_category, old_year, old_month
                )

                new_category_state.update_transaction(
                    new_amount=new_amount,
                    mode="add"
                )

                if isinstance(new_category_state, models.ExpenseState):
                    if new_category_state.total_expense > new_category_state.limit:
                        is_budget_exceeded = True

            else:

                old_category_state.update_transaction(
                    old_amount=old_amount,
                    new_amount=new_amount,
                    mode="update"
                )

                if isinstance(old_category_state, models.ExpenseState):
                    if old_category_state.total_expense > old_category_state.limit:
                        is_budget_exceeded = True

            # relocate nếu đổi ngày
            if old_date != parsed_date:
                old_transaction_index.relocate(transaction_id, parsed_date)

            # update transaction fields
            transaction.amount = new_amount
            transaction.category_id = new_category.id
            transaction.transaction_type = new_category.type
            transaction.note = new_note

        return is_budget_exceeded
