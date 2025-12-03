from fastapi import APIRouter, HTTPException
from typing import List

import crud
import schemas

router = APIRouter(
    prefix="/borrows",
    tags=["borrows"]
)

@router.post("/", response_model=schemas.BorrowRecordDetail)
def borrow_book(borrow: schemas.BorrowRecordCreate):
    """Mượn sách"""
    # Kiểm tra user tồn tại
    db_user = crud.get_user(user_id=borrow.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    if not db_user["is_active"]:
        raise HTTPException(status_code=400, detail="Người dùng không còn hoạt động")
    
    # Kiểm tra book tồn tại
    db_book = crud.get_book(book_id=borrow.book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách")
    
    # Tạo borrow record
    db_borrow = crud.create_borrow_record(borrow=borrow)
    if db_borrow is None:
        raise HTTPException(status_code=400, detail="Sách hiện không còn sẵn để mượn")
    
    return crud.get_borrow_with_details(db_borrow)

@router.put("/{borrow_id}/return", response_model=schemas.BorrowRecordDetail)
def return_book(borrow_id: int):
    """Trả sách"""
    db_borrow = crud.return_book(borrow_id=borrow_id)
    if db_borrow is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi mượn sách")
    return crud.get_borrow_with_details(db_borrow)

@router.get("/", response_model=List[schemas.BorrowRecordDetail])
def read_borrow_records(skip: int = 0, limit: int = 100):
    """Lấy danh sách tất cả bản ghi mượn sách"""
    borrows = crud.get_borrow_records(skip=skip, limit=limit)
    return [crud.get_borrow_with_details(b) for b in borrows]

@router.get("/active", response_model=List[schemas.BorrowRecordDetail])
def read_active_borrows(skip: int = 0, limit: int = 100):
    """Lấy danh sách các sách đang được mượn (chưa trả)"""
    borrows = crud.get_active_borrows(skip=skip, limit=limit)
    return [crud.get_borrow_with_details(b) for b in borrows]

@router.get("/{borrow_id}", response_model=schemas.BorrowRecordDetail)
def read_borrow_record(borrow_id: int):
    """Lấy thông tin chi tiết một bản ghi mượn sách"""
    db_borrow = crud.get_borrow_record(borrow_id=borrow_id)
    if db_borrow is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi mượn sách")
    return crud.get_borrow_with_details(db_borrow)
