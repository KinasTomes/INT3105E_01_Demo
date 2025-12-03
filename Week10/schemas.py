from pydantic import BaseModel
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
