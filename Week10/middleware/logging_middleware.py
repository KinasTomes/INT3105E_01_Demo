"""
Logging middleware để log mọi request/response
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from logger import logger
from metrics import metrics_collector
import prometheus_metrics
import time
import json

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lấy thông tin request
        start_time = time.time()
        
        # Lấy client IP
        client_ip = self._get_client_ip(request)
        
        # Log request
        logger.bind(access=True).info(
            f"→ {request.method} {request.url.path} | IP: {client_ip} | User-Agent: {request.headers.get('user-agent', 'N/A')}"
        )
        
        # Log request body cho POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Đọc body nhưng không consume stream
                body = await self._get_body(request)
                if body:
                    logger.debug(f"Request body: {body[:500]}")  # Chỉ log 500 ký tự đầu
            except Exception as e:
                logger.warning(f"Could not read request body: {e}")
        
        # Process request
        try:
            # Track request in progress for Prometheus
            with prometheus_metrics.PrometheusInProgressTracker(request.method, request.url.path):
                response = await call_next(request)
            
            # Tính thời gian xử lý
            process_time = time.time() - start_time
            
            # Record metrics (bỏ qua monitoring endpoints và static files)
            if request.url.path not in ["/metrics", "/prometheus", "/health", "/dashboard"] and not request.url.path.startswith("/static"):
                # Custom metrics
                metrics_collector.record_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    response_time=process_time
                )
                
                # Prometheus metrics
                prometheus_metrics.record_request(
                    method=request.method,
                    endpoint=request.url.path,
                    status_code=response.status_code,
                    duration=process_time
                )
            
            # Log response
            status_emoji = "✓" if response.status_code < 400 else "✗"
            log_level = "info" if response.status_code < 400 else "warning" if response.status_code < 500 else "error"
            
            getattr(logger.bind(access=True), log_level)(
                f"{status_emoji} {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.3f}s | IP: {client_ip}"
            )
            
            # Thêm header với thời gian xử lý
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.bind(access=True).error(
                f"✗ {request.method} {request.url.path} | Error: {str(e)} | Time: {process_time:.3f}s | IP: {client_ip}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Lấy IP của client"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _get_body(self, request: Request) -> str:
        """Lấy request body"""
        try:
            body = await request.body()
            return body.decode('utf-8') if body else ""
        except:
            return ""

