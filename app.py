from flask import Flask, render_template, g, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from database.db import init_db, seed_db, get_db, seed_custom_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['DATABASE'] = 'database.sqlite'
app.secret_key = 'dev-secret-key-for-spendly' # Change this in production

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database and seed it with sample data."""
    init_db()
    seed_db()
    print("Initialized the database and added sample data.")



# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        db = get_db()
        user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            return render_template("register.html", error="Email already registered")

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (name, password_hash, email)
        )
        db.commit()

        flash("Account created successfully! Please sign in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Email and password are required")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!")
            return redirect(url_for("profile"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/analytics")
def analytics():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view analytics.")
        return redirect(url_for("login"))

    return render_template("analytics.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your profile.")
        return redirect(url_for("login"))

    db = get_db()

    # Fetch user details
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash("User not found.")
        return redirect(url_for("login"))

    # Calculate Total Spent and Transaction Count
    stats = db.execute(
        "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    total_spent = stats["total"] if stats["total"] is not None else 0.0
    transaction_count = stats["count"] if stats["count"] is not None else 0

    # Calculate Top Category
    top_cat_row = db.execute(
        """SELECT c.name
           FROM expenses e
           JOIN categories c ON e.category_id = c.id
           WHERE e.user_id = ?
           GROUP BY c.name
           ORDER BY SUM(e.amount) DESC
           LIMIT 1""",
        (user_id,)
    ).fetchone()
    top_category = top_cat_row["name"] if top_cat_row else "N/A"

    # Fetch Recent Transactions
    expenses = db.execute(
        """SELECT e.id, e.date, e.description, c.name as category_name, e.amount
           FROM expenses e
           JOIN categories c ON e.category_id = c.id
           WHERE e.user_id = ?
           ORDER BY e.date DESC""",
        (user_id,)
    ).fetchall()

    # Generate Initials for Avatar
    username = user["username"] or "User"
    initials = "".join([name[0].upper() for name in username.split()[:2]])
    if not initials:
        initials = "U"

    return render_template(
        "profile.html",
        user=user,
        total_spent=total_spent,
        transaction_count=transaction_count,
        top_category=top_category,
        expenses=expenses,
        initials=initials
    )


@app.route("/expenses/history")
def expenses_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    expenses = db.execute(
        "SELECT e.id, e.date, e.description, c.name AS category, e.amount FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = ? ORDER BY e.date DESC",
        (user_id,)
    ).fetchall()

    return jsonify([dict(row) for row in expenses])


@app.route("/expenses/stats")
def expenses_stats():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    row = db.execute(
        "SELECT SUM(amount) AS total_spent, COUNT(*) AS transaction_count FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    return jsonify({
        "total_spent": row["total_spent"] if row and row["total_spent"] is not None else 0.0,
        "transaction_count": row["transaction_count"] if row else 0
    })


@app.route("/expenses/categories")
def expenses_categories():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    db = get_db()
    results = db.execute(
        "SELECT c.name AS category, SUM(e.amount) AS amount FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = ? GROUP BY c.name",
        (user_id,)
    ).fetchall()

    return jsonify([dict(row) for row in results])


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add an expense.")
        return redirect(url_for("login"))

    categories = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

    if request.method == "POST":
        amount_str = request.form.get("amount")
        category = request.form.get("category")
        date_str = request.form.get("date")
        description = request.form.get("description")

        # Validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except (TypeError, ValueError):
            flash("Invalid amount. Please enter a value greater than 0.")
            return redirect(url_for("add_expense"))

        if not category or category not in categories:
            flash("Invalid category selected.")
            return redirect(url_for("add_expense"))

        if not date_str:
            flash("Date is required.")
            return redirect(url_for("add_expense"))

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for("add_expense"))

        db = get_db()

        # Map category name to id
        cat_row = db.execute("SELECT id FROM categories WHERE name = ?", (category,)).fetchone()
        if not cat_row:
            flash("Category not found in database.")
            return redirect(url_for("add_expense"))

        category_id = cat_row["id"]

        # Insert expense
        db.execute(
            "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, category_id, amount, description or None, date_str)
        )
        db.commit()

        flash("Expense added successfully!")
        return redirect(url_for("profile"))

    return render_template("add_expense.html", categories=categories, today=datetime.now().strftime("%Y-%m-%d"))




@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to edit an expense.")
        return redirect(url_for("login"))

    db = get_db()

    # Fetch categories list for the dropdown (consistent with add_expense)
    categories = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

    if request.method == "POST":
        amount_str = request.form.get("amount")
        category = request.form.get("category")
        date_str = request.form.get("date")
        description = request.form.get("description")

        # Validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except (TypeError, ValueError):
            flash("Invalid amount. Please enter a value greater than 0.")
            expense = db.execute(
                "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
                (id, user_id)
            ).fetchone()
            return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))

        if not category or category not in categories:
            flash("Invalid category selected.")
            expense = db.execute(
                "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
                (id, user_id)
            ).fetchone()
            return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))

        if not date_str:
            flash("Date is required.")
            expense = db.execute(
                "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
                (id, user_id)
            ).fetchone()
            return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            expense = db.execute(
                "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
                (id, user_id)
            ).fetchone()
            return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))

        # Map category name to id
        cat_row = db.execute("SELECT id FROM categories WHERE name = ?", (category,)).fetchone()
        if not cat_row:
            flash("Category not found in database.")
            expense = db.execute(
                "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
                (id, user_id)
            ).fetchone()
            return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))

        category_id = cat_row["id"]

        # Update expense
        result = db.execute(
            "UPDATE expenses SET category_id = ?, amount = ?, description = ?, date = ? WHERE id = ? AND user_id = ?",
            (category_id, amount, description or None, date_str, id, user_id)
        )
        db.commit()

        if result.rowcount == 0:
            flash("Expense not found or you are not authorized to edit it.")
            return redirect(url_for("profile"))

        flash("Expense updated successfully!")
        return redirect(url_for("profile"))

    # GET request
    expense = db.execute(
        "SELECT e.id, e.amount, e.category_id, e.description, e.date, c.name as category_name FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.id = ? AND e.user_id = ?",
        (id, user_id)
    ).fetchone()

    if not expense:
        flash("Expense not found or unauthorized.")
        return redirect(url_for("profile"))

    return render_template("edit_expense.html", expense=expense, categories=categories, today=datetime.now().strftime("%Y-%m-%d"))



@app.route("/expenses/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    db = get_db()

    # Step 2 & 3: Fetch and Ownership Check
    expense = db.execute("SELECT id, user_id FROM expenses WHERE id = ?", (expense_id,)).fetchone()

    if not expense:
        flash("Expense not found")
        return redirect(url_for("profile"))

    if expense["user_id"] != user_id:
        flash("You are not authorized to delete this expense")
        return redirect(url_for("profile"))

    # Step 4: Delete from Database
    db.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    db.commit()

    flash("Expense deleted successfully!")
    return redirect(url_for("profile"))



if __name__ == "__main__":
    with app.app_context():
        seed_custom_user("Demo User 2", "demo2@spendly.com", "test123")
    app.run(debug=True, port=5001)
