
from core import models


class CategoryManager:

    def __init__(self):
        self.categories = []
    
    def add_category(self, category):
        self.categories.append(category)

    def find_by_id(self, categories, category_id):
        for i, category in enumerate(categories):
            if category.id == category_id:
                return i
        return -1

    def find_by_name(self, categories, name):
        for i, category in enumerate(categories):
            if category.name.lower() == name.lower():
                return i
        return -1

    def find_by_type(self, categories, category_type):
        result = []
        for i, category in enumerate(categories):
            if category.type == category_type:
                result.append(i)
        return result
    
    def get(self, categories, category_id):
        index = self.find_by_id(categories, category_id)
        if index == -1:
            return None
        return categories[index]

    def get_active_categories(self):
        result = []
        for category in self.categories:
            result.append(category)
        return result

class CategoryFinance(CategoryManager):    
    def __init__(self):
        super().__init__()

    def add_category(self, category):

        # 1. FIND BY ID (ONLY RESTORE PATH)
        index = self.find_by_id(self.categories, category.id)

        if index != -1:
            target = self.categories[index]

            # already active → error
            if target.is_active:
                raise ValueError("Category ID already exists and is active")

            # check name conflict using existing function
            name_index = self.find_by_name(self.categories, category.name)

            if name_index != -1:
                existing = self.categories[name_index]

                # if it's NOT the same category → conflict
                if existing.id != category.id:
                    raise ValueError("Category name already exists")

            # restore                
            target.is_active = True
            target.name = category.name
            target.type = category.type
            target.limit = category.limit
            target.created_at = category.created_at

            print("Success")
            return

        # 2. CHECK NAME for new category
        name_index = self.find_by_name(self.categories, category.name)

        if name_index != -1:
            raise ValueError("Category name already exists")

        # 3. validate type
        if category.type not in ["income", "expense"]:
            raise ValueError("Invalid category type")

        # 4. validate limit
        if category.limit < 0:
            raise ValueError("Limit cannot be negative")

        if category.type == "expense" and category.limit <= 0:
            raise ValueError("Expense category must have limit > 0")

        if category.type == "income" and category.limit != 0:
            raise ValueError("Income category must have limit = 0")

        # 6. add new
        self.categories.append(category)

        print("Success")
        return

    def remove_category(self, category_id):

        # 1. find by ID
        index = self.find_by_id(self.categories, category_id)

        if index == -1:
            raise ValueError("Category ID does not exist")

        target = self.categories[index]

        # 2. already inactive
        if not target.is_active:
            raise ValueError("Category is already inactive")

        # 3. soft delete
        target.is_active = False

        print("Success")
        return
    def update_category(
            self,
            category_id,
            new_name=None,
            new_type=None,
            new_limit=None,
            new_created_at=None
    ):

        # Find category
        index = self.find_by_id(self.categories, category_id)

        if index == -1:
            raise ValueError("Category ID does not exist")

        category = self.categories[index]

        # Không cho sửa category đã bị xóa
        if not category.is_active:
            raise ValueError("Category has been removed")

        # Update name
        if new_name is not None:

            name_index = self.find_by_name(self.categories, new_name)

            if name_index != -1:
                exist = self.categories[name_index]

                if exist.id != category_id:
                    raise ValueError("Category name already exists")

            category.name = new_name

        # Update type
        if new_type is not None:

            if new_type not in ["income", "expense"]:
                raise ValueError("Invalid category type")

            category.type = new_type

        # Update limit
        if new_limit is not None:

            if new_limit < 0:
                raise ValueError("Limit cannot be negative")

            category.limit = new_limit

        # Kiểm tra sau khi cập nhật type/limit
        if category.type == "expense" and category.limit <= 0:
            raise ValueError("Expense category must have limit > 0")

        if category.type == "income" and category.limit != 0:
            raise ValueError("Income category must have limit = 0")

        # Update created_at
        if new_created_at is not None:
            category.created_at = new_created_at

        print("Success")
