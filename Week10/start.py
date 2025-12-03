"""
Script để chạy uvicorn với cấu hình tối ưu
"""

import uvicorn
from pathlib import Path

if __name__ == "__main__":
    # Lấy thư mục hiện tại
    current_dir = Path(__file__).parent
    
    # Chỉ watch các thư mục chứa code Python
    # Không watch thư mục logs để tránh reload khi ghi log
    reload_dirs = [
        str(current_dir / "routers"),
        str(current_dir / "middleware"),
        str(current_dir),  # Root directory cho các file .py ở root
    ]
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=reload_dirs,
        reload_delay=0.5,  # Delay 0.5s trước khi reload
        log_level="info"
    )

