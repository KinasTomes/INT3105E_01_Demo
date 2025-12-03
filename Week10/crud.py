from typing import List, Optional
import data_store
import schemas
from logger import logger

# CRUD cho Book
def get_book(book_id: int) -> Optional[dict]:
    for book in data_store.books:
        if book["id"] == book_id:
            return book
    return None

def get_books(skip: int = 0, limit: int = 100) -> List[dict]:
    return data_store.books[skip:skip + limit]

def get_book_by_isbn(isbn: str) -> Optional[dict]:
    for book in data_store.books:
        if book["isbn"] == isbn:
            return book
    return None

def create_book(book: schemas.BookCreate) -> dict:
    new_book = {
        "id": data_store.get_next_book_id(),
        **book.model_dump(),
        "available": book.quantity
    }
    data_store.books.append(new_book)
    logger.info(f"📚 Created new book: '{new_book['title']}' (ID: {new_book['id']})")
    return new_book

def update_book(book_id: int, book: schemas.BookUpdate) -> Optional[dict]:
    db_book = get_book(book_id)
    if db_book:
        update_data = book.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            db_book[key] = value
        logger.info(f"✏️ Updated book: '{db_book['title']}' (ID: {book_id})")
    return db_book

def delete_book(book_id: int) -> Optional[dict]:
    for i, book in enumerate(data_store.books):
        if book["id"] == book_id:
            deleted_book = data_store.books.pop(i)
            logger.warning(f"🗑️ Deleted book: '{deleted_book['title']}' (ID: {book_id})")
            return deleted_book
    return None
