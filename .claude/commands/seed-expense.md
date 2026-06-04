# Seed Expense

Seed random expenses for a specific user for a given month.

## Arguments
- `user_id`: The ID of the user to seed expenses for.
- `month`: The month to seed (e.g., "05" or "2026-05").

## Execution
Run the following Python script:
```bash
python3 -c "from database.db import seed_expenses_for_user; seed_expenses_for_user(<user_id>, '<month>')"
```
Note: This requires a Flask app context, so the implementation in `database/db.py` handles that.
