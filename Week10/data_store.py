"""
In-memory data storage using lists
"""

from datetime import datetime
from typing import List, Optional

# Storage lists
books: List[dict] = []
users: List[dict] = []
borrow_records: List[dict] = []

# Auto-increment IDs
next_book_id = 1
next_user_id = 1
next_borrow_id = 1

# Helper functions
def get_next_book_id() -> int:
    global next_book_id
    current_id = next_book_id
    next_book_id += 1
    return current_id

def get_next_user_id() -> int:
    global next_user_id
    current_id = next_user_id
    next_user_id += 1
    return current_id

def get_next_borrow_id() -> int:
    global next_borrow_id
    current_id = next_borrow_id
    next_borrow_id += 1
    return current_id

# Initialize with some sample data
def init_sample_data():
    """Khởi tạo dữ liệu mẫu"""
    global books, users, borrow_records
    
    # Sample books
    books.extend([
        {
            "id": get_next_book_id(),
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "978-0132350884",
            "published_year": 2008,
            "quantity": 5,
            "available": 5
        },
        {
            "id": get_next_book_id(),
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt, David Thomas",
            "isbn": "978-0201616224",
            "published_year": 1999,
            "quantity": 3,
            "available": 3
        }
    ])
    
    # Sample users
    users.extend([
        {
            "id": get_next_user_id(),
            "name": "Nguyễn Văn A",
            "email": "nguyenvana@example.com",
            "phone": "0123456789",
            "is_active": True
        },
        {
            "id": get_next_user_id(),
            "name": "Trần Thị B",
            "email": "tranthib@example.com",
            "phone": "0987654321",
            "is_active": True
        }
    ])

# Initialize sample data on module load
init_sample_data()

