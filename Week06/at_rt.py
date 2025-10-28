"""
Access Token & Refresh Token Demo with FastAPI

This demonstrates:
- Access Token: Short-lived token for API access (15 minutes)
- Refresh Token: Long-lived token to get new access tokens (7 days)
- Token refresh endpoint to exchange refresh token for new access token
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt

app = FastAPI(title="Access Token & Refresh Token Demo")

# ------------------------
# Configuration
# ------------------------
SECRET_KEY = "hello-nigeria-access-token-secret"
REFRESH_SECRET_KEY = "hello-nigeria-refresh-token-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.5
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()

# ------------------------
# Fake Database
# ------------------------
users_db = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

books_db = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "year": 2023},
    {"id": 2, "title": "Web Development", "author": "Jane Smith", "year": 2024},
    {"id": 3, "title": "Data Science", "author": "Bob Johnson", "year": 2023}
]

# Store active refresh tokens (in production, use Redis or database)
active_refresh_tokens: Dict[str, str] = {}

# ------------------------
# Request/Response Models
# ------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int

# ------------------------
# JWT Helper Functions
# ------------------------
def create_access_token(username: str, role: str) -> str:
    """Create short-lived access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str) -> str:
    """Create long-lived refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": username,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    # Store refresh token
    active_refresh_tokens[token] = username
    return token

def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify and decode access token"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Access token required."
            )
        
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please use refresh token to get a new one."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

def verify_refresh_token(refresh_token: str) -> str:
    """Verify and decode refresh token"""
    try:
        # Check if token is in active list
        if refresh_token not in active_refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or does not exist"
            )
        
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Refresh token required."
            )
        
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return username
    
    except jwt.ExpiredSignatureError:
        # Remove expired token from active list
        if refresh_token in active_refresh_tokens:
            del active_refresh_tokens[refresh_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please login again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# ------------------------
# API Endpoints
# ------------------------

@app.get("/", include_in_schema=False)
def root():
    """API information"""
    return {
        "message": "Access Token & Refresh Token Demo with FastAPI",
        "endpoints": {
            "login": "POST /login - Get access token and refresh token",
            "refresh": "POST /refresh - Exchange refresh token for new access token",
            "books": "GET /books - List books (requires access token)",
            "logout": "POST /logout - Revoke refresh token"
        },
        "token_info": {
            "access_token_lifetime": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "refresh_token_lifetime": f"{REFRESH_TOKEN_EXPIRE_DAYS} days"
        }
    }

@app.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """
    Login endpoint - returns both access token and refresh token
    
    Access Token: Short-lived (0.5 min) - use for API requests
    Refresh Token: Long-lived (7 days) - use to get new access tokens
    """
    username = credentials.username
    password = credentials.password
    
    # Check credentials
    if username not in users_db or users_db[username]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    user = users_db[username]
    
    # Create tokens
    access_token = create_access_token(username, user["role"])
    refresh_token = create_refresh_token(username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    )

@app.post("/refresh")
def refresh_access_token(request: RefreshRequest):
    """
    Refresh endpoint - exchange refresh token for new access + new refresh token
    """
    username = verify_refresh_token(request.refresh_token)
    
    # Xoá refresh token cũ
    if request.refresh_token in active_refresh_tokens:
        del active_refresh_tokens[request.refresh_token]
    
    # Tạo access token mới
    user = users_db[username]
    new_access_token = create_access_token(username, user["role"])
    
    # 🔁 Tạo refresh token mới
    new_refresh_token = create_refresh_token(username)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "message": "Access & Refresh tokens renewed successfully"
    }

@app.post("/logout")
def logout(request: RefreshRequest):
    """
    Logout endpoint - revoke refresh token
    
    This removes the refresh token from the active list,
    preventing it from being used to generate new access tokens.
    """
    refresh_token = request.refresh_token
    
    if refresh_token in active_refresh_tokens:
        username = active_refresh_tokens[refresh_token]
        del active_refresh_tokens[refresh_token]
        return {
            "message": f"User {username} logged out successfully",
            "detail": "Refresh token has been revoked"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found or already revoked"
        )

@app.get("/books")
def get_books(current_user: dict = Depends(verify_access_token)):
    """
    Protected endpoint - requires valid access token
    
    Returns list of books. Only accessible with a valid access token.
    """
    return {
        "user": current_user["sub"],
        "role": current_user["role"],
        "books": books_db
    }

@app.get("/books/{book_id}")
def get_book(book_id: int, current_user: dict = Depends(verify_access_token)):
    """Get a specific book - requires access token"""
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return {
        "user": current_user["sub"],
        "book": book
    }

@app.get("/me")
def get_current_user(current_user: dict = Depends(verify_access_token)):
    """Get current user info from access token"""
    return {
        "username": current_user["sub"],
        "role": current_user["role"],
        "token_type": current_user["type"],
        "issued_at": datetime.fromtimestamp(current_user["iat"]).isoformat(),
        "expires_at": datetime.fromtimestamp(current_user["exp"]).isoformat()
    }

@app.get("/admin/tokens")
def list_active_tokens(current_user: dict = Depends(verify_access_token)):
    """Admin endpoint - list all active refresh tokens"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "active_refresh_tokens": len(active_refresh_tokens),
        "users": list(set(active_refresh_tokens.values()))
    }

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Access Token & Refresh Token Demo")
    print("=" * 60)
    print(f"Access Token Lifetime: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"Refresh Token Lifetime: {REFRESH_TOKEN_EXPIRE_DAYS} days")
    print("\nTest credentials:")
    print("  - admin / admin123")
    print("  - user / user123")
    print("\nServer running on: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
