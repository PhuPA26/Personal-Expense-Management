import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import models
from services.transaction_manager import FinanceManager
from services.category_manager import CategoryFinance
from data import file_io

class TestIntegrationAndStress(unittest.TestCase):
    """IV. KIỂM THỬ TÍCH HỢP (INTEGRATION) & TẢI (STRESS)"""

    def setUp(self):
        self.test_file = "test_data.txt"
        file_io._SAVE_FILE = self.test_file

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_it_01_load_empty_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        fm, cf = file_io.load_data()
        self.assertEqual(len(cf.categories), 0)
        self.assertEqual(fm.get_total_balance(), 0)

    def test_it_02_save_and_load(self):
        cf = CategoryFinance()
        fm = FinanceManager(cf)
        cat = models.Category("C1", "Test", "expense", limit=1000)
        cf.add_category(cat)
        date_str = "01-01-2023"
        fm.add_transaction("T1", 500, date_str, "C1")
        
        file_io.save_data(fm, cf)
        
        fm2, cf2 = file_io.load_data()
        self.assertEqual(len(cf2.categories), 1)
        self.assertEqual(cf2.categories[0].name, "Test")
        self.assertEqual(fm2.get_total_balance(), -500)

    def test_it_03_load_with_error_line(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("BEGIN_CATEGORIES\n")
            f.write("C1|Test|expense|1000|1\n")
            f.write("END_CATEGORIES\n")
            f.write("BEGIN_TRANSACTIONS\n")
            f.write("T1|500|2023-01-01|C1|expense|ok\n")
            f.write("T2|abc|2023-01-02|C1|expense|error\n") # Sai kiểu số
            f.write("T3|500|2023-01-03|C1\n")               # Thiếu cột
            f.write("END_TRANSACTIONS\n")
            
        fm, cf = file_io.load_data()
        self.assertEqual(len(cf.categories), 1)
        self.assertEqual(fm.get_total_balance(), -500)
        self.assertIsNotNone(fm._transaction_map.get("T1"))
        self.assertIsNone(fm._transaction_map.get("T2"))
        self.assertIsNone(fm._transaction_map.get("T3"))

    def test_st_01_stress_test(self):
        cf = CategoryFinance()
        fm = FinanceManager(cf)
        cat = models.Category("C1", "Test", "income")
        cf.add_category(cat)
        
        for i in range(10000):
            fm.add_transaction(f"TX{i}", 10, "01-01-2023", "C1")
            
        self.assertEqual(fm.get_total_balance(), 100000)

if __name__ == "__main__":
    unittest.main()
