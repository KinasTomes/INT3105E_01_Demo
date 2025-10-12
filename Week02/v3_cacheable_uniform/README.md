# V3: Client-Server + Stateless + Cacheable + Uniform Interface

## Nguyên tắc:
1. **Client-Server**: Tách biệt client và server
2. **Stateless**: Không lưu session state
3. **Cacheable**: Hỗ trợ HTTP caching
4. **Uniform Interface**: URI và HTTP methods chuẩn

**Cacheable Features:**
- ETags cho conditional requests
- Cache-Control headers
- Last-Modified headers
- 304 Not Modified responses

**Uniform Interface:**
- Consistent `/api/books` URIs
- Standard HTTP status codes (200, 201, 204, 400, 404, 409)
- Location headers cho created resources
- Structured error responses

**Chạy:**
```bash
python app.py
```

**Test Caching:**
```bash
# First request - returns data with ETag
curl -i "http://localhost:5002/api/books"

# Second request with ETag - returns 304 Not Modified
curl -i "http://localhost:5002/api/books" \
  -H "If-None-Match: <etag-from-first-request>"

# Test optimistic concurrency control
curl -X PUT "http://localhost:5002/api/books/1" \
  -H "Content-Type: application/json" \
  -H "If-Match: <etag>" \
  -d '{"title": "Updated Title"}'
```