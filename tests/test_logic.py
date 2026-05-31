import unittest
from datetime import date

from logic import (
    calculate_item_status,
    days_until,
    is_maintenance_due,
    is_valid_category,
    status_matches,
    warranty_exceeds_category_limit,
    validate_item_dates,
    validate_password,
    warranty_status,
)


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

    def test_password_must_have_minimum_length(self):
        self.assertEqual(validate_password("12345"), "Password must be at least 6 characters.")
        self.assertIsNone(validate_password("123456"))

    def test_category_must_be_from_allowed_choices(self):
        self.assertTrue(is_valid_category("Laptop"))
        self.assertFalse(is_valid_category("Random Category"))

    def test_warranty_end_date_can_be_in_past(self):
        self.assertIsNone(validate_item_dates("2025-05-01", "2026-05-01", today=self.today))

    def test_warranty_end_date_cannot_be_before_purchase_date(self):
        self.assertEqual(
            validate_item_dates("2026-05-01", "2026-04-30", today=self.today),
            "Warranty end date cannot be before the purchase date.",
        )

    def test_purchase_date_cannot_be_in_future(self):
        self.assertEqual(
            validate_item_dates("2026-05-13", "2026-06-01", today=self.today),
            "Purchase date cannot be in the future.",
        )

    def test_maintenance_date_cannot_be_in_past(self):
        self.assertEqual(
            validate_item_dates("2026-05-01", "2026-06-01", "2026-05-11", self.today),
            "Maintenance date cannot be in the past.",
        )

    def test_status_filter_matches_calculated_status(self):
        self.assertTrue(status_matches("2026-05-30", None, "Expiring Soon", self.today))
        self.assertFalse(status_matches("2026-08-01", None, "Expiring Soon", self.today))

    def test_category_warranty_limit_blocks_unrealistic_dates(self):
        self.assertEqual(
            validate_item_dates("2026-05-01", "2032-05-02", today=self.today, category="Phone"),
            "Phone warranty cannot be longer than 5 years.",
        )

    def test_category_warranty_limit_allows_valid_dates(self):
        self.assertFalse(
            warranty_exceeds_category_limit(
                "Phone",
                date(2026, 5, 1),
                date(2031, 5, 1),
            )
        )

    def test_maintenance_date_cannot_be_too_far_in_future(self):
        self.assertEqual(
            validate_item_dates("2026-05-01", "2027-05-01", "2032-06-01", self.today),
            "Maintenance date cannot be more than 5 years from today.",
        )

    def test_maintenance_date_respects_category_purchase_limit(self):
        self.assertEqual(
            validate_item_dates("2022-05-01", "2026-05-01", "2029-05-01", self.today, "Phone"),
            "Phone maintenance date cannot be more than 5 years after purchase.",
        )


if __name__ == "__main__":
    unittest.main()
