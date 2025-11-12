from contextlib import asynccontextmanager
from .db import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app):
    await connect_to_mongo()
    yield
    await close_mongo_connection()
