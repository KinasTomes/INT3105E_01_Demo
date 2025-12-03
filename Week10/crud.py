from datetime import datetime
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
    return db_book

def delete_book(book_id: int) -> Optional[dict]:
    for i, book in enumerate(data_store.books):
        if book["id"] == book_id:
            deleted_book = data_store.books.pop(i)
            logger.warning(f"🗑️ Deleted book: '{deleted_book['title']}' (ID: {book_id})")
            return deleted_book
    return None

# CRUD cho User
def get_user(user_id: int) -> Optional[dict]:
    for user in data_store.users:
        if user["id"] == user_id:
            return user
    return None

def get_users(skip: int = 0, limit: int = 100) -> List[dict]:
    return data_store.users[skip:skip + limit]

def get_user_by_email(email: str) -> Optional[dict]:
    for user in data_store.users:
        if user["email"] == email:
            return user
    return None

def create_user(user: schemas.UserCreate) -> dict:
    new_user = {
        "id": data_store.get_next_user_id(),
        **user.model_dump(),
        "is_active": True
    }
    data_store.users.append(new_user)
    logger.info(f"👤 Created new user: '{new_user['name']}' (ID: {new_user['id']}, Email: {new_user['email']})")
    return new_user

def update_user(user_id: int, user: schemas.UserUpdate) -> Optional[dict]:
    db_user = get_user(user_id)
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            db_user[key] = value
    return db_user

def delete_user(user_id: int) -> Optional[dict]:
    for i, user in enumerate(data_store.users):
        if user["id"] == user_id:
            return data_store.users.pop(i)
    return None

# CRUD cho BorrowRecord
def create_borrow_record(borrow: schemas.BorrowRecordCreate) -> Optional[dict]:
    # Kiểm tra sách còn available không
    book = get_book(borrow.book_id)
    if not book or book["available"] <= 0:
        logger.warning(f"❌ Book borrow failed: Book ID {borrow.book_id} not available")
        return None
    
    user = get_user(borrow.user_id)
    
    # Tạo borrow record
    new_borrow = {
        "id": data_store.get_next_borrow_id(),
        **borrow.model_dump(),
        "borrow_date": datetime.now(),
        "return_date": None,
        "is_returned": False
    }
    data_store.borrow_records.append(new_borrow)
    
    # Giảm số lượng available của sách
    book["available"] -= 1
    
    logger.info(f"📖 Book borrowed: '{book['title']}' by '{user['name'] if user else 'Unknown'}' (Borrow ID: {new_borrow['id']}, Available: {book['available']})")
    
    return new_borrow

def return_book(borrow_id: int) -> Optional[dict]:
    db_borrow = None
    for borrow in data_store.borrow_records:
        if borrow["id"] == borrow_id:
            db_borrow = borrow
            break
    
    if db_borrow and not db_borrow["is_returned"]:
        db_borrow["is_returned"] = True
        db_borrow["return_date"] = datetime.now()
        
        # Tăng số lượng available của sách
        book = get_book(db_borrow["book_id"])
        user = get_user(db_borrow["user_id"])
        
        if book:
            book["available"] += 1
            logger.info(f"📚 Book returned: '{book['title']}' by '{user['name'] if user else 'Unknown'}' (Borrow ID: {borrow_id}, Available: {book['available']})")
    
    return db_borrow

def get_borrow_records(skip: int = 0, limit: int = 100) -> List[dict]:
    return data_store.borrow_records[skip:skip + limit]

def get_borrow_record(borrow_id: int) -> Optional[dict]:
    for borrow in data_store.borrow_records:
        if borrow["id"] == borrow_id:
            return borrow
    return None

def get_user_borrow_records(user_id: int) -> List[dict]:
    return [b for b in data_store.borrow_records if b["user_id"] == user_id]

def get_active_borrows(skip: int = 0, limit: int = 100) -> List[dict]:
    active = [b for b in data_store.borrow_records if not b["is_returned"]]
    return active[skip:skip + limit]

# Helper function to get borrow record with details
def get_borrow_with_details(borrow: dict) -> dict:
    book = get_book(borrow["book_id"])
    user = get_user(borrow["user_id"])
    return {
        **borrow,
        "book": book,
        "user": user
    }
