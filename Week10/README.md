# Library Management API

API đơn giản để quản lý thư viện được xây dựng bằng FastAPI với **in-memory storage** (lưu trữ bằng mảng).

## Tính năng

- **Quản lý sách**: Thêm, sửa, xóa, và xem danh sách sách
- **Quản lý người dùng**: Thêm, sửa, xóa, và xem danh sách người dùng
- **Quản lý mượn/trả sách**: Mượn sách, trả sách, và xem lịch sử mượn
- **Dữ liệu mẫu**: Hệ thống tự động khởi tạo một số dữ liệu mẫu khi chạy
- **Rate Limiting**: Giới hạn 5 requests/phút cho mỗi IP address

## Đặc điểm

✅ **Đơn giản**: Không cần cài đặt database, không cần cấu hình phức tạp  
✅ **Nhanh**: Sử dụng in-memory storage, truy xuất dữ liệu cực nhanh  
✅ **Bảo vệ**: Rate limiting tự động chống spam và abuse  
⚠️ **Lưu ý**: Dữ liệu sẽ mất khi restart server (chỉ phù hợp cho demo/development)

## Cài đặt

### Yêu cầu

- Python 3.8+
- pip

### Các bước cài đặt

1. Clone repository hoặc tạo thư mục project

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Chạy server:
```bash
uvicorn main:app --reload
```

Server sẽ chạy tại: `http://127.0.0.1:8000`

## Sử dụng

### Truy cập API Documentation

Sau khi chạy server, bạn có thể truy cập:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Dữ liệu mẫu

Khi khởi động, hệ thống tự động tạo sẵn:
- 2 cuốn sách mẫu
- 2 người dùng mẫu

Bạn có thể test ngay các API mà không cần thêm dữ liệu!

### API Endpoints

#### Books (Sách)

- `POST /books/` - Tạo sách mới
- `GET /books/` - Lấy danh sách tất cả sách
- `GET /books/{book_id}` - Lấy thông tin chi tiết một cuốn sách
- `PUT /books/{book_id}` - Cập nhật thông tin sách
- `DELETE /books/{book_id}` - Xóa sách

#### Users (Người dùng)

- `POST /users/` - Tạo người dùng mới
- `GET /users/` - Lấy danh sách tất cả người dùng
- `GET /users/{user_id}` - Lấy thông tin chi tiết một người dùng
- `PUT /users/{user_id}` - Cập nhật thông tin người dùng
- `DELETE /users/{user_id}` - Xóa người dùng
- `GET /users/{user_id}/borrows` - Xem lịch sử mượn sách của người dùng

#### Borrows (Mượn/Trả sách)

- `POST /borrows/` - Mượn sách
- `PUT /borrows/{borrow_id}/return` - Trả sách
- `GET /borrows/` - Lấy danh sách tất cả bản ghi mượn sách
- `GET /borrows/active` - Lấy danh sách các sách đang được mượn
- `GET /borrows/{borrow_id}` - Lấy thông tin chi tiết một bản ghi mượn

## Rate Limiting

API có rate limiting tự động:
- **Giới hạn**: 5 requests/phút cho mỗi IP
- **Response headers**: Mỗi response có chứa thông tin rate limit
  - `X-RateLimit-Limit`: Số request tối đa
  - `X-RateLimit-Remaining`: Số request còn lại
  - `X-RateLimit-Reset`: Thời gian reset (giây)

Khi vượt quá giới hạn:
- **Status code**: 429 Too Many Requests
- **Response**: Thông báo lỗi với thời gian cần chờ
- **Header**: `Retry-After` cho biết số giây cần đợi

**Lưu ý**: Các endpoint `/docs`, `/redoc`, `/openapi.json`, `/health` không bị giới hạn.

## Ví dụ sử dụng

### Xem danh sách sách (có sẵn dữ liệu mẫu)

```bash
curl http://127.0.0.1:8000/books/
```

### Tạo sách mới

```bash
curl -X POST "http://127.0.0.1:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design Patterns",
    "author": "Gang of Four",
    "isbn": "978-0201633610",
    "published_year": 1994,
    "quantity": 3
  }'
```

### Tạo người dùng mới

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lê Văn C",
    "email": "levanc@example.com",
    "phone": "0912345678"
  }'
```

### Mượn sách (sử dụng ID từ dữ liệu mẫu)

```bash
curl -X POST "http://127.0.0.1:8000/borrows/" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "user_id": 1
  }'
```

### Trả sách

```bash
curl -X PUT "http://127.0.0.1:8000/borrows/1/return"
```

## Cấu trúc dữ liệu

### Book (Sách)
- `id`: ID sách (tự động tăng)
- `title`: Tên sách
- `author`: Tác giả
- `isbn`: Mã ISBN
- `published_year`: Năm xuất bản
- `quantity`: Tổng số lượng
- `available`: Số lượng còn sẵn để mượn

### User (Người dùng)
- `id`: ID người dùng (tự động tăng)
- `name`: Tên người dùng
- `email`: Email
- `phone`: Số điện thoại
- `is_active`: Trạng thái hoạt động

### BorrowRecord (Bản ghi mượn sách)
- `id`: ID bản ghi (tự động tăng)
- `book_id`: ID sách được mượn
- `user_id`: ID người mượn
- `borrow_date`: Ngày mượn
- `return_date`: Ngày trả (null nếu chưa trả)
- `is_returned`: Trạng thái đã trả hay chưa

## Cấu trúc Project

```
Week10/
├── routers/
│   ├── __init__.py
│   ├── books.py          # API routes cho quản lý sách
│   ├── users.py          # API routes cho quản lý người dùng
│   └── borrows.py        # API routes cho mượn/trả sách
├── main.py               # File chính của ứng dụng
├── data_store.py         # In-memory data storage (mảng)
├── schemas.py            # Pydantic schemas cho validation
├── crud.py               # CRUD operations
├── rate_limiter.py       # Rate limiting middleware
├── requirements.txt      # Dependencies
└── README.md            # Tài liệu hướng dẫn
```

## Công nghệ sử dụng

- **FastAPI**: Web framework hiện đại, nhanh
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Python Lists**: In-memory data storage (không cần database)

## Ưu điểm của phương pháp này

✅ Không cần cài đặt và cấu hình database  
✅ Code đơn giản, dễ hiểu  
✅ Chạy nhanh, phù hợp cho demo và học tập  
✅ Không phụ thuộc vào thư viện database  
✅ Có rate limiting bảo vệ khỏi spam/abuse  

## Hạn chế

⚠️ Dữ liệu mất khi restart server  
⚠️ Không phù hợp cho production  
⚠️ Không hỗ trợ concurrent access an toàn  
⚠️ Rate limit dựa trên IP (có thể bị bypass bằng proxy)  

## Nâng cấp trong tương lai

Nếu muốn chuyển sang production, bạn có thể:
- Thêm SQLite hoặc PostgreSQL database
- Thêm authentication/authorization
- Thêm logging và monitoring
- Thêm unit tests

## License

MIT License
