"""
API v2 Routes - Enhanced payment endpoints
(Placeholder for future enhancements)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def v2_info():
    """API v2 info endpoint"""
    return {
        "version": "2.0",
        "message": "API v2 - Coming soon with enhanced features"
    }
