# Resources Tree — API Endpoint Hierarchy

This document maps the data model from `data-model.md` and `data-model.sql` to a hierarchical set of RESTful API endpoints. It shows resources, common HTTP methods, typical request/response shapes (summary), and query parameters for listing/filtering.

Goals:
- Provide a clear resource hierarchy and relationship-based endpoints.
- Suggest common query parameters and example payload attributes.
- Keep endpoints predictable and easy to implement.

---

## Top-level resources

- /authors
- /books
- /book-copies
- /loans
- /readers
- /categories
- /staff
- /reviews

---

## Resource tree (hierarchical view)

```
/ (root)
├─ /authors
│  ├─ GET /authors — list authors (q, page, per_page)
│  ├─ POST /authors — create author { name, biography }
│  ├─ GET /authors/{author_id} — get author
│  ├─ PUT /authors/{author_id} — replace author
│  ├─ PATCH /authors/{author_id} — partial update
│  └─ DELETE /authors/{author_id}
│     └─ /authors/{author_id}/books — GET books by author (convenience)

├─ /categories
│  ├─ GET /categories — list categories
│  ├─ POST /categories — create category { name, description }
│  ├─ GET /categories/{category_id}
│  ├─ PUT /categories/{category_id}
│  ├─ PATCH /categories/{category_id}
│  └─ DELETE /categories/{category_id}
│     └─ /categories/{category_id}/books — GET books in category

├─ /books
│  ├─ GET /books — list books (q, author_id, category_id, publish_year, isbn, sort, page, per_page)
│  ├─ POST /books — create book {
│  │       title, isbn, publish_year, category_id, description, authors: [author_id...]
│  │     }
│  ├─ GET /books/{book_id} — get book details
│  ├─ PUT /books/{book_id} — replace book (full payload)
│  ├─ PATCH /books/{book_id} — partial update
│  ├─ DELETE /books/{book_id}
│  ├─ /books/{book_id}/copies — GET list of copies for a book
│  │   ├─ POST /books/{book_id}/copies — create copy { shelf_location, status, barcode }
│  │   └─ GET /books/{book_id}/copies/{copy_id} — get copy
│  └─ /books/{book_id}/reviews — GET reviews for a book
│      ├─ POST /books/{book_id}/reviews — create review { reader_id, rating, comment }
│      └─ GET /books/{book_id}/reviews/{review_id}

├─ /book-copies
│  ├─ GET /book-copies — list copies (book_id, status)
│  ├─ GET /book-copies/{copy_id} — get copy
│  ├─ PUT /book-copies/{copy_id}
│  ├─ PATCH /book-copies/{copy_id}
│  └─ DELETE /book-copies/{copy_id}

├─ /readers
│  ├─ GET /readers — list readers (q, membership_level)
│  ├─ POST /readers — create reader { name, email, phone, address, membership_level }
│  ├─ GET /readers/{reader_id}
│  ├─ PUT /readers/{reader_id}
│  ├─ PATCH /readers/{reader_id}
│  └─ DELETE /readers/{reader_id}
│     └─ /readers/{reader_id}/loans — GET loans for a reader

├─ /staff
│  ├─ GET /staff — list staff
│  ├─ POST /staff — create staff { name, email, role }
│  ├─ GET /staff/{staff_id}
│  ├─ PUT /staff/{staff_id}
│  └─ PATCH /staff/{staff_id}

├─ /loans
│  ├─ GET /loans — list loans (reader_id, copy_id, status, overdue)
│  ├─ POST /loans — create loan { reader_id, copy_id, staff_id, due_date }
│  ├─ GET /loans/{loan_id}
│  ├─ PATCH /loans/{loan_id} — partial update (e.g., return_date)
│  └─ PUT /loans/{loan_id} — replace loan record

└─ /reviews
   ├─ GET /reviews — list reviews (book_id, reader_id, rating)
   ├─ POST /reviews — create review { reader_id, book_id, rating, comment }
   ├─ GET /reviews/{review_id}
   └─ DELETE /reviews/{review_id}
```

---

## Common query parameters and filters

- q: full-text search across name/title/author
- page, per_page: pagination
- sort: e.g. created_at, publish_year, title
- status: for copies and loans (available, loaned, lost, ongoing, returned)
- overdue=true: for loans where due_date < today and return_date IS NULL

---

## Example payloads (summaries)

- Create Book
  {
    "title": "Design Patterns",
    "isbn": "978-0201633610",
    "publish_year": 1994,
    "category_id": 3,
    "description": "...",
    "authors": [1, 2]
  }

- Create Book Copy
  { "shelf_location": "A3-12", "status": "available", "barcode": "BC123456" }

- Create Loan
  { "reader_id": 10, "copy_id": 24, "staff_id": 2, "due_date": "2025-11-21" }

- Create Review
  { "reader_id": 10, "rating": 5, "comment": "Great book!" }

---

## Notes & recommendations

- Use nested endpoints for convenience (e.g., `/books/{id}/copies`) but keep canonical resources at top-level (`/book-copies`) so each resource can be addressed independently.
- Enforce referential integrity in the DB and validate foreign keys in the API layer with clear 4xx responses.
- Consider adding batch endpoints for bulk imports (e.g., POST /books/bulk) if needed.

---

Generated from `data-model.md` and `data-model.sql`.
