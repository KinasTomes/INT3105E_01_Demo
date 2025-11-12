from datetime import datetime, timedelta
from typing import Dict
import jwt
import uuid
from passlib.context import CryptContext
from fastapi import HTTPException, status
from openapi_server.general_settings import Settings

from openapi_server.apis.authentication_api_base import BaseAuthenticationApi
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.refresh_request import RefreshRequest
from openapi_server.models.token_response import TokenResponse
from openapi_server.db import get_collection


settings = Settings()

# JWT Configuration (read from settings)
SECRET_KEY = settings.access_secret
REFRESH_SECRET_KEY = settings.refresh_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationApiImpl(BaseAuthenticationApi):
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def _create_access_token(self, username: str, user_data: dict) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": username,
            "type": "access",
            "role": user_data.get("role", "user"),
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    async def _create_refresh_token(self, user_id: str, username: str) -> str:
        """
        Create JWT refresh token with JTI (JWT ID)
        Store token metadata in MongoDB refresh_tokens collection
        """
        # Generate unique JTI
        jti = str(uuid.uuid4())
        
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": username,
            "jti": jti,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        
        # Store refresh token metadata in MongoDB
        refresh_tokens_collection = get_collection("refresh_tokens")
        await refresh_tokens_collection.insert_one({
            "user_id": user_id,
            "jti": jti,
            "expires_at": expire,
            "created_at": datetime.utcnow()
        })
        
        return token

    async def _revoke_user_refresh_tokens(self, user_id: str) -> int:
        """
        Revoke all existing refresh tokens for a given user by removing
        their token metadata records from the database. Returns number revoked.
        """
        refresh_tokens_collection = get_collection("refresh_tokens")
        result = await refresh_tokens_collection.delete_many({"user_id": user_id})
        return result.deleted_count
    
    async def _verify_refresh_token(self, token: str) -> tuple[str, str]:
        """
        Verify refresh token and return (username, user_id)
        Check both JWT validity and JTI presence in MongoDB
        """
        try:
            # Decode and verify JWT signature
            payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            username = payload.get("sub")
            jti = payload.get("jti")
            
            if username is None or jti is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Check if JTI exists in database (not revoked)
            refresh_tokens_collection = get_collection("refresh_tokens")
            token_record = await refresh_tokens_collection.find_one({"jti": jti})
            
            if not token_record:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked or does not exist"
                )
            
            return username, token_record["user_id"]
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def login(self, login_request: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return access token + refresh token
        
        Checks credentials against MongoDB users collection
        """
        users_collection = get_collection("users")
        
        # Get username and password
        username = login_request.username
        password = login_request.password.get_secret_value()
        
        # Find user in database
        user = await users_collection.find_one({"username": username})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        if not self._verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Get user_id (MongoDB _id or custom id field)
        user_id = str(user.get("_id", user.get("id", username)))
        
        # Revoke existing refresh tokens for this user (single-session policy)
        await self._revoke_user_refresh_tokens(user_id)

        # Create tokens
        access_token = self._create_access_token(username, user)
        refresh_token = await self._create_refresh_token(user_id, username)
        
        # Update last login timestamp
        await users_collection.update_one(
            {"username": username},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(self, refresh_request: RefreshRequest) -> TokenResponse:
        """
        Exchange refresh token for new access token
        
        Verifies the refresh token and generates a new access token
        """
        refresh_token = refresh_request.refresh_token
        
        # Verify refresh token and get username and user_id
        username, user_id = await self._verify_refresh_token(refresh_token)
        
        # Get user from database
        users_collection = get_collection("users")
        user = await users_collection.find_one({"username": username})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = self._create_access_token(username, user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
