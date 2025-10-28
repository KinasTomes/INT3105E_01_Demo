"""
RESOURCE SERVER
-----------------
Cung cấp API được bảo vệ:
- /login_demo : link để mô phỏng redirect tới Auth Server
- /callback   : nhận code từ Auth Server, đổi lấy token
- /me         : truy cập bằng Bearer token
"""

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import jwt

app = FastAPI(title="OAuth2 Resource Server")

# Config
AUTH_SERVER_URL = "http://127.0.0.1:8001"
CLIENT_ID = "demo-client"
CLIENT_SECRET = "demo-secret"
REDIRECT_URI = "http://127.0.0.1:8000/callback"
SECRET_KEY = "super-secret-auth-server"  # phải khớp với Auth Server
ALGORITHM = "HS256"

security = HTTPBearer()

# ---------------------
# Simulate client login flow
# ---------------------
@app.get("/login_demo")
def login_demo():
    """
    Giả lập client mở luồng OAuth2 để đăng nhập
    """
    state = "xyz123"
    authorize_url = (
        f"{AUTH_SERVER_URL}/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}"
    )
    return RedirectResponse(authorize_url)


@app.get("/callback")
def oauth_callback(code: str, state: str):
    """
    Nhận code từ Auth Server, đổi sang access token
    """
    token_url = f"{AUTH_SERVER_URL}/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return JSONResponse({"error": "cannot exchange code"}, status_code=400)

    token = r.json()["access_token"]
    print(f"[ResourceServer] Received token: {token[:30]}...")

    return {
        "message": "✅ Login successful!",
        "access_token": token,
        "use": "Call /me with Authorization: Bearer <token>"
    }


@app.get("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    API yêu cầu Bearer token
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user": payload["sub"],
            "issued_at": payload["iat"],
            "expires_at": payload["exp"],
            "books": ["Python 101", "FastAPI Deep Dive", "OAuth2 Simplified"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
