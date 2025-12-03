from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import books
from rate_limiter import rate_limit_middleware
from middleware.logging_middleware import LoggingMiddleware
from logger import logger
from metrics import metrics_collector
import data_store

app = FastAPI(
    title="Books Management API",
    description="API đơn giản để quản lý sách (CRUD operations with in-memory storage)",
    version="1.0.0"
)

# Log startup
logger.info("🚀 Starting Books Management API...")
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

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Chào mừng đến với Books Management API",
        "docs": "/docs",
        "version": "1.0.0",
        "features": ["CRUD operations for books", "Rate limiting", "Logging"],
        "note": "Dữ liệu được lưu trong bộ nhớ (in-memory), sẽ mất khi restart server",
        "rate_limit": "5 requests/phút cho mỗi IP"
    }

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/metrics")
def get_metrics():
    """Lấy metrics và thống kê hệ thống"""
    logger.info("Metrics endpoint accessed")
    metrics = metrics_collector.get_metrics()
    
    # Thêm thông tin về data storage
    metrics["storage"] = {
        "total_books": len(data_store.books),
        "books_available": sum(1 for book in data_store.books if book["available"] > 0),
        "total_copies": sum(book["quantity"] for book in data_store.books),
        "available_copies": sum(book["available"] for book in data_store.books)
    }
    
    return metrics

@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Shutting down Books Management API...")
