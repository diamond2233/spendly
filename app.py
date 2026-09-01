import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash

from database.db import (
    get_db,
    init_db,
    seed_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_expense_summary_by_user,
    get_recent_expenses_by_user,
    get_category_totals_by_user,
)

CATEGORY_COLOR_CLASSES = [
    "cat-color-0",
    "cat-color-1",
    "cat-color-2",
    "cat-color-3",
    "cat-color-4",
    "cat-color-5",
    "cat-color-6",
]

app = Flask(__name__)
# Generated fresh at each startup — sessions reset on restart, which is
# an accepted limitation for this dev-scoped app.
app.config["SECRET_KEY"] = os.urandom(24)

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")
        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters long.",
            )

        user_id = create_user(name, email, password)
        if user_id is None:
            return render_template(
                "register.html",
                error="An account with this email already exists.",
            )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    summary = get_expense_summary_by_user(user_id)
    recent_expenses = get_recent_expenses_by_user(user_id)
    category_totals = get_category_totals_by_user(user_id)
    member_since = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")

    top_category = category_totals[0]["category"] if category_totals else None
    initials = "".join(part[0] for part in user["name"].split()[:2]).upper()
    category_colors = {
        row["category"]: CATEGORY_COLOR_CLASSES[i % len(CATEGORY_COLOR_CLASSES)]
        for i, row in enumerate(category_totals)
    }

    return render_template(
        "profile.html",
        user=user,
        summary=summary,
        recent_expenses=recent_expenses,
        category_totals=category_totals,
        top_category=top_category,
        category_colors=category_colors,
        initials=initials,
        member_since=member_since,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
