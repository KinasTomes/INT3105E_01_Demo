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
    try:
        # SSL/TLS configuration for MongoDB Atlas
        db.client = AsyncIOMotorClient(
            settings.mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=False
        )
        # Test connection
        await db.client.admin.command('ping')
        db.db = db.client[settings.mongo_db_name] # Chọn Database
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Falling back to local MongoDB...")
        try:
            db.client = AsyncIOMotorClient("mongodb://localhost:27017")
            await db.client.admin.command('ping')
            db.db = db.client[settings.mongo_db_name]
            print("Connected to local MongoDB!")
        except Exception as local_e:
            print(f"Failed to connect to local MongoDB: {local_e}")
            raise

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