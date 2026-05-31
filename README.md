# Warranty & Maintenance Tracker

A Flask web application for tracking personal product warranties and maintenance dates.

## Features

- Register, login, and logout with Flask sessions
- Multi-user data isolation
- Raw SQL with SQLite
- CRUD for warranty items
- Dashboard search and filtering with query parameters
- Business logic for warranty and maintenance status
- Unit tests for business logic

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
flask --app app run --port 5001
```

Open `http://127.0.0.1:5001`.

## Tests

```bash
python -m unittest discover -s tests
```

## User Stories

- `[US1]` As a user, I want to add a product with warranty dates so that I can track when its warranty expires.
- `[US2]` As a user, I want to view my own products with status labels so that I can quickly see which items need attention.
- `[US3]` As a user, I want to update warranty or maintenance details so that my records stay accurate.
- `[US4]` As a user, I want to delete products I no longer own so that my dashboard stays clean.
- `[US5]` As a user, I want overdue maintenance to be highlighted so that I do not miss important service dates.

The detailed Kanban board plan and acceptance criteria are in `PROJECT_BOARD.md`.

## Demo Accounts

You can create users through the register page. For the final demo, use two different
accounts to show that each user only sees their own warranty items.

Example accounts used during local testing:

- `demo_user1 / demo123`
- `demo_user2 / demo456`

## Design Notes

- The application uses raw SQL queries in `app.py`; no ORM is used.
- User-specific data is enforced with `user_id` in the `items` table.
- Passwords are stored with Werkzeug password hashing instead of plain text.
- Business logic is kept in `logic.py` so it can be tested without testing routes.

## Business Rules

- Usernames must be unique.
- Passwords must be at least 6 characters.
- Purchase date cannot be in the future.
- Warranty end date cannot be before the purchase date.
- Warranty and maintenance dates are limited by product category.
- Maintenance Due has priority over the normal warranty status.
