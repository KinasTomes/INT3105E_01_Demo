# Payment API Demo

Demo API thanh toán với versioning (v1, v2) sử dụng FastAPI.

## Cấu trúc Project

```
payment-api/
├── main.py                 # Entry point với separate docs
├── requirements.txt        # Dependencies
├── openapi_v1.yaml        # OpenAPI spec cho v1
├── openapi_v2.yaml        # OpenAPI spec cho v2
├── MIGRATION_GUIDE.md     # Hướng dẫn migration v1 → v2
├── docs/
│   └── index.html         # Documentation hub page
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   └── routes.py      # Routes cho API v1 (deprecated)
│   └── v2/
│       ├── __init__.py
│       └── routes.py      # Routes cho API v2 (enhanced)
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

**Documentation Hub**: http://localhost:8000/docs (hoặc mở file `docs/index.html`)

## API Documentation

### Interactive Documentation

- **Combined Docs**: http://localhost:8000/docs (All versions)
- **v1 Only** ⚠️: http://localhost:8000/docs/v1 (Deprecated)
- **v2 Only**: http://localhost:8000/docs/v2 (Recommended)
- **ReDoc Combined**: http://localhost:8000/redoc
- **ReDoc v1**: http://localhost:8000/docs/v1/redoc
- **ReDoc v2**: http://localhost:8000/docs/v2/redoc

### OpenAPI Specifications

- **OpenAPI v1 Spec**: `openapi_v1.yaml` ⚠️ DEPRECATED
- **OpenAPI v2 Spec**: `openapi_v2.yaml`
- **v1 JSON**: http://localhost:8000/openapi/v1.json
- **v2 JSON**: http://localhost:8000/openapi/v2.json

### Guides

- **Migration Guide**: `MIGRATION_GUIDE.md`

## API Endpoints

### API v1 (`/api/v1`) ⚠️ DEPRECATED

> **⚠️ WARNING**: API v1 is deprecated and will be sunset on **01/06/2026**.  
> Please migrate to v2. See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for details.
>
> All v1 responses include deprecation headers:
> - `Deprecation: true`
> - `Sunset: Mon, 01 Jun 2026 00:00:00 GMT`
> - `Link: </api/v2>; rel="successor-version"`

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

### API v2 (`/api/v2`) - Enhanced Version

#### Tạo thanh toán với thông tin mở rộng
```http
POST /api/v2/payments
Content-Type: application/json

{
  "amount": 100000,
  "currency": "VND",
  "description": "Thanh toán đơn hàng #123",
  "customer": {
    "name": "Nguyễn Văn A",
    "email": "nguyenvana@example.com",
    "phone": "0901234567"
  },
  "metadata": {
    "order_id": "ORD-123",
    "product": "Laptop Dell XPS 13"
  },
  "webhook_url": "https://example.com/webhook"
}
```

#### Xem thông tin thanh toán (v2)
```http
GET /api/v2/payments/{payment_id}
```

#### Liệt kê thanh toán với phân trang và filter
```http
GET /api/v2/payments?limit=10&offset=0&status=pending&currency=VND
```

#### Cập nhật trạng thái thanh toán (NEW)
```http
PATCH /api/v2/payments/{payment_id}
Content-Type: application/json

{
  "status": "completed"
}
```

#### Hủy thanh toán (NEW)
```http
DELETE /api/v2/payments/{payment_id}
```

#### Đăng ký webhook (NEW)
```http
POST /api/v2/webhooks
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["payment.completed", "payment.failed"]
}
```

### So sánh v1 vs v2

| Tính năng | v1 | v2 |
|-----------|----|----|
| Tạo thanh toán | ✅ | ✅ |
| Xem thanh toán | ✅ | ✅ |
| Liệt kê thanh toán | ✅ | ✅ (với pagination) |
| Thông tin khách hàng | ❌ | ✅ |
| Metadata tùy chỉnh | ❌ | ✅ |
| Cập nhật trạng thái | ❌ | ✅ |
| Hủy thanh toán | ❌ | ✅ |
| Webhook notifications | ❌ | ✅ |
| Phân trang | ❌ | ✅ |
| Filter | ❌ | ✅ |

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

✅ **PHASE 4** — Implement API v1 (mock)
- Các endpoint v1 hoạt động đầy đủ
- In-memory storage cho demo
- Response theo đúng spec

✅ **PHASE 5** — Implement API v2 (mock)
- Các endpoint v2 với tính năng nâng cao
- OpenAPI specification cho v2
- Thể hiện rõ breaking changes và improvements

✅ **PHASE 6** — Thêm Deprecation Header cho v1
- Deprecation headers trên tất cả v1 responses
- Sunset date: 01/06/2026
- Link đến successor version (v2)
- Warning message cho developers

✅ **PHASE 7** — Viết Migration Guide
- Tài liệu chi tiết về breaking changes
- Request/Response mapping v1 → v2
- Step-by-step migration checklist
- Code examples và best practices

✅ **PHASE 9** — Tách Swagger UI cho 2 version
- Separate documentation pages cho v1 và v2
- `/docs/v1` - API v1 documentation (deprecated)
- `/docs/v2` - API v2 documentation (recommended)
- `/docs` - Combined documentation (all versions)
- Cross-links giữa các versions

## Testing với curl

### API v1 Examples

#### Tạo thanh toán
```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d "{\"amount\": 100000, \"currency\": \"VND\", \"description\": \"Test payment\"}"
```

#### Xem thanh toán
```bash
curl "http://localhost:8000/api/v1/payments/1"
```

#### Liệt kê thanh toán
```bash
curl "http://localhost:8000/api/v1/payments"
```

### API v2 Examples

#### Tạo thanh toán với thông tin đầy đủ
```bash
curl -X POST "http://localhost:8000/api/v2/payments" \
  -H "Content-Type: application/json" \
  -d "{\"amount\": 100000, \"currency\": \"VND\", \"description\": \"Test payment v2\", \"customer\": {\"name\": \"Nguyen Van A\", \"email\": \"test@example.com\", \"phone\": \"0901234567\"}, \"metadata\": {\"order_id\": \"ORD-123\"}}"
```

#### Liệt kê với phân trang
```bash
curl "http://localhost:8000/api/v2/payments?limit=5&offset=0"
```

#### Filter theo status
```bash
curl "http://localhost:8000/api/v2/payments?status=pending"
```

#### Cập nhật trạng thái
```bash
curl -X PATCH "http://localhost:8000/api/v2/payments/1" \
  -H "Content-Type: application/json" \
  -d "{\"status\": \"completed\"}"
```

#### Hủy thanh toán
```bash
curl -X DELETE "http://localhost:8000/api/v2/payments/1"
```

#### Đăng ký webhook
```bash
curl -X POST "http://localhost:8000/api/v2/webhooks" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://example.com/webhook\", \"events\": [\"payment.completed\", \"payment.failed\"]}"
```

## ⚠️ API v1 Deprecation Notice

**API v1 đã được đánh dấu DEPRECATED và sẽ ngừng hoạt động vào 01/06/2026.**

- Tất cả v1 endpoints trả về deprecation headers
- Không có updates hoặc bug fixes mới cho v1
- Vui lòng migrate sang v2 càng sớm càng tốt
- Xem chi tiết tại: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

## Lưu ý

- Dữ liệu được lưu trong memory (in-memory), sẽ mất khi restart server
- Đây là demo đơn giản, chưa có authentication/authorization
- v1 và v2 có storage riêng biệt (không share data)
