"""
Rate limiter middleware - Giới hạn số request từ mỗi IP
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, List
import time
from logger import logger

class RateLimiter:
    def __init__(self, requests: int = 5, window: int = 60):
        """
        Args:
            requests: Số request tối đa
            window: Thời gian cửa sổ tính bằng giây (mặc định 60 giây = 1 phút)
        """
        self.requests = requests
        self.window = window
        # Lưu trữ: {ip: [timestamp1, timestamp2, ...]}
        self.request_records: Dict[str, List[float]] = {}
    
    def _clean_old_records(self, ip: str, current_time: float):
        """Xóa các record cũ ngoài cửa sổ thời gian"""
        if ip in self.request_records:
            cutoff_time = current_time - self.window
            self.request_records[ip] = [
                timestamp for timestamp in self.request_records[ip]
                if timestamp > cutoff_time
            ]
    
    def is_allowed(self, ip: str) -> tuple[bool, dict]:
        """
        Kiểm tra xem IP có được phép request không
        Returns: (allowed, info_dict)
        """
        current_time = time.time()
        
        # Xóa các record cũ
        self._clean_old_records(ip, current_time)
        
        # Khởi tạo nếu chưa có
        if ip not in self.request_records:
            self.request_records[ip] = []
        
        # Đếm số request trong cửa sổ thời gian
        request_count = len(self.request_records[ip])
        
        if request_count >= self.requests:
            # Tính thời gian reset
            oldest_request = self.request_records[ip][0]
            reset_time = oldest_request + self.window
            retry_after = int(reset_time - current_time)
            
            # Log rate limit violation
            logger.warning(f"Rate limit exceeded for IP: {ip} | Requests: {request_count}/{self.requests}")
            
            return False, {
                "allowed": False,
                "limit": self.requests,
                "remaining": 0,
                "reset_in_seconds": retry_after,
                "message": f"Vượt quá giới hạn {self.requests} requests/{self.window}s. Vui lòng thử lại sau {retry_after} giây."
            }
        
        # Cho phép request
        self.request_records[ip].append(current_time)
        remaining = self.requests - request_count - 1
        
        return True, {
            "allowed": True,
            "limit": self.requests,
            "remaining": remaining,
            "reset_in_seconds": self.window
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Lấy IP của client"""
        # Kiểm tra X-Forwarded-For header (nếu đằng sau proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Kiểm tra X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Lấy từ client
        if request.client:
            return request.client.host
        
        return "unknown"

# Tạo instance global
rate_limiter = RateLimiter(requests=5, window=60)

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware để kiểm tra rate limit cho mọi request
    """
    # Bỏ qua rate limit cho documentation endpoints
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        response = await call_next(request)
        return response
    
    # Lấy IP
    client_ip = rate_limiter.get_client_ip(request)
    
    # Kiểm tra rate limit
    allowed, info = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        logger.bind(access=True).warning(
            f"🚫 Rate limit blocked | {request.method} {request.url.path} | IP: {client_ip} | Retry after: {info['reset_in_seconds']}s"
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": info["message"],
                "limit": info["limit"],
                "retry_after": info["reset_in_seconds"]
            },
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info["reset_in_seconds"]),
                "Retry-After": str(info["reset_in_seconds"])
            }
        )
    
    # Cho phép request và thêm headers
    response = await call_next(request)
    
    # Thêm rate limit info vào response headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset_in_seconds"])
    
    return response

