"""
API v2 Routes - Enhanced payment endpoints with advanced features
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

router = APIRouter()

# In-memory storage for demo (separate from v1)
payments_db_v2 = {}
payment_counter_v2 = 1
webhooks_db = {}
webhook_counter = 1


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PaymentRequestV2(BaseModel):
    amount: float
    currency: str = "VND"
    description: Optional[str] = None
    customer: Optional[CustomerInfo] = None
    metadata: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None


class PaymentResponseV2(BaseModel):
    id: int
    amount: float
    currency: str
    description: Optional[str]
    status: str
    customer: Optional[CustomerInfo]
    metadata: Optional[Dict[str, Any]]
    webhook_url: Optional[str]
    created_at: str
    updated_at: str


class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class PaymentListResponse(BaseModel):
    data: List[PaymentResponseV2]
    pagination: PaginationInfo


class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(processing|completed|failed)$")


class WebhookRequest(BaseModel):
    url: str
    events: List[str]


@router.get("/")
async def v2_info():
    """API v2 info endpoint"""
    return {
        "version": "2.0",
        "message": "API v2 - Enhanced with customer info, metadata, webhooks, and more",
        "new_features": [
            "Customer information support",
            "Custom metadata",
            "Webhook notifications",
            "Payment status updates",
            "Payment cancellation",
            "Pagination and filtering"
        ]
    }


@router.post("/payments", response_model=PaymentResponseV2)
async def create_payment_v2(payment: PaymentRequestV2):
    """
    Tạo một thanh toán mới với thông tin mở rộng (v2)
    
    Mới trong v2:
    - Thông tin khách hàng
    - Metadata tùy chỉnh
    - Webhook URL
    """
    global payment_counter_v2
    
    payment_id = payment_counter_v2
    payment_counter_v2 += 1
    
    now = datetime.now().isoformat()
    payment_data = {
        "id": payment_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "status": "pending",
        "customer": payment.customer.dict() if payment.customer else None,
        "metadata": payment.metadata,
        "webhook_url": payment.webhook_url,
        "created_at": now,
        "updated_at": now
    }
    
    payments_db_v2[payment_id] = payment_data
    return payment_data


@router.get("/payments/{payment_id}", response_model=PaymentResponseV2)
async def get_payment_v2(payment_id: int):
    """Xem thông tin thanh toán với dữ liệu mở rộng (v2)"""
    if payment_id not in payments_db_v2:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payments_db_v2[payment_id]


@router.get("/payments", response_model=PaymentListResponse)
async def list_payments_v2(
    limit: int = Query(10, ge=1, le=100, description="Số records trên trang"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu"),
    status: Optional[str] = Query(None, description="Filter theo status"),
    currency: Optional[str] = Query(None, description="Filter theo currency")
):
    """
    Liệt kê thanh toán với phân trang và filter (v2)
    
    Mới trong v2:
    - Pagination với limit/offset
    - Filter theo status và currency
    - Metadata về tổng số records
    """
    # Filter payments
    filtered_payments = list(payments_db_v2.values())
    
    if status:
        filtered_payments = [p for p in filtered_payments if p["status"] == status]
    
    if currency:
        filtered_payments = [p for p in filtered_payments if p["currency"] == currency]
    
    total = len(filtered_payments)
    
    # Apply pagination
    paginated_payments = filtered_payments[offset:offset + limit]
    
    has_more = (offset + limit) < total
    
    return {
        "data": paginated_payments,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": has_more
        }
    }


@router.patch("/payments/{payment_id}", response_model=PaymentResponseV2)
async def update_payment_status(payment_id: int, status_update: StatusUpdate):
    """
    Cập nhật trạng thái thanh toán (v2)
    
    Mới trong v2: Endpoint này không có trong v1
    """
    if payment_id not in payments_db_v2:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment = payments_db_v2[payment_id]
    
    # Validate status transition
    current_status = payment["status"]
    new_status = status_update.status
    
    if current_status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot update cancelled payment")
    
    if current_status in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot update {current_status} payment")
    
    payment["status"] = new_status
    payment["updated_at"] = datetime.now().isoformat()
    
    return payment


@router.delete("/payments/{payment_id}")
async def cancel_payment(payment_id: int):
    """
    Hủy thanh toán (v2)
    
    Mới trong v2: Endpoint này không có trong v1
    """
    if payment_id not in payments_db_v2:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment = payments_db_v2[payment_id]
    
    if payment["status"] != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel payment with status: {payment['status']}"
        )
    
    payment["status"] = "cancelled"
    payment["updated_at"] = datetime.now().isoformat()
    
    return {
        "message": "Payment cancelled successfully",
        "payment": payment
    }


@router.post("/webhooks")
async def register_webhook(webhook: WebhookRequest):
    """
    Đăng ký webhook để nhận thông báo (v2)
    
    Mới trong v2: Tính năng webhook hoàn toàn mới
    """
    global webhook_counter
    
    webhook_id = f"wh_{webhook_counter}"
    webhook_counter += 1
    
    webhook_data = {
        "webhook_id": webhook_id,
        "url": webhook.url,
        "events": webhook.events,
        "created_at": datetime.now().isoformat()
    }
    
    webhooks_db[webhook_id] = webhook_data
    
    return {
        "webhook_id": webhook_id,
        "url": webhook.url,
        "events": webhook.events
    }
