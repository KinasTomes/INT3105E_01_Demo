# Migration Guide: API v1 → v2

## 📋 Tổng quan

API v1 đã được đánh dấu **DEPRECATED** và sẽ ngừng hoạt động vào **01/06/2026**.

Tài liệu này hướng dẫn chi tiết cách migrate từ v1 sang v2.

## ⚠️ Thông tin Deprecation

- **Deprecation Date**: Ngay bây giờ (API v1 vẫn hoạt động nhưng không được khuyến khích)
- **Sunset Date**: 01/06/2026
- **Migration Deadline**: Trước 01/06/2026
- **Support**: API v1 sẽ không nhận updates hoặc bug fixes mới

## 🔔 Nhận biết Deprecation

Tất cả responses từ API v1 sẽ có các headers sau:

```http
Deprecation: true
Sunset: Mon, 01 Jun 2026 00:00:00 GMT
Link: </api/v2>; rel="successor-version"
X-API-Warn: API v1 is deprecated. Please migrate to v2. See /docs/MIGRATION_GUIDE.md
```

## 🆕 Tính năng mới trong v2

### 1. Thông tin khách hàng (Customer Info)
- Lưu trữ thông tin người thanh toán
- Fields: `name`, `email`, `phone`

### 2. Metadata tùy chỉnh
- Lưu trữ dữ liệu bổ sung theo nhu cầu
- Hỗ trợ bất kỳ key-value nào

### 3. Webhook Notifications
- Đăng ký webhook để nhận thông báo real-time
- Hỗ trợ các events: `payment.created`, `payment.completed`, `payment.failed`, `payment.cancelled`

### 4. Quản lý trạng thái nâng cao
- Cập nhật trạng thái thanh toán: `PATCH /payments/{id}`
- Hủy thanh toán: `DELETE /payments/{id}`
- Thêm status mới: `processing`, `cancelled`

### 5. Pagination & Filtering
- Phân trang với `limit` và `offset`
- Filter theo `status` và `currency`
- Response bao gồm metadata về pagination

## 🔄 Breaking Changes

### 1. Response Format thay đổi

#### v1 - List Payments Response
```json
{
  "payments": [
    {
      "id": 1,
      "amount": 100000,
      "currency": "VND",
      "description": "Test",
      "status": "pending",
      "created_at": "2025-11-19T10:30:00"
    }
  ]
}
```

#### v2 - List Payments Response
```json
{
  "data": [
    {
      "id": 1,
      "amount": 100000,
      "currency": "VND",
      "description": "Test",
      "status": "pending",
      "customer": null,
      "metadata": null,
      "webhook_url": null,
      "created_at": "2025-11-19T10:30:00",
      "updated_at": "2025-11-19T10:30:00"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
  }
}
```

**⚠️ Action Required:**
- Thay đổi code từ `response.payments` → `response.data`
- Xử lý pagination metadata

### 2. Payment Response có thêm fields

#### Các fields mới (optional):
- `customer`: Object chứa thông tin khách hàng
- `metadata`: Object chứa dữ liệu tùy chỉnh
- `webhook_url`: URL để nhận notifications
- `updated_at`: Timestamp cập nhật cuối

**⚠️ Action Required:**
- Cập nhật data models/types trong code
- Các fields mới là optional, không bắt buộc phải gửi

### 3. Status values mới

#### v1 Status:
- `pending`
- `completed`
- `failed`

#### v2 Status (thêm 2 giá trị):
- `pending`
- `processing` ⭐ NEW
- `completed`
- `failed`
- `cancelled` ⭐ NEW

**⚠️ Action Required:**
- Cập nhật enum/constants cho status
- Xử lý 2 status mới trong logic

## 📝 Endpoint Mapping

| v1 Endpoint | v2 Endpoint | Changes |
|-------------|-------------|---------|
| `POST /api/v1/payments` | `POST /api/v2/payments` | Request có thêm optional fields: `customer`, `metadata`, `webhook_url` |
| `GET /api/v1/payments/{id}` | `GET /api/v2/payments/{id}` | Response có thêm fields mới |
| `GET /api/v1/payments` | `GET /api/v2/payments` | Response format thay đổi, có pagination |
| ❌ N/A | `PATCH /api/v2/payments/{id}` | ⭐ NEW: Cập nhật status |
| ❌ N/A | `DELETE /api/v2/payments/{id}` | ⭐ NEW: Hủy payment |
| ❌ N/A | `POST /api/v2/webhooks` | ⭐ NEW: Đăng ký webhook |

## 🔧 Migration Steps

### Step 1: Cập nhật Base URL
```diff
- const BASE_URL = "http://localhost:8000/api/v1"
+ const BASE_URL = "http://localhost:8000/api/v2"
```

### Step 2: Cập nhật Request Models

#### Tạo Payment - v1
```javascript
const payment = {
  amount: 100000,
  currency: "VND",
  description: "Order #123"
}
```

#### Tạo Payment - v2 (backward compatible)
```javascript
// Minimal - vẫn hoạt động như v1
const payment = {
  amount: 100000,
  currency: "VND",
  description: "Order #123"
}

// Enhanced - tận dụng tính năng mới
const payment = {
  amount: 100000,
  currency: "VND",
  description: "Order #123",
  customer: {
    name: "Nguyen Van A",
    email: "nguyenvana@example.com",
    phone: "0901234567"
  },
  metadata: {
    order_id: "ORD-123",
    product: "Laptop"
  },
  webhook_url: "https://myapp.com/webhook"
}
```

### Step 3: Cập nhật Response Handling

#### List Payments - v1
```javascript
const response = await fetch('/api/v1/payments')
const data = await response.json()
const payments = data.payments // Array
```

#### List Payments - v2
```javascript
const response = await fetch('/api/v2/payments?limit=10&offset=0')
const data = await response.json()
const payments = data.data // Array
const pagination = data.pagination // Pagination info
```

### Step 4: Cập nhật Data Models/Types

#### TypeScript Example

```typescript
// v1 Types
interface PaymentV1 {
  id: number
  amount: number
  currency: string
  description?: string
  status: 'pending' | 'completed' | 'failed'
  created_at: string
}

// v2 Types
interface CustomerInfo {
  name?: string
  email?: string
  phone?: string
}

interface PaymentV2 {
  id: number
  amount: number
  currency: string
  description?: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  customer?: CustomerInfo
  metadata?: Record<string, any>
  webhook_url?: string
  created_at: string
  updated_at: string
}

interface PaginationInfo {
  total: number
  limit: number
  offset: number
  has_more: boolean
}

interface PaymentListResponse {
  data: PaymentV2[]
  pagination: PaginationInfo
}
```

### Step 5: Implement Pagination

```javascript
// v2 - Pagination example
async function getAllPayments() {
  let allPayments = []
  let offset = 0
  const limit = 50
  
  while (true) {
    const response = await fetch(
      `/api/v2/payments?limit=${limit}&offset=${offset}`
    )
    const data = await response.json()
    
    allPayments = allPayments.concat(data.data)
    
    if (!data.pagination.has_more) {
      break
    }
    
    offset += limit
  }
  
  return allPayments
}
```

### Step 6: Sử dụng tính năng mới (Optional)

#### Cập nhật trạng thái
```javascript
// v2 only
await fetch(`/api/v2/payments/${paymentId}`, {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ status: 'completed' })
})
```

#### Hủy thanh toán
```javascript
// v2 only
await fetch(`/api/v2/payments/${paymentId}`, {
  method: 'DELETE'
})
```

#### Đăng ký webhook
```javascript
// v2 only
await fetch('/api/v2/webhooks', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://myapp.com/webhook',
    events: ['payment.completed', 'payment.failed']
  })
})
```

## ✅ Migration Checklist

### Phase 1: Preparation (Week 1-2)
- [ ] Đọc và hiểu migration guide
- [ ] Review breaking changes
- [ ] Cập nhật data models/types trong codebase
- [ ] Setup môi trường test với v2

### Phase 2: Code Changes (Week 3-4)
- [ ] Cập nhật base URL từ v1 → v2
- [ ] Sửa response handling cho list endpoint
- [ ] Thêm xử lý cho fields mới (customer, metadata, updated_at)
- [ ] Cập nhật status enum với 2 giá trị mới
- [ ] Implement pagination logic
- [ ] (Optional) Tích hợp tính năng mới: webhooks, status updates

### Phase 3: Testing (Week 5)
- [ ] Test tất cả endpoints với v2
- [ ] Verify backward compatibility (minimal requests)
- [ ] Test pagination với datasets lớn
- [ ] Test error handling
- [ ] Load testing

### Phase 4: Deployment (Week 6)
- [ ] Deploy code mới lên staging
- [ ] Smoke test trên staging
- [ ] Deploy lên production
- [ ] Monitor logs và errors
- [ ] Verify không còn calls đến v1

### Phase 5: Cleanup (Week 7)
- [ ] Remove v1 related code
- [ ] Update documentation
- [ ] Thông báo hoàn thành migration

## 🧪 Testing

### Test với curl

#### v1 → v2 Comparison

```bash
# v1
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000, "currency": "VND"}'

# v2 (backward compatible)
curl -X POST "http://localhost:8000/api/v2/payments" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000, "currency": "VND"}'

# v2 (with new features)
curl -X POST "http://localhost:8000/api/v2/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100000,
    "currency": "VND",
    "customer": {"name": "Test User", "email": "test@example.com"},
    "metadata": {"order_id": "123"}
  }'
```

## 📞 Support

Nếu gặp vấn đề trong quá trình migration:

1. **Documentation**: Xem OpenAPI specs
   - v1: `/openapi_v1.yaml`
   - v2: `/openapi_v2.yaml`

2. **Interactive Docs**: 
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Contact**: support@example.com

## 📊 Timeline

```
Now                    01/06/2026
 |                          |
 |-- Migration Period ------|
 |                          |
 ✅ v1 Deprecated        ❌ v1 Sunset
 ✅ v2 Available         ✅ v2 Only
```

**Khuyến nghị**: Hoàn thành migration trong vòng 2-3 tháng để có thời gian xử lý issues.

## 🎯 Best Practices

1. **Migrate từng phần**: Không cần migrate toàn bộ cùng lúc
2. **Test kỹ**: Đặc biệt chú ý list endpoint và pagination
3. **Monitor**: Theo dõi logs sau khi deploy
4. **Backward compatible**: v2 hỗ trợ minimal requests giống v1
5. **Tận dụng tính năng mới**: Webhooks và metadata rất hữu ích

## 📚 Additional Resources

- [OpenAPI v1 Spec](./openapi_v1.yaml)
- [OpenAPI v2 Spec](./openapi_v2.yaml)
- [README](./README.md)
- [API Documentation](http://localhost:8000/docs)

---

**Last Updated**: 2025-11-19  
**Version**: 1.0
