# Library Management API

API đơn giản để quản lý thư viện được xây dựng bằng FastAPI với **in-memory storage** (lưu trữ bằng mảng).

## Tính năng

- **Quản lý sách**: Thêm, sửa, xóa, và xem danh sách sách
- **Quản lý người dùng**: Thêm, sửa, xóa, và xem danh sách người dùng
- **Quản lý mượn/trả sách**: Mượn sách, trả sách, và xem lịch sử mượn
- **Dữ liệu mẫu**: Hệ thống tự động khởi tạo một số dữ liệu mẫu khi chạy
- **Rate Limiting**: Giới hạn 5 requests/phút cho mỗi IP address
- **Logging**: Ghi log tất cả requests, responses, và operations với Loguru

## Đặc điểm

✅ **Đơn giản**: Không cần cài đặt database, không cần cấu hình phức tạp  
✅ **Nhanh**: Sử dụng in-memory storage, truy xuất dữ liệu cực nhanh  
✅ **Bảo vệ**: Rate limiting tự động chống spam và abuse  
✅ **Monitoring**: Logging đầy đủ với rotation và compression  
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

**Cách 1 (Khuyến nghị)**: Sử dụng script start.py (chỉ reload khi file .py thay đổi):
```bash
python start.py
```

**Cách 2**: Trực tiếp với uvicorn (chỉ watch thư mục cụ thể):
```bash
uvicorn main:app --reload --reload-dir=. --reload-dir=routers --reload-dir=middleware
```

**Cách 3**: Reload tất cả files (không khuyến nghị vì sẽ reload cả logs):
```bash
uvicorn main:app --reload
```

**Lưu ý**: Uvicorn chỉ hỗ trợ `--reload-dir` để chỉ định thư mục watch, không có cách filter theo extension file.

Server sẽ chạy tại: `http://127.0.0.1:8000`

**Lưu ý**: 
- **Cách 1** watch các thư mục code (`routers`, `middleware`, root) nhưng không watch thư mục `logs`
- Server vẫn có thể reload khi file `.py` trong root thay đổi, nhưng không reload khi logs được ghi
- Nếu vẫn bị reload do logs, hãy di chuyển các file `.py` vào thư mục con riêng

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

## Logging

Hệ thống sử dụng **Loguru** (tương đương Winston của Node.js) để ghi log:

### Log Files

Tất cả logs được lưu trong thư mục `logs/`:

- **`logs/app.log`**: Logs tổng hợp (INFO, DEBUG, WARNING, ERROR)
  - Rotation: 10 MB
  - Retention: 7 ngày
  - Compression: ZIP

- **`logs/errors.log`**: Chỉ ghi errors (ERROR)
  - Rotation: 10 MB
  - Retention: 30 ngày
  - Compression: ZIP

- **`logs/access.log`**: Access logs (requests/responses)
  - Rotation: 10 MB
  - Retention: 7 ngày
  - Compression: ZIP

### Log Format

**Console output** (có màu):
```
2024-12-03 10:15:30 | INFO     | main:read_root:35 - Root endpoint accessed
→ GET / | IP: 127.0.0.1 | User-Agent: Mozilla/5.0
✓ GET / | Status: 200 | Time: 0.002s | IP: 127.0.0.1
```

**File output**:
```
2024-12-03 10:15:30 | INFO     | main:read_root:35 - Root endpoint accessed
```

### Log Levels

- **DEBUG**: Thông tin chi tiết cho debugging
- **INFO**: Thông tin chung về operations (create, update, delete)
- **WARNING**: Rate limit violations, validation issues
- **ERROR**: Lỗi xử lý request

### Các sự kiện được log

✅ Mọi HTTP request/response với status code và thời gian xử lý  
✅ Tạo/xóa sách, người dùng  
✅ Mượn/trả sách  
✅ Rate limit violations  
✅ Server startup/shutdown  
✅ Errors và exceptions  

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
├── middleware/
│   ├── __init__.py
│   └── logging_middleware.py  # Logging middleware
├── logs/                 # Thư mục chứa log files (auto-created)
│   ├── app.log          # Logs tổng hợp
│   ├── errors.log       # Error logs
│   └── access.log       # Access logs
├── main.py               # File chính của ứng dụng
├── start.py              # Script khởi động (reload chỉ .py files)
├── data_store.py         # In-memory data storage (mảng)
├── schemas.py            # Pydantic schemas cho validation
├── crud.py               # CRUD operations
├── rate_limiter.py       # Rate limiting middleware
├── logger.py             # Logging configuration
├── requirements.txt      # Dependencies
├── .gitignore           # Git ignore (bao gồm logs/)
└── README.md            # Tài liệu hướng dẫn
```

## Công nghệ sử dụng

- **FastAPI**: Web framework hiện đại, nhanh
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Loguru**: Logging library (tương đương Winston của Node.js)
- **Python Lists**: In-memory data storage (không cần database)

## Ưu điểm của phương pháp này

✅ Không cần cài đặt và cấu hình database  
✅ Code đơn giản, dễ hiểu  
✅ Chạy nhanh, phù hợp cho demo và học tập  
✅ Không phụ thuộc vào thư viện database  
✅ Có rate limiting bảo vệ khỏi spam/abuse  
✅ Logging đầy đủ giúp debug và monitor  

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
