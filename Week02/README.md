# Flask Library Management System

Hệ thống quản lý thư viện đơn giản được xây dựng bằng Flask với kiến trúc Blueprint.

## Cấu trúc dự án

```
Week02/
├── app/
│   ├── __init__.py          # Factory function tạo app
│   ├── models.py            # Database models
│   ├── blueprints/
│   │   ├── main/
│   │   │   ├── __init__.py
│   │   │   └── routes.py    # Dashboard và seed data
│   │   ├── books/
│   │   │   ├── __init__.py
│   │   │   └── routes.py    # CRUD operations cho sách
│   │   ├── members/
│   │   │   ├── __init__.py
│   │   │   └── routes.py    # CRUD operations cho thành viên
│   │   ├── loans/
│   │   │   ├── __init__.py
│   │   │   └── routes.py    # Quản lý mượn/trả sách
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py    # JSON API endpoints
│   └── templates/
│       ├── base.html        # Template cơ sở
│       ├── dashboard.html   # Trang chủ
│       ├── books/
│       │   ├── list.html
│       │   ├── new.html
│       │   └── edit.html
│       ├── members/
│       │   ├── list.html
│       │   ├── new.html
│       │   └── edit.html
│       └── loans/
│           ├── list.html
│           └── borrow.html
├── run.py                   # Entry point
├── requirements.txt         # Dependencies
└── README.md               # Tài liệu này
```

## Tính năng

- **Quản lý sách**: Thêm, sửa, xóa, tìm kiếm sách
- **Quản lý thành viên**: Thêm, sửa, xóa thành viên
- **Quản lý mượn/trả**: Tạo phiếu mượn, trả sách, theo dõi hạn trả
- **Giao diện web**: Sử dụng Bootstrap cho UI responsive
- **API JSON**: Các endpoint để tích hợp với hệ thống khác
- **Cơ sở dữ liệu**: SQLite tự động tạo

## Cài đặt và chạy

1. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Chạy ứng dụng:
   ```bash
   python run.py
   ```

3. Truy cập: `http://127.0.0.1:5000`

## API Endpoints

### Books
- `GET /api/books` - Lấy danh sách sách
- `POST /api/books` - Tạo sách mới

### Borrows
- `POST /api/borrow` - Tạo phiếu mượn
- `POST /api/return/<id>` - Trả sách

## Kiến trúc Blueprint

Ứng dụng sử dụng Flask Blueprints để tổ chức code thành các module riêng biệt:

- `main`: Dashboard và các chức năng chung
- `books`: Quản lý sách
- `members`: Quản lý thành viên
- `loans`: Quản lý phiếu mượn/trả
- `api`: API endpoints

Mỗi blueprint có cấu trúc riêng với routes và templates tương ứng.

## Database Models

- **Book**: Thông tin sách (title, author, year, total_copies, available_copies)
- **Member**: Thông tin thành viên (name, email)
- **Loan**: Phiếu mượn (book_id, member_id, borrowed_at, due_date, returned_at)

## Templates

Sử dụng Jinja2 templates với base template và kế thừa. Giao diện sử dụng Bootstrap 5 CDN.