# Spec: Profile Page Design

## Overview

Implements the `/profile` route, currently a stub returning the raw string `"Profile page — coming in Step 4"`. This step turns it into a real, logged-in-only dashboard page: an identity header (avatar initials, name, email, member since), three stat cards (total spent, transaction count, top category), a recent-transactions table, and a by-category spend breakdown with colored bars. It builds directly on the session established in Step 3 and gives users a landing spot after login — `base.html`'s nav already links here, and login/register now redirect straight to `/profile` for an authenticated session instead of the marketing landing page. This step is read-only: editing profile fields, editing/deleting individual expenses, and full expense management (add/edit/delete forms) are out of scope and land in later steps (7–9). The recent-transactions list and category breakdown are display-only — no per-row actions.

## Depends on

- Step 1 — [database-setup](01-database-setup.md): requires `get_db()`, the `users` table, and the `expenses` table (with seeded demo data).
- Step 3 — [login-and-logout](03-login-and-logout.md): requires `session["user_id"]` to be set on login so `/profile` knows who is asking.

## Routes

- `GET /profile` — replaces the stub. If `session.get("user_id")` is not set, redirect to `url_for("login")`. Otherwise, fetch the user's account info and expense summary and render `profile.html` — logged-in only.

## Database changes

No schema changes — `users` and `expenses` tables from Step 1 are unchanged. Two new **query** functions are added to `database/db.py` (application code, not schema):

- `get_user_by_id(user_id)` — `SELECT id, name, email, created_at FROM users WHERE id = ?`. Needed because the session only stores `user_id`/`user_name`; `email` and `created_at` aren't in the session and must come from the DB.
- `get_expense_summary_by_user(user_id)` — one parameterized query returning the count of expenses and the sum of `amount` for that user (e.g. `SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?`). `COALESCE` ensures a user with zero expenses gets `0`, not `NULL`.
- `get_recent_expenses_by_user(user_id, limit=5)` — returns the `limit` most recent expenses for the user, ordered `date DESC, id DESC`. Backs the recent-transactions list; a zero-expense user gets an empty list, and the template shows an empty-state message instead of a table.
- `get_category_totals_by_user(user_id)` — `SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC`. Backs the "by category" breakdown and the "top category" stat (the first row, if any).

## Templates

- **Create:** `templates/profile.html` — extends `base.html`. Shows an identity card (avatar initials, name, email, member-since date), three stat cards (total spent, transaction count, top category), a table of the 5 most recent transactions (date, description, category badge, amount), and a by-category breakdown (category name, total, proportional bar). No edit form, no per-row actions on either list.
- **Modify:** none. `base.html`'s nav already links "Profile" → `url_for('profile')` for logged-in users from Step 3.

## Files to change

- `app.py` — implement `/profile`: session check + redirect, call the four new query functions, compute display-only values (member-since string, avatar initials, top category, a per-category color-class map), pass results to `render_template("profile.html", ...)`. Also: login success and the already-logged-in guards on `/login` and `/register` now redirect to `profile` instead of `landing`.
- `database/db.py` — add `get_user_by_id(user_id)`, `get_expense_summary_by_user(user_id)`, `get_recent_expenses_by_user(user_id, limit=5)`, and `get_category_totals_by_user(user_id)`.
- `static/css/style.css` — added `--chart-3`..`--chart-6` (plus `-light` variants) to `:root` for the category color palette; also promoted `.mock-bar-3`/`.mock-bar-4`'s previously-hardcoded hex values to reference `--chart-3`/`--chart-4`.

## Files to create

- `templates/profile.html`

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs.
- Parameterised queries only — both new functions use `?` placeholders, never string-built SQL.
- Passwords hashed with werkzeug — unaffected by this step, but `password_hash` must never be selected or passed into the template.
- Use CSS variables — never hardcode hex values; reuse the existing tokens in `static/css/style.css` (`--ink`, `--paper-card`, `--border`, etc.) rather than introducing new colors.
- All templates extend `base.html`.
- `/profile` must redirect anonymous visitors to `/login` — use `abort()` only for actual HTTP errors, not for the auth check (a redirect is the correct UX here, not a 401/403 page).
- DB logic (both lookups) stays in `database/db.py`; `app.py` only calls the functions and passes results to the template.
- Do not implement profile editing, avatar upload, or password change in this step — those are out of scope until explicitly scheduled.

## Definition of done

- [ ] Visiting `/profile` while logged out redirects to `/login`.
- [ ] Logging in as the seeded demo user (`demo@spendly.com` / `demo123`) and visiting `/profile` shows name "Demo User", email "demo@spendly.com", and a member-since date.
- [ ] The profile page shows the correct total expense count (8) and total amount spent for the seeded demo user, matching the sum of the seeded sample expenses.
- [ ] The recent-transactions table shows up to 5 rows, most recent first, with correct date/category/description/amount for each.
- [ ] A user with zero expenses sees the "No expenses logged yet." empty state instead of an empty table.
- [ ] A user with zero expenses would see a total of 0, not an error (verify the `COALESCE` behavior by reasoning through the query, since the seeded user always has expenses).
- [ ] The by-category breakdown is sorted highest-total-first, and each category gets a distinct, consistent color across the badge, the bar, and the category name (verified with a 7-category account and with a category outside the fixed list, e.g. "Travel").
- [ ] Logging in redirects straight to `/profile`; visiting `/login` or `/register` while already authenticated also redirects to `/profile`.
- [ ] The nav still shows "Profile" / "Log out" while on this page.
- [ ] All new SQL uses parameterized queries.
- [ ] No hardcoded hex colors in any new CSS.
- [ ] App starts without errors on port 5001.
