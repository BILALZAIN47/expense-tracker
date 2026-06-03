from flask import Flask, render_template, g, request, redirect, url_for, session, flash
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
        """SELECT e.date, e.description, c.name as category_name, e.amount
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
    with app.app_context():
        seed_custom_user("Demo User 2", "demo2@spendly.com", "test123")
    app.run(debug=True, port=5001)
