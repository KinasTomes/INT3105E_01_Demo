"""
Payment API Demo - Main Application
Supports multiple API versions (v1, v2) with separate documentation
"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api.v1 import routes as v1_routes
from api.v2 import routes as v2_routes

# Main app (combined docs)
app = FastAPI(
    title="Payment API Demo",
    description="Demo API thanh toán với versioning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Separate FastAPI apps for each version
app_v1 = FastAPI(
    title="Payment API v1 (DEPRECATED)",
    description="""
    ⚠️ **DEPRECATED**: This API version is deprecated and will be sunset on **01/06/2026**.
    
    Please migrate to API v2 for enhanced features and continued support.
    
    **Migration Guide**: See `/docs/MIGRATION_GUIDE.md`
    
    **Successor Version**: [API v2 Documentation](/docs/v2)
    """,
    version="1.0.0",
    docs_url="/docs/v1",
    redoc_url="/docs/v1/redoc",
    openapi_url="/openapi/v1.json"
)

app_v2 = FastAPI(
    title="Payment API v2",
    description="""
    API thanh toán phiên bản 2.0 - Enhanced version
    
    **New Features:**
    - Customer information support
    - Custom metadata
    - Webhook notifications
    - Payment status updates
    - Payment cancellation
    - Pagination and filtering
    
    **Previous Version**: [API v1 Documentation (Deprecated)](/docs/v1)
    """,
    version="2.0.0",
    docs_url="/docs/v2",
    redoc_url="/docs/v2/redoc",
    openapi_url="/openapi/v2.json"
)

# Register routes to version-specific apps
app_v1.include_router(v1_routes.router, prefix="/api/v1", tags=["v1 - Payments"])
app_v2.include_router(v2_routes.router, prefix="/api/v2", tags=["v2 - Payments", "v2 - Webhooks"])

# Mount version-specific apps to main app
app.mount("/v1", app_v1)
app.mount("/v2", app_v2)

# Register routes to main app as well (for combined docs)
app.include_router(v1_routes.router, prefix="/api/v1", tags=["v1 (DEPRECATED)"])
app.include_router(v2_routes.router, prefix="/api/v2", tags=["v2 - Payments", "v2 - Webhooks"])


@app.get("/")
async def root():
    return {
        "message": "Payment API Demo",
        "versions": {
            "v1": {
                "base_url": "/api/v1",
                "docs": "/docs/v1",
                "status": "deprecated",
                "sunset_date": "2026-06-01"
            },
            "v2": {
                "base_url": "/api/v2",
                "docs": "/docs/v2",
                "status": "active"
            }
        },
        "documentation": {
            "combined": "/docs",
            "v1_only": "/docs/v1",
            "v2_only": "/docs/v2",
            "migration_guide": "/docs/MIGRATION_GUIDE.md"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
