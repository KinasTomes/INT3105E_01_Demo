from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import books, users, borrows

app = FastAPI(
    title="Library Management API",
    description="API đơn giản để quản lý thư viện (sử dụng in-memory storage)",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router)
app.include_router(users.router)
app.include_router(borrows.router)

@app.get("/")
def read_root():
    return {
        "message": "Chào mừng đến với Library Management API",
        "docs": "/docs",
        "version": "1.0.0",
        "note": "Dữ liệu được lưu trong bộ nhớ (in-memory), sẽ mất khi restart server"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
