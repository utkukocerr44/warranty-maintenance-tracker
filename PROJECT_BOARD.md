# GitHub Projects Board Plan

Use these columns in GitHub Projects:

- Todo
- In Progress
- Done

## Todo

### [US3] Update warranty item details

As a user, I want to update warranty and maintenance details so that my product records stay accurate.

Acceptance criteria:

- The user can open an edit form for one of their own items.
- The form shows the existing item data.
- The user can change item name, category, purchase date, warranty end date, maintenance date, and notes.
- The updated item appears on the dashboard after saving.
- The user cannot update another user's item.

### [US4] Delete old warranty items

As a user, I want to delete products I no longer own so that my dashboard stays clean.

Acceptance criteria:

- The user can delete one of their own items.
- The deleted item no longer appears on the dashboard.
- The user cannot delete another user's item.

### [US5] Highlight maintenance due items

As a user, I want overdue maintenance to be highlighted so that I do not miss important service dates.

Acceptance criteria:

- An item with a maintenance date today is shown as Maintenance Due.
- An item with a past maintenance date is shown as Maintenance Due.
- Maintenance Due has priority over the normal warranty status.
- The business logic is covered by unit tests.

## In Progress

### [US1] Add warranty item

As a user, I want to add a product with warranty dates so that I can track when its warranty expires.

Acceptance criteria:

- The user can create an item with name, category, purchase date, warranty end date, optional maintenance date, and notes.
- Required fields are validated before saving.
- The item is linked to the logged-in user's `user_id`.
- The item appears on the user's dashboard after creation.

### [US2] View personal warranty dashboard

As a user, I want to view my own products with status labels so that I can quickly see which items need attention.

Acceptance criteria:

- The dashboard lists only the logged-in user's items.
- Each item shows warranty and maintenance dates.
- Each item displays one status: Active, Expiring Soon, Expired, or Maintenance Due.
- Dashboard summary counts match the user's items.
- The user can search and filter dashboard items by category and status.

## Done

- Initial Flask application structure
- SQLite schema with `users` and `items`
- Register, login, and logout routes
- Raw SQL CRUD routes for warranty items
- Unit tests for business logic functions

## Implementation Mapping

| Story | Main implementation |
| --- | --- |
| `[US1]` | `create_item()` route in `app.py`, `item_form.html`, item validation in `logic.py` |
| `[US2]` | `index()` dashboard route in `app.py`, dashboard filters with query parameters |
| `[US3]` | `edit_item()` route in `app.py` |
| `[US4]` | `delete_item()` route in `app.py`, delete confirmation in `dashboard.html` |
| `[US5]` | Warranty status, maintenance status, category limits, and unit tests in `logic.py` and `tests/test_logic.py` |
