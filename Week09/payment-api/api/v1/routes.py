"""
API v1 Routes - Payment endpoints

⚠️ DEPRECATED: This API version is deprecated and will be sunset on 2026-06-01.
Please migrate to API v2 for enhanced features and continued support.
Migration guide: /docs/MIGRATION_GUIDE.md
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

# Deprecation metadata
DEPRECATION_DATE = "true"
SUNSET_DATE = "Mon, 01 Jun 2026 00:00:00 GMT"
MIGRATION_LINK = "</api/v2>; rel=\"successor-version\""


def add_deprecation_headers(response: Response):
    """Add deprecation headers to all v1 responses"""
    response.headers["Deprecation"] = DEPRECATION_DATE
    response.headers["Sunset"] = SUNSET_DATE
    response.headers["Link"] = MIGRATION_LINK
    response.headers["X-API-Warn"] = "API v1 is deprecated. Please migrate to v2. See /docs/MIGRATION_GUIDE.md"

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
async def create_payment(payment: PaymentRequest, response: Response):
    """
    Tạo một thanh toán mới
    
    ⚠️ DEPRECATED: Use POST /api/v2/payments instead
    """
    add_deprecation_headers(response)
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
async def get_payment(payment_id: int, response: Response):
    """
    Xem thông tin thanh toán
    
    ⚠️ DEPRECATED: Use GET /api/v2/payments/{payment_id} instead
    """
    add_deprecation_headers(response)
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payments_db[payment_id]


@router.get("/payments")
async def list_payments(response: Response):
    """
    Liệt kê tất cả thanh toán
    
    ⚠️ DEPRECATED: Use GET /api/v2/payments instead (with pagination support)
    """
    add_deprecation_headers(response)
    return {"payments": list(payments_db.values())}
