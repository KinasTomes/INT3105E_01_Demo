"""
Setup MongoDB indexes including TTL index for refresh_tokens collection

Run this script once to create the necessary indexes.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING

from src.openapi_server.general_settings import Settings

settings = Settings()

# Configuration - update with your actual MongoDB URL
MONGO_URL = settings.mongo_url
DATABASE_NAME = settings.mongo_db_name

async def setup_indexes():
    """Create indexes for MongoDB collections"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("Setting up MongoDB indexes...")
    print(f"Database: {DATABASE_NAME}")
    print("-" * 60)
    
    # 1. Setup TTL index for refresh_tokens collection
    refresh_tokens_collection = db["refresh_tokens"]
    
    # Create TTL index on expires_at field
    # MongoDB will automatically delete documents when current time > expires_at
    print("\n📅 Creating TTL index on refresh_tokens.expires_at...")
    await refresh_tokens_collection.create_index(
        [("expires_at", ASCENDING)],
        name="expires_at_ttl",
        expireAfterSeconds=0  # Delete immediately when expires_at is reached
    )
    print("✅ TTL index created: refresh_tokens.expires_at")
    print("   MongoDB will automatically delete expired tokens")
    
    # Create index on jti for fast lookup
    print("\n🔍 Creating index on refresh_tokens.jti...")
    await refresh_tokens_collection.create_index(
        [("jti", ASCENDING)],
        name="jti_unique",
        unique=True
    )
    print("✅ Unique index created: refresh_tokens.jti")
    
    # Create index on user_id for fast lookup by user
    print("\n👤 Creating index on refresh_tokens.user_id...")
    await refresh_tokens_collection.create_index(
        [("user_id", ASCENDING)],
        name="user_id_index"
    )
    print("✅ Index created: refresh_tokens.user_id")
    
    # 2. Setup indexes for users collection
    users_collection = db["users"]
    
    print("\n📝 Creating index on users.username...")
    await users_collection.create_index(
        [("username", ASCENDING)],
        name="username_unique",
        unique=True
    )
    print("✅ Unique index created: users.username")
    
    # List all indexes to verify
    print("\n" + "=" * 60)
    print("Created indexes for refresh_tokens:")
    indexes = await refresh_tokens_collection.list_indexes().to_list(None)
    for idx in indexes:
        print(f"  - {idx['name']}: {idx.get('key', {})}")
        if 'expireAfterSeconds' in idx:
            print(f"    TTL: {idx['expireAfterSeconds']} seconds after expires_at")
    
    print("\nCreated indexes for users:")
    indexes = await users_collection.list_indexes().to_list(None)
    for idx in indexes:
        print(f"  - {idx['name']}: {idx.get('key', {})}")
    
    # Close connection
    client.close()
    print("\n✅ Done! All indexes created successfully")
    print("\n💡 Tips:")
    print("  - Expired refresh tokens will be automatically deleted by MongoDB")
    print("  - JTI lookup will be fast with unique index")
    print("  - User lookup will be fast with username index")


if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Index Setup")
    print("=" * 60)
    asyncio.run(setup_indexes())
