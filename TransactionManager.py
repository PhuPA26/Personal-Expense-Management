import HashMap
import model
import CTDL
import datetime


class FinanceManager:
    def __init__(self):
        self._month_index = HashMap.MonthIndex()
        self._transaction_map = HashMap.TransactionMap()
        self._category_manager = HashMap.CategoryManager()

    def _check_transaction_id(self, transaction_id):

        if self._transaction_map.exists(transaction_id):
            raise ValueError("Transaction ID already exists.")

    def _check_transaction_data(self, amount, date, category_id):

        # Kiểm tra Amount
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        # Kiểm tra Date
        try:
            check_date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Date must be in format dd-mm-yyyy and be valid.")

        if check_date > datetime.date.today():
            raise ValueError("Date cannot be in the future.")

        # Kiểm tra Category
        index = self._category_manager.find_by_id(
            self._category_manager.categories,
            category_id
        )

        if index == -1:
            raise ValueError("Category does not exist.")

        category = self._category_manager.categories[index]

        return check_date, category

    def _check_amount(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

    def _check_date(self, date):

        try:
            check_date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Date must be in format dd-mm-yyyy and be valid.")

        if check_date > datetime.date.today():
            raise ValueError("Date cannot be in the future.")

        return check_date

    def _check_category(self, category_id):

        index = self._category_manager.find_by_id(
            self._category_manager.categories,
            category_id
        )

        if index == -1:
            raise ValueError("Category does not exist.")

        return self._category_manager.categories[index]
    
    def add_transaction(
            self,
            transaction_id,
            amount,
            date,
            category_id,
            note=""
    ):



        self._check_transaction_id(transaction_id)

        self._check_amount(amount)
        check_date = self._check_date(date)
        category = self._check_category(category_id)

        year = check_date.year
        month = check_date.month

        # Lấy dữ liệu tháng
        month_data = self._month_index.get_or_create(year, month)

        transaction_index = HashMap.TransactionIndex(month_data)
        category_index = HashMap.CategoryIndex(month_data)

        transaction = model.Transaction(
            transaction_id,
            amount,
            check_date,
            category_id,
            category.type,
            note
        )

        transaction_index.add(transaction)

        # Thêm vào TransactionMap
        self._transaction_map.add(
            transaction_id,
            year,
            month
        )

        category_state = category_index.get(category.id)

        if category_state is None:

            if category.type.upper() == "INCOME":

                category_state = model.IncomeState(
                    category,
                    year,
                    month
                )

            else:

                category_state = model.ExpenseState(
                    category,
                    year,
                    month,
                    category.limit
                )

            category_index.add(category_state)

        # Cập nhật thống kê

        category_state.update_transaction(
            new_amount=amount,
            mode="add"
        )
        
        # Kiểm tra Budget

        if (
            isinstance(category_state, model.ExpenseState)
            and category_state.total_expense > category_state.limit
        ):
            print("Warning: Budget exceeded!")

        print("Transaction added successfully.")

    def delete_transaction(self, transaction_id):
        # Kiểm tra Transaction

        location = self._transaction_map.get(transaction_id)

        if location is None:
            raise ValueError("Transaction does not exist.")

        year, month = location
        # Lấy dữ liệu tháng

        month_data = self._month_index.get(year, month)

        transaction_index = HashMap.TransactionIndex(month_data)
        category_index = HashMap.CategoryIndex(month_data)

        # Tìm Transaction

        index = transaction_index.find_by_id(transaction_id)

        transaction = transaction_index._transactions[index]
        # Cập nhật CategoryState

        category_state = category_index.get(transaction.category_id)

        category_state.update_transaction(
            old_amount=transaction.amount,
            mode="delete"
        )
        # Xóa Transaction

        transaction_index.remove(transaction_id)

        # Xóa khỏi TransactionMap
        self._transaction_map.remove(transaction_id)

        print("Transaction deleted successfully.")

    def update_transaction(
            self,
            transaction_id,
            amount,
            date,
            category_id,
            note=""
    ):
        # Kiểm tra Transaction

        location = self._transaction_map.get(transaction_id)

        if location is None:
            raise ValueError("Transaction does not exist.")

        old_year, old_month = location
        # Kiểm tra dữ liệu mới

        self._check_amount(amount)
        check_date = self._check_date(date)
        new_category = self._check_category(category_id)

        new_year = check_date.year
        new_month = check_date.month
        # Lấy dữ liệu tháng cũ

        old_month_data = self._month_index.get(old_year, old_month)

        old_transaction_index = HashMap.TransactionIndex(old_month_data)
        old_category_index = HashMap.CategoryIndex(old_month_data)

        index = old_transaction_index.find_by_id(transaction_id)
        if index == -1:
            raise ValueError("Transaction does not exist.")

        transaction = old_transaction_index._transactions[index]
        old_category_id = transaction.category_id
        old_category_state = old_category_index.get(old_category_id)
        
        # TRƯỜNG HỢP 1: ĐỔI THÁNG

        if old_year != new_year or old_month != new_month:

            # Cập nhật CategoryState tháng cũ
            old_category_state.update_transaction(
                old_amount=transaction.amount,
                mode="delete"
            )

            # Xóa khỏi TransactionIndex tháng cũ
            old_transaction_index.remove(transaction_id)

            # Lấy dữ liệu tháng mới
            new_month_data = self._month_index.get_or_create(
                new_year,
                new_month
            )

            new_transaction_index = HashMap.TransactionIndex(new_month_data)
            new_category_index = HashMap.CategoryIndex(new_month_data)

            # Cập nhật Transaction
            transaction.amount = amount
            transaction.date = date
            transaction.category_id = new_category.id
            transaction.note = note

            # Thêm vào tháng mới
            new_transaction_index.add(transaction)

            # Cập nhật TransactionMap
            self._transaction_map.add(
                transaction_id,
                new_year,
                new_month
            )

            # Lấy hoặc tạo CategoryState mới
            new_category_state = new_category_index.get(new_category.id)

            if new_category_state is None:

                if new_category.type.upper() == "INCOME":
                    new_category_state = model.IncomeState(
                        new_category,
                        new_year,
                        new_month
                    )
                else:
                    new_category_state = model.ExpenseState(
                        new_category,
                        new_year,
                        new_month,
                        new_category.limit
                    )

                new_category_index.add(new_category_state)

            # Cập nhật thống kê tháng mới
            new_category_state.update_transaction(
                new_amount=amount,
                mode="add"
            )

            if isinstance(new_category_state, model.ExpenseState):
                if new_category_state.total_expense > new_category_state.limit:
                    print("Warning: Budget exceeded!")

        # TRƯỜNG HỢP 2: KHÔNG ĐỔI THÁNG

        else:

            # Nếu đổi Category
            if old_category_id != new_category.id:

                old_category_state.update_transaction(
                    old_amount=transaction.amount,
                    mode="delete"
                )

                new_category_state = old_category_index.get(new_category.id)

                if new_category_state is None:

                    if new_category.type.upper() == "INCOME":
                        new_category_state = model.IncomeState(
                            new_category,
                            new_year,
                            new_month
                        )
                    else:
                        new_category_state = model.ExpenseState(
                            new_category,
                            new_year,
                            new_month,
                            new_category.limit
                        )

                    old_category_index.add(new_category_state)

                new_category_state.update_transaction(
                    new_amount=amount,
                    mode="add"
                )

                if isinstance(new_category_state, model.ExpenseState):
                    if new_category_state.total_expense > new_category_state.limit:
                        print("Warning: Budget exceeded!")

            # Không đổi Category
            else:

                old_category_state.update_transaction(
                    old_amount=transaction.amount,
                    new_amount=amount,
                    mode="update"
                )

                if isinstance(old_category_state, model.ExpenseState):
                    if old_category_state.total_expense > old_category_state.limit:
                        print("Warning: Budget exceeded!")

            # Nếu đổi ngày thì sắp xếp lại
            if transaction.date != date:

                old_transaction_index.relocate(
                    transaction_id,
                    date
                )

            # Cập nhật thông tin
            transaction.amount = amount
            transaction.date = date
            transaction.category_id = new_category.id
            transaction.note = note

        print("Transaction updated successfully.")
