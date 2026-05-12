# Warranty & Maintenance Tracker

A Flask web application for tracking personal product warranties and maintenance dates.

## Features

- Register, login, and logout with Flask sessions
- Multi-user data isolation
- Raw SQL with SQLite
- CRUD for warranty items
- Business logic for warranty and maintenance status
- Unit tests for business logic

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Open `http://127.0.0.1:5000`.

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
