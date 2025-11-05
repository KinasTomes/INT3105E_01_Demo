# openapi_server/db.py

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

class MongoSettings(BaseSettings):
    # Nó sẽ tự động đọc từ biến môi trường, ví dụ: MONGO_URL=...
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "my_database"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = MongoSettings()

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """Kết nối tới MongoDB khi app khởi động"""
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.mongo_url)
    db.db = db.client[settings.mongo_db_name] # Chọn Database
    print("Connected to MongoDB!")

async def close_mongo_connection():
    """Đóng kết nối khi app tắt"""
    print("Closing MongoDB connection...")
    db.client.close()
    print("MongoDB connection closed.")

def get_database():
    """Hàm helper để lấy đối tượng db"""
    if db.db is None:
        raise Exception("Database not initialized. Call connect_to_mongo first.")
    return db.db

def get_collection(name: str):
    """Hàm helper để lấy một collection cụ thể"""
    return get_database()[name]