from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timedelta

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Book Management API with JWT",
    description="Demo API quản lý sách với JWT Authentication (OpenAPI 3.1.0)",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "api-support@example.com",
    },
    license_info={
        "name": "MIT License",
    },
    openapi_url="/openapi.json"
)

security = HTTPBearer()

# ------------------------
# Định nghĩa mô hình dữ liệu
# ------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Book(BaseModel):
    id: int
    title: str
    author: str
    year: Optional[int] = None
    isbn: Optional[str] = None

class BookCreate(BaseModel):
    title: str
    author: str
    year: Optional[int] = None
    isbn: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None

# Fake users database (username: password)
users_db = {
    "admin": "admin123",
    "user": "user123"
}

# Fake books database
books_db = [
    Book(id=1, title="Python Programming", author="John Doe", year=2023, isbn="978-0123456789"),
    Book(id=2, title="Web Development", author="Jane Smith", year=2024, isbn="978-0987654321"),
    Book(id=3, title="Data Science", author="Bob Johnson", year=2023, isbn="978-1122334455")
]

# ------------------------
# JWT Helper Functions
# ------------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ------------------------
# Endpoints
# ------------------------

@app.get("/", include_in_schema=False)
def home():
    return {
        "message": "Book Management API with JWT Authentication",
        "docs": "/docs",
        "login": "POST /login with {username, password}"
    }

@app.post("/login", response_model=Token, summary="Login để lấy JWT token")
def login(request: LoginRequest):
    """
    Login với username và password để nhận JWT token.
    
    **Credentials:**
    - username: admin, password: admin123
    - username: user, password: user123
    """
    if request.username not in users_db or users_db[request.username] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": request.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/books", response_model=List[Book], summary="1. Lấy danh sách tất cả sách")
def get_books(username: str = Depends(verify_token)):
    """
    Lấy danh sách tất cả sách trong hệ thống.
    
    **Yêu cầu:** JWT token trong header Authorization: Bearer <token>
    """
    return books_db

@app.get("/books/{book_id}", response_model=Book, summary="2. Lấy thông tin một cuốn sách")
def get_book(book_id: int, username: str = Depends(verify_token)):
    """
    Lấy thông tin chi tiết của một cuốn sách theo ID.
    
    **Yêu cầu:** JWT token trong header Authorization: Bearer <token>
    """
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, summary="3. Thêm sách mới")
def create_book(book: BookCreate, username: str = Depends(verify_token)):
    """
    Thêm một cuốn sách mới vào hệ thống.
    
    **Yêu cầu:** JWT token trong header Authorization: Bearer <token>
    """
    new_id = max([b.id for b in books_db], default=0) + 1
    new_book = Book(
        id=new_id,
        title=book.title,
        author=book.author,
        year=book.year,
        isbn=book.isbn
    )
    books_db.append(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=Book, summary="4. Cập nhật thông tin sách")
def update_book(book_id: int, book: BookUpdate, username: str = Depends(verify_token)):
    """
    Cập nhật thông tin của một cuốn sách.
    
    **Yêu cầu:** JWT token trong header Authorization: Bearer <token>
    """
    for idx, existing_book in enumerate(books_db):
        if existing_book.id == book_id:
            updated_data = existing_book.dict()
            update_data = book.dict(exclude_unset=True)
            updated_data.update(update_data)
            books_db[idx] = Book(**updated_data)
            return books_db[idx]
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="5. Xóa sách")
def delete_book(book_id: int, username: str = Depends(verify_token)):
    """
    Xóa một cuốn sách khỏi hệ thống.
    
    **Yêu cầu:** JWT token trong header Authorization: Bearer <token>
    """
    global books_db
    for idx, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Book not found")

# Chạy ứng dụng với: uvicorn main:app --reload
if __name__ == '__main__':
    import uvicorn
    print("=== Book Management API with JWT ===")
    print("Login credentials:")
    print("  - admin / admin123")
    print("  - user / user123")
    print("Running on http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")