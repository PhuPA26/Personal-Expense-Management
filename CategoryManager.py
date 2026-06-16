import CTDL
import model
import HashMap

class CategoryFinance(HashMap.CategoryManager):

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