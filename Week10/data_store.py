"""
In-memory data storage using lists
"""

from typing import List

# Storage lists
books: List[dict] = []

# Auto-increment IDs
next_book_id = 1

# Helper functions
def get_next_book_id() -> int:
    global next_book_id
    current_id = next_book_id
    next_book_id += 1
    return current_id

# Initialize with some sample data
def init_sample_data():
    """Khởi tạo dữ liệu mẫu"""
    global books
    
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
        },
        {
            "id": get_next_book_id(),
            "title": "Design Patterns",
            "author": "Gang of Four",
            "isbn": "978-0201633610",
            "published_year": 1994,
            "quantity": 4,
            "available": 4
        }
    ])

# Initialize sample data on module load
init_sample_data()

