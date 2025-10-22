# Books API (search & pagination)

This is a minimal FastAPI app that exposes endpoints to search and paginate `Book` records using SQLite + SQLModel.

Files:
- `books_api.py` — FastAPI application with endpoints:
  - GET /books — search + pagination
  - GET /books/{book_id} — get single book
  - POST /books — create book

Quick start (Windows PowerShell):

```powershell
# create and activate virtualenv (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Week05\requirements.txt

# run the app
uvicorn Week05.books_api:app --reload
```

Open http://127.0.0.1:8000/docs for interactive docs.

Notes:
- The app uses SQLite file `week05_books.db` created in the working directory.
- For simplicity authors are stored as a JSON array of author IDs on the `Book` record.
- This is a focused sample for searching and pagination; production code should add validation, authentication, and more robust error handling.
