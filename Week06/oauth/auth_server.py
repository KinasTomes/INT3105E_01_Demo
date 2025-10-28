"""
AUTH SERVER (Authorization Server)
-----------------------------------
Chức năng:
- /authorize : user login và cấp quyền (trả code)
- /token     : đổi code thành access token
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from datetime import datetime, timedelta
import jwt
import uuid

app = FastAPI(title="OAuth2 Auth Server")

# Cấu hình
SECRET_KEY = "super-secret-auth-server"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

# Giả lập database người dùng và code
fake_users = {"admin": "admin123"}
auth_codes = {}  # code -> username

# ---------------------
# Trang login (HTML)
# ---------------------
@app.get("/authorize", response_class=HTMLResponse)
def authorize(client_id: str, redirect_uri: str, state: str):
    """
    Giả lập bước user login + consent
    - Thực tế: hiển thị form để user nhập username/password
    - Sau khi login ok: redirect về client kèm code
    """
    html = f"""
    <h3>OAuth2 Authorization Server</h3>
    <form method="post" action="/login">
        <input type="hidden" name="client_id" value="{client_id}">
        <input type="hidden" name="redirect_uri" value="{redirect_uri}">
        <input type="hidden" name="state" value="{state}">
        <label>Username:</label><br><input name="username"><br>
        <label>Password:</label><br><input name="password" type="password"><br><br>
        <button type="submit">Login & Authorize</button>
    </form>
    """
    return HTMLResponse(html)


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...)
):
    if username not in fake_users or fake_users[username] != password:
        return HTMLResponse("<h3>❌ Invalid credentials</h3>", status_code=401)

    # Sinh authorization code ngẫu nhiên
    code = str(uuid.uuid4())
    auth_codes[code] = username
    print(f"[AuthServer] Issued code for {username}: {code}")

    # Redirect về client (Resource server)
    redirect_url = f"{redirect_uri}?code={code}&state={state}"
    return RedirectResponse(redirect_url)


@app.post("/token")
def exchange_code_for_token(
    code: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    redirect_uri: str = Form(...)
):
    """
    Client gửi code để đổi access token
    """
    if code not in auth_codes:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    username = auth_codes.pop(code)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": username, "exp": expire, "iat": datetime.utcnow()},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    print(f"[AuthServer] Issued token for {username}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
