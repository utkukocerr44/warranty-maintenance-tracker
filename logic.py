from datetime import date, datetime


DATE_FORMAT = "%Y-%m-%d"
MIN_PASSWORD_LENGTH = 6
MAX_MAINTENANCE_YEARS = 5
ITEM_CATEGORIES = (
    "Phone",
    "Laptop",
    "Tablet",
    "Home Appliance",
    "Gaming Device",
    "Camera",
    "Audio Device",
    "Tool",
    "Other",
)
STATUS_CHOICES = ("Active", "Expiring Soon", "Expired", "Maintenance Due")
MAX_WARRANTY_YEARS_BY_CATEGORY = {
    "Phone": 5,
    "Laptop": 6,
    "Tablet": 5,
    "Home Appliance": 20,
    "Gaming Device": 6,
    "Camera": 8,
    "Audio Device": 5,
    "Tool": 15,
    "Other": 10,
}


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        return None


def days_until(target_date, today=None):
    if today is None:
        today = date.today()
    parsed_date = parse_date(target_date) if isinstance(target_date, str) else target_date
    if parsed_date is None:
        return None
    return (parsed_date - today).days


def warranty_status(warranty_end_date, today=None):
    remaining_days = days_until(warranty_end_date, today)
    if remaining_days is None:
        return "Unknown"
    if remaining_days < 0:
        return "Expired"
    if remaining_days <= 30:
        return "Expiring Soon"
    return "Active"


def is_maintenance_due(maintenance_date, today=None):
    remaining_days = days_until(maintenance_date, today)
    return remaining_days is not None and remaining_days <= 0


def calculate_item_status(warranty_end_date, maintenance_date=None, today=None):
    if is_maintenance_due(maintenance_date, today):
        return "Maintenance Due"
    return warranty_status(warranty_end_date, today)


def status_matches(warranty_end_date, maintenance_date, selected_status, today=None):
    if not selected_status:
        return True
    return calculate_item_status(warranty_end_date, maintenance_date, today) == selected_status


def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return None


def is_valid_category(category):
    return category in ITEM_CATEGORIES


def validate_item_dates(
    purchase_date,
    warranty_end_date,
    maintenance_date=None,
    today=None,
    category=None,
):
    if today is None:
        today = date.today()

    parsed_purchase_date = parse_date(purchase_date)
    parsed_warranty_end_date = parse_date(warranty_end_date)
    parsed_maintenance_date = parse_date(maintenance_date) if maintenance_date else None

    if parsed_purchase_date is None:
        return "Purchase date must be a valid date."
    if parsed_purchase_date > today:
        return "Purchase date cannot be in the future."
    if parsed_warranty_end_date is None:
        return "Warranty end date must be a valid date."
    if parsed_warranty_end_date < parsed_purchase_date:
        return "Warranty end date cannot be before the purchase date."
    if category and warranty_exceeds_category_limit(
        category,
        parsed_purchase_date,
        parsed_warranty_end_date,
    ):
        return f"{category} warranty cannot be longer than {MAX_WARRANTY_YEARS_BY_CATEGORY[category]} years."
    if maintenance_date and parsed_maintenance_date is None:
        return "Maintenance date must be a valid date."
    if parsed_maintenance_date and parsed_maintenance_date < today:
        return "Maintenance date cannot be in the past."
    if category and parsed_maintenance_date and warranty_exceeds_category_limit(
        category,
        parsed_purchase_date,
        parsed_maintenance_date,
    ):
        return f"{category} maintenance date cannot be more than {MAX_WARRANTY_YEARS_BY_CATEGORY[category]} years after purchase."
    if parsed_maintenance_date and parsed_maintenance_date > add_years(today, MAX_MAINTENANCE_YEARS):
        return f"Maintenance date cannot be more than {MAX_MAINTENANCE_YEARS} years from today."
    return None


def warranty_exceeds_category_limit(category, purchase_date, warranty_end_date):
    if category not in MAX_WARRANTY_YEARS_BY_CATEGORY:
        return False
    return warranty_end_date > add_years(purchase_date, MAX_WARRANTY_YEARS_BY_CATEGORY[category])


def add_years(start_date, years):
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        return start_date.replace(month=2, day=28, year=start_date.year + years)
