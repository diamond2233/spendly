import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db():
    """Open a new SQLite connection with row access by column name and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert one demo user and 8 sample expenses, but only on an empty DB."""
    conn = get_db()

    row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if row["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    y, m = today.year, today.month

    sample_expenses = [
        (450.00, "Food",          f"{y:04d}-{m:02d}-02", "Grocery shopping"),
        (120.50, "Transport",     f"{y:04d}-{m:02d}-04", "Bus pass"),
        (1500.00, "Bills",        f"{y:04d}-{m:02d}-05", "Electricity bill"),
        (300.00, "Health",        f"{y:04d}-{m:02d}-08", "Pharmacy"),
        (600.00, "Entertainment", f"{y:04d}-{m:02d}-10", "Movie night"),
        (899.00, "Shopping",      f"{y:04d}-{m:02d}-14", "New shoes"),
        (250.00, "Other",         f"{y:04d}-{m:02d}-18", "Miscellaneous purchase"),
        (180.00, "Food",          f"{y:04d}-{m:02d}-22", "Restaurant dinner"),
    ]

    for amount, category, exp_date, description in sample_expenses:
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, exp_date, description),
        )

    conn.commit()
    conn.close()


def create_user(name, email, password):
    """Insert a new user with a hashed password; return the new user's id, or None if the email is already taken."""
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        user_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        user_id = None
    conn.close()
    return user_id


def get_user_by_email(email):
    """Return the user row matching email, or None if no such user exists."""
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, password_hash FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Return the user row (id, name, email, created_at) matching user_id, or None if not found."""
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return user


def get_expense_summary_by_user(user_id):
    """Return a row with the expense count and total amount for user_id."""
    conn = get_db()
    summary = conn.execute(
        "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return summary


def get_category_totals_by_user(user_id):
    """Return each category's total amount for user_id, highest total first."""
    conn = get_db()
    totals = conn.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return totals


def get_recent_expenses_by_user(user_id, limit=5):
    """Return the most recent `limit` expenses for user_id, newest first."""
    conn = get_db()
    expenses = conn.execute(
        """
        SELECT id, amount, category, date, description
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()
    return expenses
