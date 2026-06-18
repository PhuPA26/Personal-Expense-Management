from core.data_structure import HashMap
class Transaction:
    def __init__(
        self,
        transaction_id,
        amount,
        date,
        category_id,
        transaction_type,
        note=""
    ):
        self.transaction_id = transaction_id
        self.amount = amount
        self.date = date
        self.category_id = category_id
        self.transaction_type = transaction_type
        self.note = note

class Category:
    def __init__(self, id, name, type, created_at=None, is_active=True, limit=0):
        self.id = id
        self.name = name
        self.type = type  # "income" or "expense"
        self.limit = limit  # Mặc định là 0
        self.is_active = is_active # True nếu đang hoạt động, False nếu đã bị vô hiệu hóa
    
    def set_limit(self, new_limit):
        self.limit = new_limit

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

class CategoryState:
    def __init__(self, category, year, month):
        self.category = category
        self.year = year
        self.month = month

class IncomeState(CategoryState):
    def __init__(self, category, year, month):
        super().__init__(category, year, month)
        self.total_income = 0
        
    def update_transaction(self, old_amount=0, new_amount=0, mode="add"):
        if mode == "add":
            self.total_income += new_amount

        elif mode == "update":
            self.total_income -= old_amount
            self.total_income += new_amount

        elif mode == "delete":
            self.total_income -= old_amount

class ExpenseState(CategoryState):
    def __init__(self, category, year, month, limit):
        super().__init__(category, year, month)
        self.limit = limit
        self.total_expense = 0
        
    def update_transaction(self, old_amount=0, new_amount=0, mode="add"):
        if mode == "add":
            self.total_expense += new_amount

        elif mode == "update":
            self.total_expense -= old_amount
            self.total_expense += new_amount

        elif mode == "delete":
            self.total_expense -= old_amount

    def set_limit(self, new_limit):
        self.limit = new_limit

class MonthData:
    def __init__(self):
        self.category_states = HashMap()
        self.transactions = []
