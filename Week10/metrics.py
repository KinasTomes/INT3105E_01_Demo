"""
Metrics tracking for the API
"""

import time
from typing import Dict, List
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.requests_by_endpoint: Dict[str, int] = {}
        self.requests_by_method: Dict[str, int] = {}
        self.requests_by_status: Dict[int, int] = {}
        self.response_times: List[float] = []
        self.rate_limit_violations = 0
        self.errors_count = 0
    
    def record_request(self, method: str, path: str, status_code: int, response_time: float):
        """Ghi lại thông tin request"""
        self.request_count += 1
        
        # Đếm theo endpoint
        endpoint_key = f"{method} {path}"
        self.requests_by_endpoint[endpoint_key] = self.requests_by_endpoint.get(endpoint_key, 0) + 1
        
        # Đếm theo method
        self.requests_by_method[method] = self.requests_by_method.get(method, 0) + 1
        
        # Đếm theo status code
        self.requests_by_status[status_code] = self.requests_by_status.get(status_code, 0) + 1
        
        # Lưu response time
        self.response_times.append(response_time)
        
        # Đếm errors
        if status_code >= 400:
            self.errors_count += 1
        
        # Đếm rate limit violations
        if status_code == 429:
            self.rate_limit_violations += 1
    
    def get_metrics(self) -> dict:
        """Lấy tất cả metrics"""
        uptime = time.time() - self.start_time
        
        # Tính average response time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        # Tính min/max response time
        min_response_time = min(self.response_times) if self.response_times else 0
        max_response_time = max(self.response_times) if self.response_times else 0
        
        # Lấy top 5 endpoints được gọi nhiều nhất
        top_endpoints = sorted(
            self.requests_by_endpoint.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "server": {
                "uptime_seconds": round(uptime, 2),
                "uptime_human": self._format_uptime(uptime),
                "start_time": datetime.fromtimestamp(self.start_time).isoformat()
            },
            "requests": {
                "total": self.request_count,
                "by_method": self.requests_by_method,
                "by_status": self.requests_by_status,
                "top_endpoints": [{"endpoint": k, "count": v} for k, v in top_endpoints]
            },
            "performance": {
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "min_response_time_ms": round(min_response_time * 1000, 2),
                "max_response_time_ms": round(max_response_time * 1000, 2),
                "total_requests_tracked": len(self.response_times)
            },
            "errors": {
                "total_errors": self.errors_count,
                "rate_limit_violations": self.rate_limit_violations,
                "error_rate_percent": round((self.errors_count / self.request_count * 100) if self.request_count > 0 else 0, 2)
            },
            "rate_limiting": {
                "limit": "5 requests/minute per IP",
                "violations": self.rate_limit_violations
            }
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime thành dạng dễ đọc"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def reset_metrics(self):
        """Reset tất cả metrics"""
        self.__init__()

# Global metrics collector
metrics_collector = MetricsCollector()

