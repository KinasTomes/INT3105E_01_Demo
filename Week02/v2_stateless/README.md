# V2: Client-Server + Stateless

## Nguyên tắc:
1. **Client-Server**: Tách biệt client và server
2. **Stateless**: Server không lưu trữ session state

**Đặc điểm Stateless:**
- Mỗi request chứa tất cả thông tin cần thiết
- Server không lưu context giữa các requests
- Tất cả filtering parameters đến từ query string
- Complete resource state trong PUT requests

**Chạy:**
```bash
python app.py
```

**Test Stateless:**
```bash
# Filter by author (state in URL)
curl "http://localhost:5001/books?author=John"

# Filter by availability
curl "http://localhost:5001/books?available=true"

# Complete update (all state in request)
curl -X PUT "http://localhost:5001/books/1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "author": "John Doe", "available": false}'
```