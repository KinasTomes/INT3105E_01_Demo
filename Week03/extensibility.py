# app.py
# ===========================================
# API QUẢN LÝ SÁCH - v1 vs v2
# - v1: price = float, year
# - v2: price = {amount, currency}, published_year, stock
# - Methods: GET, POST, PUT, PATCH (UPDATE)
# - Lưu trữ in-memory (demo)
# ===========================================

from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Book Management API (v1 & v2)", version="1.0.0")


# Small root endpoint to avoid 404 at GET /
@app.get("/", include_in_schema=False)
def root():
    """Redirect root to the interactive API docs (Swagger UI)."""
    return RedirectResponse(url="/docs")

# -----------------------------
# Internal canonical model (v2-like)
# -----------------------------
class _InternalBook(BaseModel):
    id: int
    title: str
    author: str
    price_amount: float
    currency: str = "USD"
    published_year: Optional[int] = None
    stock: int = 0


# In-memory "database"
_DB: Dict[int, _InternalBook] = {}
_NEXT_ID = 1


def _next_id() -> int:
    global _NEXT_ID
    nid = _NEXT_ID
    _NEXT_ID += 1
    return nid


# -----------------------------
# v1 Schemas (projection)
# -----------------------------
class BookV1(BaseModel):
    id: int
    title: str
    author: str
    price: float = Field(..., description="Giá dạng số (float)")
    year: Optional[int] = Field(None, description="Năm xuất bản (tùy chọn)")

class BookV1Create(BaseModel):
    title: str
    author: str
    price: float
    year: Optional[int] = None

class BookV1UpdatePUT(BaseModel):
    title: str
    author: str
    price: float
    year: Optional[int] = None

class BookV1UpdatePATCH(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    year: Optional[int] = None


# -----------------------------
# v2 Schemas (richer)
# -----------------------------
class PriceV2(BaseModel):
    amount: float
    currency: str = Field("USD", min_length=3, max_length=3, description="Mã tiền tệ ISO (ví dụ: USD, VND)")

class BookV2(BaseModel):
    id: int
    title: str
    author: str
    price: PriceV2
    published_year: Optional[int] = None
    stock: int = 0

class BookV2Create(BaseModel):
    title: str
    author: str
    price: PriceV2
    published_year: Optional[int] = None
    stock: int = 0

class BookV2UpdatePUT(BaseModel):
    title: str
    author: str
    price: PriceV2
    published_year: Optional[int] = None
    stock: int = 0

class BookV2UpdatePATCH(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[PriceV2] = None
    published_year: Optional[int] = None
    stock: Optional[int] = None


# -----------------------------
# Mapping helpers v1 <-> internal, v2 <-> internal
# -----------------------------
def _to_v1(b: _InternalBook) -> BookV1:
    return BookV1(
        id=b.id,
        title=b.title,
        author=b.author,
        price=b.price_amount,
        year=b.published_year
    )

def _from_v1_create(payload: BookV1Create) -> _InternalBook:
    return _InternalBook(
        id=_next_id(),
        title=payload.title,
        author=payload.author,
        price_amount=payload.price,
        currency="USD",                      # v1 không có currency, mặc định USD
        published_year=payload.year,
        stock=0                              # v1 không có stock, mặc định 0
    )

def _apply_v1_put(existing: _InternalBook, payload: BookV1UpdatePUT) -> _InternalBook:
    return _InternalBook(
        id=existing.id,
        title=payload.title,
        author=payload.author,
        price_amount=payload.price,
        currency=existing.currency,          # giữ nguyên currency
        published_year=payload.year,
        stock=existing.stock                 # v1 không thao tác stock
    )

def _apply_v1_patch(existing: _InternalBook, patch: BookV1UpdatePATCH) -> _InternalBook:
    return _InternalBook(
        id=existing.id,
        title=patch.title if patch.title is not None else existing.title,
        author=patch.author if patch.author is not None else existing.author,
        price_amount=patch.price if patch.price is not None else existing.price_amount,
        currency=existing.currency,
        published_year=patch.year if patch.year is not None else existing.published_year,
        stock=existing.stock
    )

def _to_v2(b: _InternalBook) -> BookV2:
    return BookV2(
        id=b.id,
        title=b.title,
        author=b.author,
        price=PriceV2(amount=b.price_amount, currency=b.currency),
        published_year=b.published_year,
        stock=b.stock
    )

def _from_v2_create(payload: BookV2Create) -> _InternalBook:
    return _InternalBook(
        id=_next_id(),
        title=payload.title,
        author=payload.author,
        price_amount=payload.price.amount,
        currency=payload.price.currency,
        published_year=payload.published_year,
        stock=payload.stock
    )

def _apply_v2_put(existing: _InternalBook, payload: BookV2UpdatePUT) -> _InternalBook:
    return _InternalBook(
        id=existing.id,
        title=payload.title,
        author=payload.author,
        price_amount=payload.price.amount,
        currency=payload.price.currency,
        published_year=payload.published_year,
        stock=payload.stock
    )

def _apply_v2_patch(existing: _InternalBook, patch: BookV2UpdatePATCH) -> _InternalBook:
    return _InternalBook(
        id=existing.id,
        title=patch.title if patch.title is not None else existing.title,
        author=patch.author if patch.author is not None else existing.author,
        price_amount=patch.price.amount if (patch.price and patch.price.amount is not None) else existing.price_amount,
        currency=patch.price.currency if (patch.price and patch.price.currency is not None) else existing.currency,
        published_year=patch.published_year if patch.published_year is not None else existing.published_year,
        stock=patch.stock if patch.stock is not None else existing.stock
    )


# -----------------------------
# Seed data (optional)
# -----------------------------
def _seed():
    global _DB, _NEXT_ID
    if _DB:
        return
    s1 = _InternalBook(id=_next_id(), title="Clean Code", author="Robert C. Martin", price_amount=25.5, currency="USD", published_year=2008, stock=10)
    s2 = _InternalBook(id=_next_id(), title="Design Patterns", author="Erich Gamma", price_amount=30.0, currency="USD", published_year=1994, stock=5)
    _DB[s1.id] = s1
    _DB[s2.id] = s2

_seed()


# =============================================================================
# API v1 - Books (price = float, year)
# =============================================================================

@app.get("/api/v1/books", response_model=List[BookV1], tags=["Books (v1)"])
def list_books_v1(
    q: Optional[str] = Query(None, description="Tìm theo title/author (chứa chuỗi)")
):
    result = []
    for b in _DB.values():
        if q:
            text = f"{b.title} {b.author}".lower()
            if q.lower() not in text:
                continue
        result.append(_to_v1(b))
    return result

@app.get("/api/v1/books/{book_id}", response_model=BookV1, tags=["Books (v1)"])
def get_book_v1(book_id: int = Path(..., ge=1)):
    b = _DB.get(book_id)
    if not b:
        raise HTTPException(status_code=404, detail="Book not found")
    return _to_v1(b)

@app.post("/api/v1/books", response_model=BookV1, status_code=201, tags=["Books (v1)"])
def create_book_v1(payload: BookV1Create):
    b = _from_v1_create(payload)
    _DB[b.id] = b
    return _to_v1(b)

@app.put("/api/v1/books/{book_id}", response_model=BookV1, tags=["Books (v1)"])
def update_book_put_v1(book_id: int, payload: BookV1UpdatePUT):
    existing = _DB.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")
    updated = _apply_v1_put(existing, payload)
    _DB[book_id] = updated
    return _to_v1(updated)

@app.patch("/api/v1/books/{book_id}", response_model=BookV1, tags=["Books (v1)"])
def update_book_patch_v1(book_id: int, patch: BookV1UpdatePATCH):
    existing = _DB.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")
    updated = _apply_v1_patch(existing, patch)
    _DB[book_id] = updated
    return _to_v1(updated)


# =============================================================================
# API v2 - Books (price = {amount, currency}, published_year, stock)
# =============================================================================

@app.get("/api/v2/books", response_model=List[BookV2], tags=["Books (v2)"])
def list_books_v2(
    q: Optional[str] = Query(None, description="Tìm theo title/author (chứa chuỗi)"),
    min_price: Optional[float] = Query(None, ge=0, description="Lọc giá tối thiểu (amount)"),
    max_price: Optional[float] = Query(None, ge=0, description="Lọc giá tối đa (amount)"),
    currency: Optional[str] = Query(None, min_length=3, max_length=3, description="Mã tiền tệ ISO (ví dụ USD, VND)")
):
    result = []
    for b in _DB.values():
        if q:
            text = f"{b.title} {b.author}".lower()
            if q.lower() not in text:
                continue
        if currency and b.currency != currency:
            continue
        if min_price is not None and b.price_amount < min_price:
            continue
        if max_price is not None and b.price_amount > max_price:
            continue
        result.append(_to_v2(b))
    return result

@app.get("/api/v2/books/{book_id}", response_model=BookV2, tags=["Books (v2)"])
def get_book_v2(book_id: int = Path(..., ge=1)):
    b = _DB.get(book_id)
    if not b:
        raise HTTPException(status_code=404, detail="Book not found")
    return _to_v2(b)

@app.post("/api/v2/books", response_model=BookV2, status_code=201, tags=["Books (v2)"])
def create_book_v2(payload: BookV2Create):
    b = _from_v2_create(payload)
    _DB[b.id] = b
    return _to_v2(b)

@app.put("/api/v2/books/{book_id}", response_model=BookV2, tags=["Books (v2)"])
def update_book_put_v2(book_id: int, payload: BookV2UpdatePUT):
    existing = _DB.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")
    updated = _apply_v2_put(existing, payload)
    _DB[book_id] = updated
    return _to_v2(updated)

@app.patch("/api/v2/books/{book_id}", response_model=BookV2, tags=["Books (v2)"])
def update_book_patch_v2(book_id: int, patch: BookV2UpdatePATCH):
    existing = _DB.get(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")
    updated = _apply_v2_patch(existing, patch)
    _DB[book_id] = updated
    return _to_v2(updated)
