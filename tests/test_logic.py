import unittest
from datetime import date

from logic import calculate_item_status, days_until, is_maintenance_due, warranty_status


class WarrantyLogicTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 5, 12)

    def test_days_until_future_date(self):
        self.assertEqual(days_until("2026-05-22", self.today), 10)

    def test_expired_warranty(self):
        self.assertEqual(warranty_status("2026-05-01", self.today), "Expired")

    def test_expiring_soon_warranty(self):
        self.assertEqual(warranty_status("2026-05-30", self.today), "Expiring Soon")

    def test_active_warranty(self):
        self.assertEqual(warranty_status("2026-08-01", self.today), "Active")

    def test_maintenance_due_today(self):
        self.assertTrue(is_maintenance_due("2026-05-12", self.today))

    def test_maintenance_due_overrides_warranty_status(self):
        self.assertEqual(
            calculate_item_status("2026-08-01", "2026-05-01", self.today),
            "Maintenance Due",
        )


if __name__ == "__main__":
    unittest.main()
