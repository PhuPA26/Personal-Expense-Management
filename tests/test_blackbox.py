import unittest
from unittest.mock import patch
import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.transaction_manager import FinanceManager
from services.category_manager import CategoryFinance
import main

class TestBlackBoxInput(unittest.TestCase):
    """II. KIỂM THỬ HỘP ĐEN (BLACK-BOX) – Giao diện nhập liệu"""

    def test_bt_01_invalid_menu(self):
        with patch('main._input', side_effect=["9", "0"]), \
             patch('builtins.print') as mock_print:
            category_finance = CategoryFinance()
            fm = FinanceManager(category_finance)
            main._menu_category(fm, category_finance)
            mock_print.assert_any_call("  Lựa chọn không hợp lệ.")
            
    def test_bt_02_invalid_amount(self):
        category_finance = CategoryFinance()
        fm = FinanceManager(category_finance)
        with self.assertRaises(ValueError) as ctx:
            fm._check_amount(-50000)
        self.assertIn("Amount must be greater than 0", str(ctx.exception))
        
        with self.assertRaises(ValueError):
            fm._check_amount(0)

    def test_bt_03_invalid_date(self):
        category_finance = CategoryFinance()
        fm = FinanceManager(category_finance)
        
        with self.assertRaises(ValueError) as ctx:
            fm._parse_and_validate_date("32/13/2026")
        self.assertIn("Date must be in format dd-mm-yyyy", str(ctx.exception))
        
        future_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        with self.assertRaises(ValueError) as ctx:
            fm._parse_and_validate_date(future_date)
        self.assertIn("Date cannot be in the future", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
