from datetime import date, datetime


DATE_FORMAT = "%Y-%m-%d"


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
