import sqlite3
import random
from datetime import datetime, timedelta
from flask import g, current_app
from werkzeug.security import generate_password_hash

def get_db():
    """Returns the database connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def init_db():
    """Initializes the database by creating the necessary tables."""
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row

    with db:

        # Users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Categories table
        db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Expenses table
        db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
    db.close()

def seed_db():
    """Seeds the database with sample data for development."""
    init_db()
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row

    try:

        with db:
            # Seed Categories
            categories = [
                ('Food', 'Groceries, dining out, etc.'),
                ('Transport', 'Gas, public transport, Uber'),
                ('Utilities', 'Electricity, water, internet'),
                ('Entertainment', 'Movies, games, hobbies'),
                ('Health', 'Medicine, gym, doctor visits')
            ]
            db.executemany('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', categories)

            # Seed User
            db.execute('INSERT OR IGNORE INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                      ('testuser', 'pbkdf2:sha256:260000$examplehash', 'test@example.com'))

            # Get user and category IDs for expenses
            user_id = db.execute('SELECT id FROM users WHERE username = ?', ('testuser',)).fetchone()[0]
            category_ids = {row['name']: row['id'] for row in db.execute('SELECT id, name FROM categories').fetchall()}

            # Seed Expenses
            expenses = [
                (user_id, category_ids['Food'], 50.0, 'Weekly groceries', '2026-05-20'),
                (user_id, category_ids['Transport'], 20.0, 'Bus pass', '2026-05-21'),
                (user_id, category_ids['Entertainment'], 15.0, 'Cinema ticket', '2026-05-22'),
            ]
            db.executemany('INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)', expenses)

    finally:
        db.close()

def seed_custom_user(name, email, password):
    db = get_db()
    # Check if the email already exists in the users table using a parameterized query
    user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if user:
        print(f"User with email {email} already exists. Skipping.")
        return

    # Hash the password using generate_password_hash and insert the user
    password_hash = generate_password_hash(password)
    db.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
               (name, password_hash, email))
    db.commit()
    db.close()
    print(f"User {name} with email {email} successfully seeded.")

def seed_expenses_for_user(user_id, month):
    """Seeds random expenses for a specific user for a given month (YYYY-MM)."""
    # We use a standalone connection since we might not be in a request context
    from flask import Flask
    app = Flask(__name__)
    app.config['DATABASE'] = 'database.sqlite'

    with app.app_context():
        db = get_db()

        # Get available categories
        categories = db.execute('SELECT id, name FROM categories').fetchall()
        if not categories:
            print("No categories found. Please run seed_db() first.")
            return

        # Generate 5-10 random expenses
        count = random.randint(5, 10)
        expenses_to_insert = []

        # Year is assumed to be 2026 based on project context
        year = 2026
        month_num = int(month.split('-')[1]) if '-' in month else int(month)

        # Basic date generation for the month
        for i in range(count):
            cat = random.choice(categories)
            amount = round(random.uniform(10.0, 500.0), 2)
            day = random.randint(1, 28) # Simplified to 28 to avoid month end issues
            date_str = f"{year}-{month_num:02d}-{day:02d}"
            desc = f"Random {cat['name']} expense {i+1}"
            expenses_to_insert.append((user_id, cat['id'], amount, desc, date_str))

        db.executemany(
            'INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)',
            expenses_to_insert
        )
        db.commit()
        print(f"Successfully seeded {count} expenses for user {user_id} in month {month}.")
