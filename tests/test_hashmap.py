import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_structure import HashMap

class TestHashMap(unittest.TestCase):
    """I. KIỂM THỬ HỘP TRẮNG (WHITE-BOX) – HashMap tự cài đặt"""

    def test_wt_01_insert_empty(self):
        hm = HashMap()
        hm.insert("food", 100)
        self.assertEqual(hm._HashMap__count, 1)
        self.assertEqual(hm.get("food"), 100)
        index = hm._HashMap__hash_function("food")
        bucket = hm._HashMap__buckets[index]
        self.assertIsNotNone(bucket)
        self.assertIsNone(bucket.next)

    def test_wt_02_update_existing(self):
        hm = HashMap()
        hm.insert("food", 100)
        hm.insert("food", 200)
        self.assertEqual(hm._HashMap__count, 1)
        self.assertEqual(hm.get("food"), 200)

    def test_wt_03_collision_delete(self):
        hm = HashMap()
        key1 = "abc"
        key2 = None
        target_hash = hm._HashMap__hash_function(key1)
        
        for i in range(10000):
            k = f"test{i}"
            if hm._HashMap__hash_function(k) == target_hash and k != key1:
                key2 = k
                break
        
        self.assertIsNotNone(key2, "Could not find a collision key")
        hm.insert(key1, 1)
        hm.insert(key2, 2)
        
        hm.remove_key(key1)
        self.assertEqual(hm.get(key2), 2)
        self.assertIsNone(hm.get(key1))
        self.assertEqual(hm._HashMap__count, 1)

if __name__ == "__main__":
    unittest.main()
