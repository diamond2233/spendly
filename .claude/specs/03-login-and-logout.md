# Spec: Login and Logout

## Overview

Adds session-based authentication to Spendly. `GET /login` already renders `login.html` with a form posting `email`/`password` to `/login`, but there's no handler for that submission yet. This step adds `POST /login` (verify credentials against the `users` table created in Step 1 and populated via Step 2's registration, then start a session) and implements the `GET /logout` stub (end the session). This is the authentication foundation every later step needs — `/profile` (Step 4) and the `/expenses/*` routes (Steps 7–9) all require knowing who is logged in.

## Depends on

- Step 1 — [database-setup](01-database-setup.md): requires `get_db()` and the `users` table (with `password_hash`).
- Step 2 — [registration](02-registration.md): requires `create_user()`-created accounts (or the seeded demo user) to exist to log into.

## Routes

- `POST /login` — added to the existing `/login` route (`methods=["GET", "POST"]`). Reads `email`/`password` from the form, looks up the user, verifies the password hash, and on success stores `user_id` and `user_name` in the Flask session, then redirects to `/profile`. On failure (unknown email or wrong password) re-renders `login.html` with a single generic error — public.
- `GET /logout` — clears the session (`session.clear()`) and redirects to `/login`. Safe to hit whether or not a session currently exists (no error if already logged out) — logged-in in the normal flow, but tolerant of anonymous access.

`GET /login` behavior is unchanged — still renders `login.html` with no error.

## Database changes

No database changes — schema from Step 1 (`users.password_hash`) is unchanged. A new **query** function (`get_user_by_email`) is added to `database/db.py`, but that's application code, not a schema change.

## Templates

- **Create:** none.
- **Modify:**
    - `templates/base.html` — the nav currently always shows "Sign in" / "Get started". Make it session-aware: when `session.user_id` is set, show "Profile" (→ `url_for('profile')`) and "Log out" (→ `url_for('logout')`) instead. Flask injects `session` into the Jinja context automatically, so no extra `render_template` args are needed anywhere just for this.
    - `templates/login.html` — no structural changes required. It already has the `{% if error %}` block and posts `email`/`password` to `/login`, matching the pattern used for `register.html` in Step 2.

## Files to change

- `app.py` — set a `SECRET_KEY` (required for Flask sessions), add `session` and `check_password_hash` imports, change `/login` to `methods=["GET", "POST"]` with POST handling, implement `/logout`.
- `database/db.py` — add `get_user_by_email(email)`.
- `templates/base.html` — session-aware nav links.

## Files to create

None.

## New dependencies

No new dependencies — Flask's built-in `session` and `werkzeug.security.check_password_hash` (same package already used for `generate_password_hash`) cover everything needed.

## Rules for implementation

- No SQLAlchemy or ORMs.
- Parameterised queries only — `get_user_by_email` uses a `?` placeholder, never string-built SQL.
- Passwords hashed with werkzeug — verify with `check_password_hash(user.password_hash, password)`; never compare plaintext passwords directly.
- Use CSS variables — never hardcode hex values (applies if any nav styling is touched in `style.css`).
- All templates extend `base.html`.
- Use the **same generic error message** ("Invalid email or password.") for both "email not found" and "wrong password" — do not reveal which case occurred, to avoid leaking which emails are registered.
- `SECRET_KEY` is generated once at startup via `os.urandom(24)` — acceptable for this dev-scoped app; sessions reset on server restart, which is a known/accepted limitation, not a bug to fix here.
- Session must only ever store non-sensitive identifiers (`user_id`, `user_name`) — never store `password_hash` or the raw password in the session.
- DB logic (the lookup) stays in `database/db.py`; `app.py` only calls it and interprets the result.

## Definition of done

- [ ] Logging in with the seeded demo account (`demo@spendly.com` / `demo123`) redirects to `/profile` and the nav switches to "Profile" / "Log out".
- [ ] Logging in with a correct email but wrong password re-renders `login.html` with "Invalid email or password.", no session set.
- [ ] Logging in with an email that doesn't exist shows the exact same "Invalid email or password." message, no session set.
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/login`; the nav reverts to "Sign in" / "Get started".
- [ ] Visiting `/logout` while already logged out does not error — redirects to `/login` cleanly.
- [ ] `GET /login` (no form submission) still renders exactly as before, no `error` shown.
- [ ] All new SQL uses parameterized queries.
- [ ] App starts without errors on port 5001.
