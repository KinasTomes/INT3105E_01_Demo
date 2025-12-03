"""
Prometheus metrics integration
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
import time

# Tạo registry riêng cho app
registry = CollectorRegistry()

# Server info
server_info = Info(
    'books_api_server',
    'Information about Books Management API server',
    registry=registry
)
server_info.info({
    'version': '1.0.0',
    'name': 'Books Management API'
})

# Server uptime
server_uptime = Gauge(
    'books_api_uptime_seconds',
    'Server uptime in seconds',
    registry=registry
)

# Request counter
http_requests_total = Counter(
    'books_api_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# Request duration histogram
http_request_duration_seconds = Histogram(
    'books_api_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=registry
)

# Request in progress
http_requests_in_progress = Gauge(
    'books_api_http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint'],
    registry=registry
)

# Rate limit violations
rate_limit_violations_total = Counter(
    'books_api_rate_limit_violations_total',
    'Total rate limit violations',
    ['endpoint'],
    registry=registry
)

# Books metrics
books_total = Gauge(
    'books_api_books_total',
    'Total number of books in the system',
    registry=registry
)

books_available = Gauge(
    'books_api_books_available',
    'Number of books currently available',
    registry=registry
)

total_copies = Gauge(
    'books_api_total_copies',
    'Total number of book copies',
    registry=registry
)

available_copies = Gauge(
    'books_api_available_copies',
    'Number of available book copies',
    registry=registry
)

# Error counter
http_errors_total = Counter(
    'books_api_http_errors_total',
    'Total HTTP errors',
    ['status'],
    registry=registry
)

# Start time
START_TIME = time.time()

def update_storage_metrics(data_store):
    """Update storage-related metrics"""
    books_total.set(len(data_store.books))
    books_available.set(sum(1 for book in data_store.books if book["available"] > 0))
    total_copies.set(sum(book["quantity"] for book in data_store.books))
    available_copies.set(sum(book["available"] for book in data_store.books))

def update_uptime():
    """Update server uptime"""
    server_uptime.set(time.time() - START_TIME)

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record metrics for a request"""
    # Sanitize endpoint (remove IDs)
    sanitized_endpoint = _sanitize_endpoint(endpoint)
    
    # Record request
    http_requests_total.labels(
        method=method,
        endpoint=sanitized_endpoint,
        status=str(status_code)
    ).inc()
    
    # Record duration
    http_request_duration_seconds.labels(
        method=method,
        endpoint=sanitized_endpoint
    ).observe(duration)
    
    # Record errors
    if status_code >= 400:
        http_errors_total.labels(status=str(status_code)).inc()
    
    # Record rate limit violations
    if status_code == 429:
        rate_limit_violations_total.labels(endpoint=sanitized_endpoint).inc()

def _sanitize_endpoint(endpoint: str) -> str:
    """
    Sanitize endpoint to group similar endpoints
    E.g., /books/1, /books/2 -> /books/{id}
    """
    parts = endpoint.split('/')
    sanitized_parts = []
    
    for part in parts:
        # Check if part is a number (ID)
        if part.isdigit():
            sanitized_parts.append('{id}')
        else:
            sanitized_parts.append(part)
    
    return '/'.join(sanitized_parts)

class PrometheusInProgressTracker:
    """Context manager to track requests in progress"""
    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = _sanitize_endpoint(endpoint)
    
    def __enter__(self):
        http_requests_in_progress.labels(
            method=self.method,
            endpoint=self.endpoint
        ).inc()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        http_requests_in_progress.labels(
            method=self.method,
            endpoint=self.endpoint
        ).dec()

def get_metrics() -> bytes:
    """Get metrics in Prometheus format"""
    update_uptime()
    return generate_latest(registry)

def get_content_type() -> str:
    """Get Prometheus content type"""
    return CONTENT_TYPE_LATEST

