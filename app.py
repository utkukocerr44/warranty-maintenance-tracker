import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from logic import (
    ITEM_CATEGORIES,
    STATUS_CHOICES,
    MAX_MAINTENANCE_YEARS,
    add_years,
    calculate_item_status,
    is_valid_category,
    status_matches,
    validate_item_dates,
    validate_password,
)


DATABASE = os.path.join(os.path.dirname(__file__), "instance", "warranty_tracker.db")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-before-deploy"
    app.config["DATABASE"] = DATABASE

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = None
        if user_id is not None:
            db = get_db()
            g.user = db.execute(
                "SELECT id, username FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.route("/")
    def index():
        if g.user is None:
            return render_template("index.html")

        filters = collect_dashboard_filters()
        conditions = ["user_id = ?"]
        parameters = [g.user["id"]]

        if filters["query"]:
            conditions.append("(LOWER(name) LIKE ? OR LOWER(notes) LIKE ?)")
            search_value = f"%{filters['query'].lower()}%"
            parameters.extend([search_value, search_value])

        if filters["category"]:
            conditions.append("category = ?")
            parameters.append(filters["category"])

        db = get_db()
        items = db.execute(
            f"""
            SELECT id, name, category, purchase_date, warranty_end_date,
                   maintenance_date, notes
            FROM items
            WHERE {' AND '.join(conditions)}
            ORDER BY warranty_end_date ASC
            """,
            parameters,
        ).fetchall()

        enriched_items = []
        counts = {"Active": 0, "Expiring Soon": 0, "Expired": 0, "Maintenance Due": 0}
        for item in items:
            status = calculate_item_status(item["warranty_end_date"], item["maintenance_date"])
            if not status_matches(item["warranty_end_date"], item["maintenance_date"], filters["status"]):
                continue
            counts[status] = counts.get(status, 0) + 1
            enriched_items.append({**dict(item), "status": status})

        return render_template(
            "dashboard.html",
            items=enriched_items,
            counts=counts,
            categories=ITEM_CATEGORIES,
            statuses=STATUS_CHOICES,
            filters=filters,
            has_filters=any(filters.values()),
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Username and password are required.")
            elif validate_password(password):
                flash(validate_password(password))
            else:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                    flash("Account created. You can log in now.")
                    return redirect(url_for("login"))
                except sqlite3.IntegrityError:
                    flash("This username is already taken.")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            db = get_db()
            user = db.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if user is None or not check_password_hash(user["password_hash"], password):
                flash("Invalid username or password.")
            else:
                session.clear()
                session["user_id"] = user["id"]
                return redirect(url_for("index"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/items/new", methods=["GET", "POST"])
    @login_required
    def create_item():
        if request.method == "POST":
            form_data = collect_item_form()
            error = validate_item_form(form_data)
            if error:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    """
                    INSERT INTO items
                    (user_id, name, category, purchase_date, warranty_end_date, maintenance_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        g.user["id"],
                        form_data["name"],
                        form_data["category"],
                        form_data["purchase_date"],
                        form_data["warranty_end_date"],
                        form_data["maintenance_date"],
                        form_data["notes"],
                    ),
                )
                db.commit()
                flash("Item added.")
                return redirect(url_for("index"))

        return render_template(
            "item_form.html",
            item=None,
            action="Add",
            categories=ITEM_CATEGORIES,
            warranty_limits=get_warranty_limits(),
            today_date=current_date_value(),
            maintenance_max_date=maintenance_max_date_value(),
        )

    @app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_item(item_id):
        item = get_user_item(item_id)
        if item is None:
            flash("Item not found.")
            return redirect(url_for("index"))

        if request.method == "POST":
            form_data = collect_item_form()
            error = validate_item_form(form_data)
            if error:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    """
                    UPDATE items
                    SET name = ?, category = ?, purchase_date = ?,
                        warranty_end_date = ?, maintenance_date = ?, notes = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (
                        form_data["name"],
                        form_data["category"],
                        form_data["purchase_date"],
                        form_data["warranty_end_date"],
                        form_data["maintenance_date"],
                        form_data["notes"],
                        item_id,
                        g.user["id"],
                    ),
                )
                db.commit()
                flash("Item updated.")
                return redirect(url_for("index"))

        return render_template(
            "item_form.html",
            item=item,
            action="Edit",
            categories=ITEM_CATEGORIES,
            warranty_limits=get_warranty_limits(),
            today_date=current_date_value(),
            maintenance_max_date=maintenance_max_date_value(),
        )

    @app.route("/items/<int:item_id>/delete", methods=["POST"])
    @login_required
    def delete_item(item_id):
        db = get_db()
        db.execute("DELETE FROM items WHERE id = ? AND user_id = ?", (item_id, g.user["id"]))
        db.commit()
        flash("Item deleted.")
        return redirect(url_for("index"))

    return app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app_database())
        g.db.row_factory = sqlite3.Row
    return g.db


def current_app_database():
    from flask import current_app

    return current_app.config["DATABASE"]


def init_db():
    db = get_db()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8") as file:
        db.executescript(file.read())
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def collect_item_form():
    return {
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "").strip(),
        "purchase_date": request.form.get("purchase_date", "").strip(),
        "warranty_end_date": request.form.get("warranty_end_date", "").strip(),
        "maintenance_date": request.form.get("maintenance_date", "").strip(),
        "notes": request.form.get("notes", "").strip(),
    }


def collect_dashboard_filters():
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    if category and category not in ITEM_CATEGORIES:
        category = ""
    if status and status not in STATUS_CHOICES:
        status = ""
    return {
        "query": request.args.get("q", "").strip(),
        "category": category,
        "status": status,
    }


def validate_item_form(form_data):
    if not form_data["name"]:
        return "Item name is required."
    if not is_valid_category(form_data["category"]):
        return "Choose a valid category."
    return validate_item_dates(
        form_data["purchase_date"],
        form_data["warranty_end_date"],
        form_data["maintenance_date"],
        category=form_data["category"],
    )


def current_date_value():
    from datetime import date

    return date.today().isoformat()


def maintenance_max_date_value():
    from datetime import date

    return add_years(date.today(), MAX_MAINTENANCE_YEARS).isoformat()


def get_warranty_limits():
    from logic import MAX_WARRANTY_YEARS_BY_CATEGORY

    return MAX_WARRANTY_YEARS_BY_CATEGORY


def get_user_item(item_id):
    db = get_db()
    return db.execute(
        """
        SELECT id, name, category, purchase_date, warranty_end_date, maintenance_date, notes
        FROM items
        WHERE id = ? AND user_id = ?
        """,
        (item_id, g.user["id"]),
    ).fetchone()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
