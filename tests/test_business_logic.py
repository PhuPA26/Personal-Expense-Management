import unittest
from unittest.mock import patch
import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import models
from services.transaction_manager import FinanceManager
from services.category_manager import CategoryFinance
from services.report_manager import ReportManager

class TestBusinessLogic(unittest.TestCase):
    """III. KIỂM THỬ LOGIC NGHIỆP VỤ (BUSINESS LOGIC)"""

    def setUp(self):
        self.category_finance = CategoryFinance()
        self.fm = FinanceManager(self.category_finance)
        self.cat1 = models.Category("C1", "Ăn uống", "expense", limit=1000000)
        self.category_finance.add_category(self.cat1)

    def test_lt_01_add_exceed_budget(self):
        date_str = datetime.date.today().strftime("%d-%m-%Y")
        self.fm.add_transaction("T1", 800000, date_str, "C1")
        is_exceeded = self.fm.add_transaction("T2", 300000, date_str, "C1")
        self.assertTrue(is_exceeded)

    def test_lt_02_update_exceed_budget(self):
        date_str = datetime.date.today().strftime("%d-%m-%Y")
        self.fm.add_transaction("T1", 600000, date_str, "C1")
        is_exceeded = self.fm.update_transaction("T1", amount=1200000)
        self.assertTrue(is_exceeded)

    def test_lt_03_delete_update_balance(self):
        cat_inc = models.Category("C2", "Lương", "income")
        self.category_finance.add_category(cat_inc)
        date_str = datetime.date.today().strftime("%d-%m-%Y")
        
        self.fm.add_transaction("T1", 5000000, date_str, "C2")
        self.fm.add_transaction("T2", 2000000, date_str, "C1")
        
        self.assertEqual(self.fm.get_total_balance(), 3000000)
        self.fm.delete_transaction("T2")
        self.assertEqual(self.fm.get_total_balance(), 5000000)

    def test_lt_04_recover_soft_delete(self):
        self.category_finance.remove_category("C1")
        self.assertFalse(self.cat1.is_active)
        cat_recover = models.Category("C1", "Ăn uống", "expense", limit=1000000)
        self.category_finance.add_category(cat_recover)
        self.assertTrue(self.cat1.is_active)

    def test_lt_05_add_existing_name(self):
        cat_duplicate = models.Category("C3", "Ăn uống", "expense", limit=500000)
        with self.assertRaises(ValueError) as ctx:
            self.category_finance.add_category(cat_duplicate)
        self.assertIn("Category name already exists", str(ctx.exception))

    def test_lt_06_update_category_exceed_budget(self):
        cat2 = models.Category("C2", "Đi lại", "expense", limit=1000000)
        self.category_finance.add_category(cat2)
        date_str = datetime.date.today().strftime("%d-%m-%Y")
        
        self.fm.add_transaction("T1", 500000, date_str, "C2")
        self.fm.add_transaction("T2", 800000, date_str, "C1")
        
        is_exceeded = self.fm.update_transaction("T1", category_id="C1")
        self.assertTrue(is_exceeded)

    def test_lt_07_update_date_change_month(self):
        date_str_may = "15-05-2023"
        date_str_june = "15-06-2023"
        
        self.fm.add_transaction("T1", 200000, date_str_may, "C1")
        self.fm.update_transaction("T1", date=date_str_june)
        
        md_may = self.fm._month_index.get(2023, 5)
        self.assertEqual(len(md_may.transactions), 0)
        
        md_june = self.fm._month_index.get(2023, 6)
        self.assertEqual(len(md_june.transactions), 1)
        self.assertEqual(md_june.transactions[0].date.month, 6)

    def test_lt_08_report_exceed_budget(self):
        date_str = "15-06-2023"
        self.fm.add_transaction("T1", 1200000, date_str, "C1")
        
        rm = ReportManager(self.fm._month_index)
        with patch('builtins.print') as mock_print:
            rm.generate_monthly_report(2023, 6)
            mock_print.assert_any_call("   ❌ [Ăn uống] ĐÃ VƯỢT HẠN MỨC!")

if __name__ == "__main__":
    unittest.main()
