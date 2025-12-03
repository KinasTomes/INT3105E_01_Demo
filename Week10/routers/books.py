from fastapi import APIRouter, HTTPException
from typing import List

import crud
import schemas

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate):
    """Tạo sách mới"""
    db_book = crud.get_book_by_isbn(isbn=book.isbn)
    if db_book:
        raise HTTPException(status_code=400, detail="ISBN đã tồn tại")
    return crud.create_book(book=book)

@router.get("/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100):
    """Lấy danh sách tất cả sách"""
    books = crud.get_books(skip=skip, limit=limit)
    return books

@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int):
    """Lấy thông tin chi tiết một cuốn sách"""
    db_book = crud.get_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    return db_book

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate):
    """Cập nhật thông tin sách"""
    db_book = crud.update_book(book_id=book_id, book=book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    return db_book

@router.delete("/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int):
    """Xóa sách"""
    db_book = crud.delete_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    return db_book
