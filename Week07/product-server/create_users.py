"""
Create initial users in MongoDB for testing

Run this script once to populate the users collection with test users.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

# Configuration
MONGO_URL = "mongodb+srv://trinhquanghunglk2014_db_user:<db_password>@testproduct.va2tbdm.mongodb.net/?appName=TestProduct"
DATABASE_NAME = "my_database"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_users():
    """Create initial users in MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    # Test users to create
    test_users = [
        {
            "username": "admin",
            "password": pwd_context.hash("admin123"),
            "role": "admin",
            "email": "admin@example.com",
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        {
            "username": "user",
            "password": pwd_context.hash("user123"),
            "role": "user",
            "email": "user@example.com",
            "created_at": datetime.utcnow(),
            "last_login": None
        }
    ]
    
    # Create users (update if exists)
    for user in test_users:
        result = await users_collection.update_one(
            {"username": user["username"]},
            {"$set": user},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"✅ Created user: {user['username']}")
        else:
            print(f"🔄 Updated user: {user['username']}")
    
    # Close connection
    client.close()
    print(f"\n✅ Done! Created/updated {len(test_users)} users")
    print("\nTest credentials:")
    for user in test_users:
        password = "admin123" if user["username"] == "admin" else "user123"
        print(f"  - {user['username']} / {password} (role: {user['role']})")


if __name__ == "__main__":
    print("Creating test users in MongoDB...")
    print(f"Database: {DATABASE_NAME}")
    print("-" * 60)
    asyncio.run(create_users())
