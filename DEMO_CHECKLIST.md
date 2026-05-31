# Final Demo Checklist

Use this flow during the project demo.

## 1. Start the Application

```bash
source .venv/bin/activate
python init_db.py
flask --app app run --port 5001
```

Open `http://127.0.0.1:5001`.

## 2. Authentication

- Register a new user with a password shorter than 6 characters and show validation.
- Register a valid user.
- Try registering the same username again and show the duplicate username message.
- Login and logout.

## 3. Multi-User Behavior

- Login as user A and create a warranty item.
- Logout.
- Login as user B.
- Show that user B cannot see user A's item.

## 4. CRUD

- Create an item with category, purchase date, warranty end date, maintenance date, and notes.
- Edit the item.
- Delete the item and show the confirmation prompt.

## 5. Business Logic

- Show status labels on the dashboard: Active, Expiring Soon, Expired, Maintenance Due.
- Explain that Maintenance Due has priority over warranty status.
- Show dashboard search and filters.

## 6. Testing

Run:

```bash
python -m unittest discover -s tests
```

Explain that the tests cover business logic functions, not routes.

## 7. GitHub Process

- Open the GitHub repository and show the commit messages with user story IDs.
- Open the GitHub Projects Kanban board.
- Show that each user story has acceptance criteria.
- Show that completed user stories are in the Done column.
