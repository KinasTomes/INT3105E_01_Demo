from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Books API (in-memory, search & pagination)")


class Book(BaseModel):
    id: int
    title: str
    isbn: Optional[str] = None
    publish_year: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    authors: List[int] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# In-memory "database"
_books_db: List[Book] = []
_next_id = 1


def _seed():
    global _next_id
    if _books_db:
        return
    samples = [
        {
            "title": "Design Patterns",
            "isbn": "978-0201633610",
            "publish_year": 1994,
            "category_id": 1,
            "description": "Classic book on design patterns.",
            "authors": [1, 2],
        },
        {
            "title": "Clean Code",
            "isbn": "978-0132350884",
            "publish_year": 2008,
            "category_id": 2,
            "description": "A Handbook of Agile Software Craftsmanship.",
            "authors": [3],
        },
        {
            "title": "The Pragmatic Programmer",
            "isbn": "978-0201616224",
            "publish_year": 1999,
            "category_id": 2,
            "description": "From journeyman to master.",
            "authors": [4, 5],
        },
    ]
    for s in samples:
        global _next_id
        b = Book(id=_next_id, **s)
        _books_db.append(b)
        _next_id += 1


@app.on_event("startup")
def startup_event():
    _seed()


@app.get("/books", response_model=List[Book])
def list_books(
    q: Optional[str] = Query(None, description="Full-text search on title and description"),
    isbn: Optional[str] = Query(None),
    publish_year: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    sort: Optional[str] = Query(None, description="field to sort by: title, publish_year, created_at"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    results = _books_db

    # filters
    if q:
        qlow = q.lower()
        results = [b for b in results if qlow in b.title.lower() or (b.description and qlow in b.description.lower())]
    if isbn:
        results = [b for b in results if b.isbn == isbn]
    if publish_year:
        results = [b for b in results if b.publish_year == publish_year]
    if category_id:
        results = [b for b in results if b.category_id == category_id]

    # sorting
    if sort:
        reverse = False
        key = None
        if sort == "title":
            key = lambda b: b.title
        elif sort == "publish_year":
            key = lambda b: (b.publish_year or 0)
        elif sort == "created_at":
            key = lambda b: b.created_at
        if key:
            results = sorted(results, key=key, reverse=reverse)

    # pagination
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = results[start:end]

    return page_items


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for b in _books_db:
        if b.id == book_id:
            return b
    raise HTTPException(status_code=404, detail="Book not found")


class BookCreate(BaseModel):
    title: str
    isbn: Optional[str] = None
    publish_year: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    authors: List[int] = Field(default_factory=list)


@app.post("/books", response_model=Book, status_code=201)
def create_book(payload: BookCreate):
    global _next_id
    b = Book(id=_next_id, **payload.dict())
    _books_db.append(b)
    _next_id += 1
    return b
