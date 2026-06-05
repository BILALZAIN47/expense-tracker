# Spec Document

## 1. Overview

Build an **Add Expense** feature for the Spendly application where the logged-in user can fill a form and save a new expense to the database.

The expense is linked to the currently logged-in user automatically — the user does not select or enter their own user_id.

---

## 2. Depends on

- Step 01 — Database setup (expenses table must exist)
- User must be logged in (active session required)

---

## 3. Routes

| Method | URL | Description |
| --- | --- | --- |
| GET | /expenses/add | Show the empty Add Expense form |
| POST | /expenses/add | Receive form data, validate it, and save to database |

---

## 4. Add Expense Form Fields

The form must contain exactly these fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| Amount | Number input | Yes | Must be greater than 0 |
| Category | Dropdown select | Yes | Fixed list of 7 options only |
| Date | Date input | Yes | Must be in YYYY-MM-DD format |
| Description | Text area | No | Optional, can be left empty |

---

## 5. Category Dropdown Options

The category dropdown must show exactly these 7 options and no others:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

---

## 6. Route Logic

---

### GET /expenses/add

- Check session — if user is not logged in, redirect to login page
- Render the add expense form template
- Pass the category list to the template for the dropdown

---

### POST /expenses/add

Perform these steps in order:

**Step 1 — Session Check**
- If user_id is not in session, redirect to login page immediately

**Step 2 — Read Form Data**
- Read these four values from the submitted form:
  - amount
  - category
  - date
  - description (can be empty)

**Step 3 — Validate the Data**
- Amount must not be empty
- Amount must be a valid number
- Amount must be greater than zero
- Category must not be empty
- Category must be one of the 7 allowed values listed above
- Date must not be empty
- Date must be a valid date in YYYY-MM-DD format

**Step 4 — Handle Validation Failure**
- If any validation check fails, do not insert anything into the database
- Flash an error message explaining what went wrong
- Redirect back to the add expense form
- The user should be able to try again

**Step 5 — Insert into Database**
- Get the user_id from the session
- Insert a new row into the expenses table with these values:
  - user_id — from session
  - amount — from form, stored as a decimal number
  - category — from form
  - date — from form
  - description — from form, store as null if left empty
- Use parameterized queries only — never put form values directly into SQL text
- Do not set id or created_at manually — database handles these automatically

**Step 6 — Success**
- After successful insert, flash a success message
- Redirect the user to the expenses list page or dashboard

---

## 7. Files to Change

| File | What to Change |
| --- | --- |
| `app.py` | Add GET and POST routes for /expenses/add |

---

## 8. Files to Create

| File | Purpose |
| --- | --- |
| `templates/add_expense.html` | Form page for adding a new expense |

---

## 9. Template Requirements (add_expense.html)

- Extend base.html
- Page title: "Add Expense"
- Form must send data using POST method to /expenses/add
- Amount field: number input, accepts decimals, placeholder like "0.00"
- Category field: dropdown select with all 7 categories listed
- Date field: date picker input, defaults to today's date
- Description field: textarea, optional, placeholder like "What was this for?"
- Submit button: labeled "Add Expense"
- Flash message area at top for success or error feedback
- A back link or cancel button to return to expenses list

---

## 10. Variables to Pass to Template

| Variable Name | Type | Description |
| --- | --- | --- |
| categories | List | The 7 allowed category names for the dropdown |

---

## 11. Security Rules

- Always check session before rendering the form or processing submission
- Never trust form input — always validate on the server side
- Never insert user_id from the form — always take it from the session only
- Always use parameterized queries — never format SQL strings manually
- If session is missing at any point, redirect to login immediately

---

## 12. Validation Rules Summary

| Field | Rule |
| --- | --- |
| amount | Required, must be a number, must be greater than 0 |
| category | Required, must match one of the 7 allowed values exactly |
| date | Required, must be a valid date |
| description | Optional, no validation needed |

---

## 13. Flash Message Cases

| Situation | Message Type | When to Show |
| --- | --- | --- |
| Expense saved successfully | success | After successful database insert |
| Amount is missing or invalid | error | When amount fails validation |
| Category is missing or invalid | error | When category fails validation |
| Date is missing or invalid | error | When date fails validation |

---

## 14. Expected Behavior

- Logged-in user opens the add expense form
- User fills in amount, selects category, picks a date, optionally adds description
- User clicks submit
- If validation passes: expense is saved to database linked to this user, success message shown
- If validation fails: error message shown, form shown again, nothing saved to database
- If user is not logged in: redirected to login page immediately

---

## 15. Definition of Done

- [ ] GET /expenses/add shows the form to logged-in users
- [ ] Form has all 4 fields: amount, category, date, description
- [ ] Category dropdown shows exactly 7 options
- [ ] POST /expenses/add validates all required fields
- [ ] Invalid amount is rejected with error message
- [ ] Invalid category is rejected with error message
- [ ] Missing date is rejected with error message
- [ ] Valid form submission saves expense to database
- [ ] Saved expense is linked to the logged-in user's user_id from session
- [ ] User_id is never taken from the form — always from session only
- [ ] Success message shown after save
- [ ] Error message shown when validation fails
- [ ] Page redirects to login if session is missing
- [ ] All database inserts use parameterized queries
- [ ] Description is stored as null when left empty