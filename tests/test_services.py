import os
import tempfile
import unittest

import src.database as db_mod
import src.config as cfg_mod
from src.services.expense_service import ExpenseService
from src.services.analytics_service import AnalyticsService


class TestExpenseService(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_config_dir = cfg_mod.CONFIG_DIR
        cfg_mod.CONFIG_DIR = self._tmpdir
        self._orig_db_host = os.environ.pop("DB_HOST", None)
        self.db = db_mod.DatabaseConnection()
        db_mod.init_tables(self.db)
        self.staff_repo = db_mod.StaffRepository(self.db)
        self.expense_repo = db_mod.ExpenseRepository(self.db)
        self.service = ExpenseService(self.staff_repo, self.expense_repo)
        self.sid = self.staff_repo.add("Test User")

    def tearDown(self):
        self.db.close()
        cfg_mod.CONFIG_DIR = self._orig_config_dir
        if self._orig_db_host is not None:
            os.environ["DB_HOST"] = self._orig_db_host

    def test_record_valid_expense(self):
        exp = self.service.record(self.sid, 50.0, "Food & Dining", "Lunch")
        self.assertIsNotNone(exp.id)
        self.assertEqual(exp.amount, 50.0)
        self.assertEqual(exp.category, "Food & Dining")

    def test_record_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.service.record(self.sid, -10.0, "Food & Dining")

    def test_record_invalid_staff_raises(self):
        with self.assertRaises(ValueError):
            self.service.record(9999, 10.0, "Food & Dining")

    def test_get_expenses(self):
        self.service.record(self.sid, 25.0, "Food & Dining")
        self.service.record(self.sid, 15.0, "Transportation")
        exps = self.service.get_expenses(staff_id=self.sid)
        self.assertEqual(len(exps), 2)

    def test_delete_expense(self):
        exp = self.service.record(self.sid, 30.0, "Food & Dining")
        self.assertTrue(self.service.delete(exp.id))
        self.assertEqual(
            len(self.service.get_expenses(staff_id=self.sid)), 0
        )


class TestAnalyticsService(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_config_dir = cfg_mod.CONFIG_DIR
        cfg_mod.CONFIG_DIR = self._tmpdir
        self._orig_db_host = os.environ.pop("DB_HOST", None)
        self.db = db_mod.DatabaseConnection()
        db_mod.init_tables(self.db)
        self.staff_repo = db_mod.StaffRepository(self.db)
        self.expense_repo = db_mod.ExpenseRepository(self.db)
        self.service = AnalyticsService(self.expense_repo)
        self.sid = self.staff_repo.add("Test User")

        self.expense_repo.add(self.sid, 100.0, "Food & Dining")
        self.expense_repo.add(self.sid, 50.0, "Transportation")
        self.expense_repo.add(self.sid, 25.0, "Food & Dining")

    def tearDown(self):
        self.db.close()
        cfg_mod.CONFIG_DIR = self._orig_config_dir

    def test_overall_stats(self):
        stats = self.service.get_overall_stats(self.sid)
        self.assertEqual(stats.total_expenses, 3)
        self.assertEqual(stats.total_amount, 175.0)

    def test_category_breakdown(self):
        cats = self.service.get_category_breakdown(self.sid)
        self.assertEqual(len(cats), 2)
        food = next(c for c in cats if c.category == "Food & Dining")
        self.assertEqual(food.count, 2)
        self.assertEqual(food.total, 125.0)

    def test_monthly_trend(self):
        months = self.service.get_monthly_trend(self.sid)
        self.assertGreater(len(months), 0)

    def test_empty_stats(self):
        stats = self.service.get_overall_stats(staff_id=999)
        self.assertEqual(stats.total_expenses, 0)
        self.assertEqual(stats.total_amount, 0.0)


if __name__ == "__main__":
    unittest.main()
