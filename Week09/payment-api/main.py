"""
Payment API Demo - Main Application
Supports multiple API versions (v1, v2)
"""
from fastapi import FastAPI
from api.v1 import routes as v1_routes
from api.v2 import routes as v2_routes

app = FastAPI(
    title="Payment API Demo",
    description="Demo API thanh toán với versioning",
    version="1.0.0"
)

# Register v1 routes
app.include_router(v1_routes.router, prefix="/api/v1", tags=["v1"])

# Register v2 routes
app.include_router(v2_routes.router, prefix="/api/v2", tags=["v2"])


@app.get("/")
async def root():
    return {
        "message": "Payment API Demo",
        "versions": {
            "v1": "/api/v1",
            "v2": "/api/v2"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
