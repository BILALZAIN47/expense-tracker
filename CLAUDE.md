# Spendly - Expense Tracker

## Project Overview
Spendly is a Flask-based expense tracking application that allows users to register, log in, and manage their daily expenses. It provides spending analytics, profile overviews, and categorized expense tracking.

## Technical Stack
- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS (static), Jinja2 templates
- **Security**: Werkzeug password hashing

## Project Structure
- `app.py`: Main application file containing routes and application configuration.
- `database/`: Database management logic (initialization, seeding, and queries).
- `templates/`: HTML files for the user interface.
- `static/`: Static assets (CSS, JS, Images).
- `.claude/spec/`: Detailed feature specifications.
- `database.sqlite`: The SQLite database file.

## Development Commands
- **Run Application**: `python app.py` (runs on `http://127.0.0.1:5001`)
- **Initialize Database**: `flask --app app init-db` (Initializes the database and seeds sample data)

## Coding Guidelines
- **Routing**: Use clear and descriptive route names.
- **Database Access**: Use `get_db()` to obtain a database connection and ensure queries are parameterized to prevent SQL injection.
- **Session Management**: Use Flask `session` for user authentication and state.
- **Error Handling**: Use `flash()` messages to provide feedback to the user.
- **Consistency**: Follow the existing pattern of separating routes from database logic.

## Common Workflows
- **Adding a Feature**:
    1. Refer to the specifications in `.claude/spec/`.
    2. Implement the backend logic in `app.py` or `database/`.
    3. Create/Update corresponding HTML templates in `templates/`.
    4. Verify functionality by running the app and testing the flow.
- **Database Changes**:
    1. Update the database schema in the `database/` module.
    2. Update the `init-db` command to include new tables/seed data.
    3. Run `flask --app app init-db` to reset the local database.
