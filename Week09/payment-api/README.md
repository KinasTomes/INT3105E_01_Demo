# Payment API Demo

Demo API thanh toán với versioning (v1, v2) sử dụng FastAPI.

## Cấu trúc Project

```
payment-api/
├── main.py                 # Entry point của ứng dụng
├── requirements.txt        # Dependencies
├── openapi_v1.yaml        # OpenAPI spec cho v1
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   └── routes.py      # Routes cho API v1
│   └── v2/
│       ├── __init__.py
│       └── routes.py      # Routes cho API v2 (placeholder)
```

## Cài đặt

### 1. Tạo virtual environment

```bash
python -m venv venv
```

### 2. Kích hoạt virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI v1 Spec**: `openapi_v1.yaml`

## API Endpoints

### API v1 (`/api/v1`)

#### Tạo thanh toán mới
```http
POST /api/v1/payments
Content-Type: application/json

{
  "amount": 100000,
  "currency": "VND",
  "description": "Thanh toán đơn hàng #123"
}
```

#### Xem thông tin thanh toán
```http
GET /api/v1/payments/{payment_id}
```

#### Liệt kê tất cả thanh toán
```http
GET /api/v1/payments
```

### API v2 (`/api/v2`)

Coming soon - Sẽ có các tính năng nâng cao.

## Phases Hoàn thành

✅ **PHASE 0** — Khởi tạo Project
- Project FastAPI với cấu trúc cơ bản
- Virtual environment setup
- Dependencies cơ bản

✅ **PHASE 1** — Thiết lập cấu trúc versioning
- Cấu trúc thư mục cho v1 và v2
- Routes riêng biệt cho mỗi version
- Prefix `/api/v1` và `/api/v2`

✅ **PHASE 2** — Viết tài liệu API v1
- OpenAPI specification cho v1
- Mô tả đầy đủ endpoints
- Examples và schemas

## Testing với curl

### Tạo thanh toán
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d "{\"amount\": 100000, \"currency\": \"VND\", \"description\": \"Test payment\"}"
```

### Xem thanh toán
```bash
curl "http://localhost:8000/api/v1/payments/1"
```

### Liệt kê thanh toán
```bash
curl "http://localhost:8000/api/v1/payments"
```

## Lưu ý

- Dữ liệu được lưu trong memory (in-memory), sẽ mất khi restart server
- Đây là demo đơn giản, chưa có authentication/authorization
- API v2 hiện tại chỉ là placeholder cho các tính năng tương lai
