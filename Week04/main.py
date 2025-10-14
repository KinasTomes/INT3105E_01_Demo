from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="User Management API",
    description="Demo Swagger (OpenAPI 3.1.0) với FastAPI",
    version="1.0.0",
    contact={
        "name": "Hi",
        "email": "api-support@example.com",
    },
    license_info={
        "name": "MIT License",
    },
    openapi_url="/openapi.json"  # URL chứa file OpenAPI JSON
)

# ------------------------
# Định nghĩa mô hình dữ liệu
# ------------------------
class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

# Bộ nhớ tạm (giả lập database)
fake_db = [
    User(id=1, name="Nguyễn Văn A", email="a@example.com", age=30),
    User(id=2, name="Trần Thị B", email="b@example.com", age=25)
]

# ------------------------
# Định nghĩa các endpoint
# ------------------------

@app.get("/users", response_model=List[User], summary="Lấy danh sách người dùng")
def get_users():
    """
    Trả về danh sách tất cả người dùng trong hệ thống.
    """
    return fake_db


@app.get("/users/{user_id}", response_model=User, summary="Lấy chi tiết người dùng")
def get_user(user_id: int):
    """
    Truy vấn thông tin của một người dùng cụ thể qua ID.
    """
    for user in fake_db:
        if user.id == user_id:
            return user
    return {"error": "Không tìm thấy người dùng"}


@app.post("/users", response_model=User, summary="Thêm người dùng mới")
def create_user(user: User):
    """
    Thêm một người dùng mới vào danh sách (giả lập thao tác ghi DB).
    """
    fake_db.append(user)
    return user
