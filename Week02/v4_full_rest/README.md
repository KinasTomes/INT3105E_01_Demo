# V4: Full REST Architecture (All 6 Constraints)

## Tất cả 6 nguyên tắc REST:

### 1. **Client-Server**
- Tách biệt client và server responsibilities

### 2. **Stateless** 
- Không lưu session state trên server
- Mọi thông tin cần thiết trong request

### 3. **Cacheable**
- ETags cho conditional requests
- Cache-Control và Expires headers
- 304 Not Modified responses

### 4. **Uniform Interface**
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Consistent resource URIs (/api/books)
- Proper HTTP status codes
- **HATEOAS**: Hypermedia links trong responses

### 5. **Layered System**
- Middleware cho logging
- Cross-cutting concerns (headers, monitoring)
- Health check endpoint
- Request/Response interception

### 6. **Code-on-Demand** (Optional)
- Dynamic client scripts delivered from server
- Interactive web interface
- Client functionality từ server

## Tính năng đặc biệt:

**HATEOAS (Hypermedia):**
```json
{
  "id": 1,
  "title": "Book Title",
  "_links": {
    "self": "/api/books/1",
    "collection": "/api/books",
    "update": "/api/books/1",
    "delete": "/api/books/1"
  }
}
```

**Pagination với Navigation:**
```json
{
  "books": [...],
  "pagination": {...},
  "_links": {
    "self": "/api/books?page=2",
    "first": "/api/books?page=1", 
    "prev": "/api/books?page=1",
    "next": "/api/books?page=3",
    "last": "/api/books?page=5"
  }
}
```

**Chạy:**
```bash
python app.py
```

**Test Full REST:**
```bash
# HATEOAS discovery
curl "http://localhost:5003/api/books/1"

# Pagination with links  
curl "http://localhost:5003/api/books?page=1&per_page=2"

# Caching with ETags
curl -i "http://localhost:5003/api/books"

# Health check (layered system)
curl "http://localhost:5003/health"

# Interactive client (code-on-demand)
# Open: http://localhost:5003/
```