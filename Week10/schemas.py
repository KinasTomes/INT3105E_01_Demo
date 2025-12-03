from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Book Schemas
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    published_year: int
    quantity: int = 1

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    quantity: Optional[int] = None

class Book(BookBase):
    id: int
    available: int
    
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# BorrowRecord Schemas
class BorrowRecordBase(BaseModel):
    book_id: int
    user_id: int

class BorrowRecordCreate(BorrowRecordBase):
    pass

class BorrowRecord(BorrowRecordBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool
    
    class Config:
        from_attributes = True

class BorrowRecordDetail(BorrowRecord):
    book: Book
    user: User
    
    class Config:
        from_attributes = True
