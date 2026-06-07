# Spec Document

## 1. Overview

Build a **Delete Expense** feature for the Spendly application where the logged-in user can permanently delete any of their own expenses.

A delete button is shown next to each expense. When clicked, the user sees a confirmation step before the expense is permanently removed from the database.

---

## 2. Depends on

- Step 01 — Database setup (expenses table must exist)
- Step 04 — Add Expense (expenses must exist to delete)
- User must be logged in (active session required)

---

## 3. Routes

| Method | URL | Description |
| --- | --- | --- |
| POST | /expenses/delete/<expense_id> | Delete the expense from the database after ownership check |

---

## 4. Where the Delete Button Appears

The delete button must appear wherever expenses are listed in the UI — for example on the expenses list page or the profile page recent transactions section.

Each expense row must have:
- An **Edit** button — links to the edit expense page
- A **Delete** button — triggers the delete flow

---

## 5. Confirmation Before Delete

Before permanently deleting, the user must confirm their intent.

Two acceptable approaches — Claude Code can choose either:

**Option A — Browser confirm dialog**
- Delete button triggers a JavaScript confirm popup
- Popup message: "Are you sure you want to delete this expense? This cannot be undone."
- If user clicks OK, the delete form is submitted
- If user clicks Cancel, nothing happens

**Option B — Confirmation page**
- Delete button takes user to a separate confirmation page
- Page shows the expense details (amount, category, date, description)
- Two buttons: "Yes, Delete" and "Cancel"
- Cancel returns to expenses list without deleting

---

## 6. Route Logic (POST /expenses/delete/<expense_id>)

Perform these steps in order:

**Step 1 — Session Check**
- If user_id is not in session, redirect to login page immediately

**Step 2 — Fetch the Expense**
- Fetch the expense row from the database where id matches expense_id from the URL
- If no expense is found, redirect to expenses list and flash an error message

**Step 3 — Ownership Check**
- Compare the expense's user_id column with the session user_id
- If they do not match, the user is trying to delete someone else's expense
- Redirect to expenses list and flash an error message
- Never allow a user to delete another user's expense under any circumstances

**Step 4 — Delete from Database**
- Delete the expense row where id matches expense_id AND user_id matches session user_id
- The WHERE clause must include both conditions for extra safety
- Use parameterized queries only

**Step 5 — Success**
- Flash a success message confirming the expense was deleted
- Redirect to the expenses list page

---

## 7. Why POST and Not GET for Delete

Delete must use POST method, not a plain link (GET).

Reason: A plain link can be accidentally triggered by browser prefetching, bots, or someone sharing the URL. Using POST with a form ensures the delete only happens when the user intentionally submits.

---

## 8. Files to Change

| File | What to Change |
| --- | --- |
| `app.py` | Add POST route for /expenses/delete/<expense_id> |
| `templates/expenses.html` | Add delete button with confirmation to each expense row |

---

## 9. Files to Create

- None — unless Option B confirmation page is chosen, then create `templates/confirm_delete.html`

---

## 10. Delete Button Requirements

The delete button in the template must:

- Be inside a small form with method POST pointing to /expenses/delete/<expense_id>
- Have a confirmation step before submitting (Option A or B from Section 5)
- Be visually distinct — red color to signal a destructive action
- Be placed next to the Edit button on each expense row
- Not be a plain anchor link

---

## 11. Ownership Rule — Most Important Security Rule

A user must only be able to delete their own expenses.

This check must happen in the POST route:
- Fetch the expense from the database using the expense_id from the URL
- Compare the expense's user_id with the session user_id
- If they are different, reject immediately and redirect
- The DELETE SQL query must also include user_id in the WHERE clause as a second layer of protection

---

## 12. Flash Message Cases

| Situation | Message Type | When to Show |
| --- | --- | --- |
| Expense deleted successfully | success | After successful database delete |
| Expense not found | error | When expense_id does not exist |
| Ownership check fails | error | When user tries to delete another user's expense |
| User not logged in | — | Redirect to login, no flash needed |

---

## 13. Expected Behavior

- Logged-in user sees a Delete button next to each of their expenses
- User clicks Delete
- Confirmation is shown — "Are you sure?"
- If user confirms: expense is permanently deleted from database, success message shown, redirected to expenses list
- If user cancels: nothing happens, expense remains
- If user tries to delete an expense that is not theirs: redirected with error message
- If user is not logged in: redirected to login immediately

---

## 14. Definition of Done

- [ ] Delete button appears on each expense row in the expenses list
- [ ] Delete button is visually red or styled as a destructive action
- [ ] Confirmation step is shown before deletion
- [ ] POST /expenses/delete/<expense_id> route exists in app.py
- [ ] Session is checked before any database operation
- [ ] Expense is fetched from database before deletion
- [ ] Ownership check runs — user can only delete their own expenses
- [ ] Delete query uses both expense id and user_id in WHERE clause
- [ ] Expense is permanently removed from database after confirmation
- [ ] Success message shown after deletion
- [ ] Error message shown if expense not found or ownership fails
- [ ] Delete uses POST method — not a plain GET link
- [ ] All database queries use parameterized syntax
- [ ] Page redirects to login if session is missing