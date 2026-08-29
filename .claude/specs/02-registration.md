# Registration

## Overview

Implement account creation for Spendly. The `GET /register` route already renders `register.html` with a form (name, email, password) that posts to `/register`. This step adds the `POST /register` handler so submitting that form actually creates a user in the database, with validation and duplicate-email handling.

This step does **not** implement login/session management (`GET /logout` is Step 3, `GET /profile` is Step 4). After a successful registration the user is redirected to `/login` to sign in manually — no auto-login/session is created here.

---

## Dependencies

Depends on [01-database-setup](01-database-setup.md) — requires `get_db()`, `init_db()`, and the `users` table with its `UNIQUE` email constraint to already exist.

---

## Routes to Implement

### `POST /register` (add to existing `/register` route)

- Change `@app.route("/register")` to accept both `GET` and `POST` (`methods=["GET", "POST"]`)
- `GET` behavior unchanged — renders `register.html`
- `POST` behavior:
    - Read `name`, `email`, `password` from `request.form`
    - Validate:
        - `name`, `email`, `password` all non-empty
        - `password` is at least 8 characters
    - On validation failure → re-render `register.html` with an `error` message, form values not preserved (matches current template's minimal state)
    - Call `create_user(name, email, password)` from `database/db.py`
    - If `create_user` reports the email is already taken → re-render `register.html` with `error = "An account with this email already exists."`
    - On success → `redirect(url_for('login'))`
    - Route function only handles request parsing, calling the DB helper, and choosing what to render/redirect — no SQL or password hashing inline

---

## Database Changes

No schema changes — `users` table from Step 1 is unchanged.

### New function in `database/db.py`: `create_user(name, email, password)`

- Hashes `password` with `werkzeug.security.generate_password_hash` (same helper already used in `seed_db()`)
- Inserts into `users (name, email, password_hash)` using a parameterized query
- Catches `sqlite3.IntegrityError` (raised by the `email UNIQUE` constraint) and returns `None` to signal "email taken" instead of letting the exception bubble up
- On success, commits and returns the new user's `id`
- Closes its own connection (matches the pattern in `init_db()` / `seed_db()`)

---

## Templates to Create/Modify

### Modify `templates/register.html`

- No structural changes needed — it already has `{% if error %}` and posts `name`, `email`, `password` to `/register`
- No new template files required

---

## Files Modified

- `app.py` — `/register` route gains `methods=["GET", "POST"]` and POST handling logic
- `database/db.py` — add `create_user(name, email, password)`

---

## New Files Created

- None

---

## New Dependencies

- None — `werkzeug.security.generate_password_hash` is already used in `database/db.py` and already in `requirements.txt`

---

## Rules of Implementation

- Never build SQL with f-strings — use `?` parameterized queries only (per CLAUDE.md)
- All DB logic (insert, duplicate-email handling) stays in `database/db.py`, never inline in `app.py`
- `app.py` route stays single-responsibility: parse form → call `create_user` → render/redirect
- Never hardcode `/login` or `/register` URLs in templates or redirects — use `url_for()`
- Do not implement `GET /logout`, `GET /profile`, or any session/cookie logic in this step — those are separate steps
- Do not add a POST handler to `/login` — it stays a stub until its own step
- Do not install new pip packages

---

## Acceptance Criteria (Definition of Done)

- [ ] `GET /register` still renders the form exactly as before
- [ ] Submitting valid name/email/password creates a new row in `users` with a hashed password
- [ ] Submitting a duplicate email shows an error on `register.html` instead of crashing or creating a duplicate row
- [ ] Submitting an empty field or a password under 8 characters shows a validation error, no row is created
- [ ] Successful registration redirects to `/login`
- [ ] All new SQL uses parameterized queries
- [ ] No DB logic lives in `app.py`
- [ ] `pytest` passes with no regressions to existing routes
