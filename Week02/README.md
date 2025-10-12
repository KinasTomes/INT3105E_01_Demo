# Week02 - REST Architecture

Thư mục này chứa 4 version demo từng bước các nguyên tắc REST Architecture:

## 📁 Cấu trúc

```
Week02/
├── v1_client_server/     # Client-Server
├── v2_stateless/        # + Stateless  
├── v3_cacheable_uniform/ # + Cacheable + Uniform Interface
├── v4_full_rest/        # + Layered System + Code-on-Demand
└── README.md            # File này
```

## 🚀 Evolution Timeline

### V1: Client-Server
**Port: 5000**
- ✅ Client-Server separation
- Basic HTTP endpoints
- Simple in-memory storage

### V2: + Stateless  
**Port: 5001**
- ✅ Client-Server
- ✅ Stateless (no server-side sessions)
- Complete request information
- Query parameters for filtering

### V3: + Cacheable + Uniform Interface
**Port: 5002** 
- ✅ Client-Server
- ✅ Stateless  
- ✅ Cacheable (ETags, Cache-Control)
- ✅ Uniform Interface (standard URIs, HTTP codes)
- Conditional requests (304 Not Modified)
- Optimistic concurrency control

### V4: + Layered System + Code-on-Demand
**Port: 5003**
- ✅ Client-Server
- ✅ Stateless
- ✅ Cacheable  
- ✅ Uniform Interface
- ✅ Layered System (middleware, monitoring)
- ✅ Code-on-Demand (dynamic client scripts)
- **HATEOAS** hypermedia links
- Pagination with navigation
- Health monitoring

## 🧪 Quick Test All Versions

```bash
# Terminal 1
cd v1_client_server && python app.py

# Terminal 2  
cd v2_stateless && python app.py

# Terminal 3
cd v3_cacheable_uniform && python app.py

# Terminal 4
cd v4_full_rest && python app.py
```

**Browsers:**
- V1: http://localhost:5000
- V2: http://localhost:5001  
- V3: http://localhost:5002
- V4: http://localhost:5003


Mỗi version tập trung vào:

1. **V1**: Hiểu Client-Server separation
2. **V2**: Stateless communication patterns  
3. **V3**: HTTP caching và standard interfaces
4. **V4**: Complete REST với hypermedia và layering