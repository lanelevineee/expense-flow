import os
import tempfile
import unittest

import src.database as db_mod
import src.config as cfg_mod


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_config_dir = cfg_mod.CONFIG_DIR
        cfg_mod.CONFIG_DIR = self._tmpdir
        self._orig_db_host = os.environ.pop("DB_HOST", None)
        self.db = db_mod.DatabaseConnection()
        db_mod.init_tables(self.db)
        self.staff_repo = db_mod.StaffRepository(self.db)
        self.expense_repo = db_mod.ExpenseRepository(self.db)

    def tearDown(self):
        self.db.close()
        cfg_mod.CONFIG_DIR = self._orig_config_dir
        if self._orig_db_host is not None:
            os.environ["DB_HOST"] = self._orig_db_host

    def test_add_and_get_staff(self):
        sid = self.staff_repo.add("Alice", "Engineering", "alice@example.com")
        staff = self.staff_repo.get_by_id(sid)
        self.assertIsNotNone(staff)
        self.assertEqual(staff.name, "Alice")
        self.assertEqual(staff.department, "Engineering")
        self.assertEqual(staff.email, "alice@example.com")

    def test_get_all_staff(self):
        self.staff_repo.add("Alice")
        self.staff_repo.add("Bob")
        all_s = self.staff_repo.get_all()
        self.assertEqual(len(all_s), 2)

    def test_delete_staff_cascades(self):
        sid = self.staff_repo.add("Alice")
        eid = self.expense_repo.add(sid, 50.0, "Food")
        self.staff_repo.delete(sid)
        self.assertIsNone(self.staff_repo.get_by_id(sid))
        expenses = self.expense_repo.get_all()
        self.assertEqual(len(expenses), 0)

    def test_add_and_get_expense(self):
        sid = self.staff_repo.add("Bob")
        eid = self.expense_repo.add(sid, 25.50, "Transportation", "Bus pass")
        expense = self.expense_repo.get_all(staff_id=sid)[0]
        self.assertEqual(expense.amount, 25.50)
        self.assertEqual(expense.category, "Transportation")
        self.assertEqual(expense.description, "Bus pass")

    def test_get_total_stats_empty(self):
        stats = self.expense_repo.get_total_stats()
        self.assertEqual(stats.total_expenses, 0)
        self.assertEqual(stats.total_amount, 0.0)

    def test_get_total_stats_with_data(self):
        sid = self.staff_repo.add("Charlie")
        self.expense_repo.add(sid, 100.0, "Food")
        self.expense_repo.add(sid, 200.0, "Transport")
        stats = self.expense_repo.get_total_stats(sid)
        self.assertEqual(stats.total_expenses, 2)
        self.assertEqual(stats.total_amount, 300.0)
        self.assertEqual(stats.avg_amount, 150.0)
        self.assertEqual(stats.min_amount, 100.0)
        self.assertEqual(stats.max_amount, 200.0)

    def test_get_category_stats(self):
        sid = self.staff_repo.add("Diana")
        self.expense_repo.add(sid, 50.0, "Food")
        self.expense_repo.add(sid, 30.0, "Food")
        self.expense_repo.add(sid, 100.0, "Transport")
        cats = self.expense_repo.get_category_stats(sid)
        cat_map = {c.category: c for c in cats}
        self.assertEqual(cat_map["Food"].count, 2)
        self.assertEqual(cat_map["Food"].total, 80.0)
        self.assertEqual(cat_map["Transport"].total, 100.0)

    def test_get_monthly_stats(self):
        sid = self.staff_repo.add("Eve")
        self.expense_repo.add(sid, 100.0, "Food", expense_date="2025-01-15")
        self.expense_repo.add(sid, 200.0, "Food", expense_date="2025-02-10")
        months = self.expense_repo.get_monthly_stats(sid)
        self.assertEqual(len(months), 2)

    def test_recent_expenses(self):
        sid = self.staff_repo.add("Frank")
        self.expense_repo.add(sid, 10.0, "Food")
        recent = self.expense_repo.get_recent(sid, days=30)
        self.assertEqual(len(recent), 1)

    def test_delete_expense(self):
        sid = self.staff_repo.add("Grace")
        eid = self.expense_repo.add(sid, 75.0, "Food")
        self.assertTrue(self.expense_repo.delete(eid))
        expenses = self.expense_repo.get_all(staff_id=sid)
        self.assertEqual(len(expenses), 0)

    def test_clear_all(self):
        sid = self.staff_repo.add("Hank")
        self.expense_repo.add(sid, 100.0, "Food")
        self.expense_repo.clear_all()
        stats = self.expense_repo.get_total_stats()
        self.assertEqual(stats.total_expenses, 0)


if __name__ == "__main__":
    unittest.main()
