"""
Logging configuration using Loguru
"""

import sys
from loguru import logger
from pathlib import Path

# Tạo thư mục logs nếu chưa có
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Xóa default handler
logger.remove()

# Console handler - hiển thị màu đẹp trong terminal
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# File handler - logs tổng hợp
logger.add(
    "logs/app.log",
    rotation="10 MB",  # Rotate khi file đạt 10MB
    retention="7 days",  # Giữ logs trong 7 ngày
    compression="zip",  # Nén logs cũ
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# File handler riêng cho errors
logger.add(
    "logs/errors.log",
    rotation="10 MB",
    retention="30 days",  # Giữ error logs lâu hơn
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR"
)

# File handler cho access logs (request/response)
logger.add(
    "logs/access.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    level="INFO",
    filter=lambda record: "access" in record["extra"]
)

# Export logger
__all__ = ["logger"]

