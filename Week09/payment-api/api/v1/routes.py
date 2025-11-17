"""
API v1 Routes - Payment endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# In-memory storage for demo
payments_db = {}
payment_counter = 1


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "VND"
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    description: Optional[str]
    status: str
    created_at: str


@router.post("/payments", response_model=PaymentResponse)
async def create_payment(payment: PaymentRequest):
    """Tạo một thanh toán mới"""
    global payment_counter
    
    payment_id = payment_counter
    payment_counter += 1
    
    payment_data = {
        "id": payment_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    payments_db[payment_id] = payment_data
    return payment_data


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int):
    """Xem thông tin thanh toán"""
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payments_db[payment_id]


@router.get("/payments")
async def list_payments():
    """Liệt kê tất cả thanh toán"""
    return {"payments": list(payments_db.values())}
