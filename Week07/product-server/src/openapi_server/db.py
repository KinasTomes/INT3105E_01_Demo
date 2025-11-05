# openapi_server/db.py

from motor.motor_asyncio import AsyncIOMotorClient
from .general_settings import Settings

settings = Settings()

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