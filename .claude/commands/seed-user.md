Name: seed-user

Description: Seeds a new dummy  user into the Spendly SQLite database. Adds seed_custom_user() to db.py, updates app.py imports, and inserts a hashed user safely — skips if email already exists.




You are working on a Flask + SQLite project called Spendly.

Your job is to seed a new dummy user into the database safely.

Follow these steps in order:

STEP 1 — Open database/db.py
- Read the existing file
- Locate the seed_db() function
- Add a new function called seed_custom_user(name, email, password) directly below it

The function must:
- Call get_db() to open a connection
- Check if the email already exists in the users table using a parameterized query
- If email exists: print a skip message and return early
- If email does not exist: hash the password using generate_password_hash and insert the user
- Commit and close the connection
- Print a success message after insert

STEP 2 — Open app.py
- Add seed_custom_user to the existing import line from database.db
- Inside the with app.app_context(): block, call seed_custom_user with these values:
  Name: Demo User 2
  Email: demo2@spendly.com
  Password: test123

STEP 3 — Verify
- Save both files
- Confirm no syntax errors
- Confirm the import is correct
- Confirm seed_custom_user is called inside app context

Rules to follow at all times:
- Use parameterized queries only — never use string formatting inside SQL
- Always check for duplicate email before inserting
- Always hash passwords — never store plain text
- Never modify the existing seed_db() function
- Never remove or change existing imports