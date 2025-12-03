from fastapi import APIRouter, HTTPException
from typing import List

import crud
import schemas

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    """Tạo người dùng mới"""
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    return crud.create_user(user=user)

@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100):
    """Lấy danh sách tất cả người dùng"""
    users = crud.get_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int):
    """Lấy thông tin chi tiết một người dùng"""
    db_user = crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate):
    """Cập nhật thông tin người dùng"""
    db_user = crud.update_user(user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return db_user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(user_id: int):
    """Xóa người dùng"""
    db_user = crud.delete_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return db_user

@router.get("/{user_id}/borrows", response_model=List[schemas.BorrowRecord])
def read_user_borrows(user_id: int):
    """Lấy lịch sử mượn sách của người dùng"""
    db_user = crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return crud.get_user_borrow_records(user_id=user_id)
