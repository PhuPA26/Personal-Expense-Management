from CTDL import HashMap
import model

# Category Index
# category_id -> Category

class CategoryIndex:

    def __init__(self, month_data):
        self._category_states = month_data.category_states

    def get(self, category_id):
        return self._category_states.get(category_id)

    def exists(self, category_id):
        return category_id in self._category_states

    def add(self, category_state):
        self._category_states[category_state.category.id] = category_state

    def remove(self, category_id):
        del self._category_states[category_id]

class MonthIndex:

    def __init__(self):
        self._months = HashMap()

    def _get_key(self, year, month):
        return f"{year}-{month:02d}"

    def get(self, year, month):
        key = self._get_key(year, month)
        return self._months.get(key)

    def exists(self, year, month):
        key = self._get_key(year, month)
        return key in self._months

    def create(self, year, month):
        key = self._get_key(year, month)

        if key not in self._months:
            self._months[key] = model.MonthData()

        return self._months[key]

    def get_or_create(self, year, month):
        month_data = self.get(year, month)

        if month_data is None:
            month_data = self.create(year, month)

        return month_data

    def remove(self, year, month):
        key = self._get_key(year, month)

        if key in self._months:
            del self._months[key]

class TransactionIndex:

    def __init__(self, month_data):
        self._transactions = month_data.transactions

    # TÌM TUẦN TỰ
    def find_by_id(self, transaction_id):
        for i, transaction in enumerate(self._transactions):
            if transaction.transaction_id == transaction_id:
                return i
        return -1

    def get_transaction(self, transaction_id):
        index = self.find_by_id(transaction_id)
        if index == -1:
            return None
        return self._transactions[index]

    def find_by_category(self, category_id):
        result = []
        for i, transaction in enumerate(self._transactions):
            if transaction.category_id == category_id:
                result.append(i)
        return result

    def find_by_amount(self, amount):
        result = []
        for i, transaction in enumerate(self._transactions):
            if transaction.amount == amount:
                result.append(i)
        return result

    def find_by_note(self, keyword):
        result = []
        for i, transaction in enumerate(self._transactions):
            if keyword.lower() in transaction.note.lower():
                result.append(i)
        return result


#BINARY SEARCH THEO NGÀY

    def find_by_date(self, date):

        left = 0
        right = len(self._transactions) - 1

        while left <= right:

            mid = (left + right) // 2

            if self._transactions[mid].date == date:

                first = mid
                while first > 0 and self._transactions[first - 1].date == date:
                    first -= 1

                last = mid
                while last < len(self._transactions) - 1 and \
                        self._transactions[last + 1].date == date:
                    last += 1

                return first, last

            elif self._transactions[mid].date < date:
                left = mid + 1

            else:
                right = mid - 1

        return -(right + 1), -(left + 1)


# THÊM GIAO DỊCH THEO NGÀY

    def add(self, transaction):

        left, right = self.find_by_date(transaction.date)

        if left >= 0:
            self._transactions.insert(right + 1, transaction)
        else:
            insert_pos = -right - 1
            self._transactions.insert(insert_pos, transaction)


# CẬP NHẬT GIAO DỊCH THEO NGÀY

    def relocate(self, transaction_id, new_date):

        index = self.find_by_id(transaction_id)

        if index == -1:
            return False

        transaction = self._transactions.pop(index)

        transaction.date = new_date

        self.add(transaction)

        return True

#Xóa giao dịch theo ID
    def remove(self, transaction_id):

        index = self.find_by_id(transaction_id)

        if index == -1:
            return False

        self._transactions.pop(index)

        return True

    # LẤY CÁC GIAO DỊCH TRONG THÁNG (TUẦN TỰ)

    def get_monthly_transactions(self, year, month):

        result = []
        for transaction in self._transactions:
            result.append(transaction)
        return result
    


class TransactionMap:

    def __init__(self):
        self._transactions = HashMap()

    def get(self, transaction_id):
        return self._transactions.get(transaction_id)

    def exists(self, transaction_id):
        return transaction_id in self._transactions

    def add(self, transaction_id, year, month):
        self._transactions[transaction_id] = (year, month)

    def remove(self, transaction_id):
        if transaction_id in self._transactions:
            del self._transactions[transaction_id]