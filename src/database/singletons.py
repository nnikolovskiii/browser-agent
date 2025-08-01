from typing import Optional

from src.database.mongo import MongoDBDatabase

mdb = None


async def get_mongo_db(url: Optional[str] = None) -> MongoDBDatabase:
    global mdb
    if mdb is None:
        mdb = MongoDBDatabase(url=url)
    return mdb