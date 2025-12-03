from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import books, users, borrows
from rate_limiter import rate_limit_middleware
from middleware.logging_middleware import LoggingMiddleware
from logger import logger

app = FastAPI(
    title="Library Management API",
    description="API đơn giản để quản lý thư viện (sử dụng in-memory storage)",
    version="1.0.0"
)

# Log startup
logger.info("🚀 Starting Library Management API...")
logger.info("📚 In-memory storage initialized")
logger.info("🔒 Rate limiting: 5 requests/minute per IP")

# Cấu hình Logging Middleware
app.add_middleware(LoggingMiddleware)

# Cấu hình Rate Limiting
app.middleware("http")(rate_limit_middleware)

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
    logger.info("Root endpoint accessed")
    return {
        "message": "Chào mừng đến với Library Management API",
        "docs": "/docs",
        "version": "1.0.0",
        "note": "Dữ liệu được lưu trong bộ nhớ (in-memory), sẽ mất khi restart server",
        "rate_limit": "5 requests/phút cho mỗi IP",
        "logging": "Enabled with Loguru"
    }

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}

@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Shutting down Library Management API...")
