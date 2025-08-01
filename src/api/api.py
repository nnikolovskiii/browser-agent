from contextlib import asynccontextmanager

from fastapi import FastAPI

import uvicorn

from src.api.user import user
from src.database.singletons import get_mongo_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_mongo_db()
    yield
    mdb = await get_mongo_db()
    mdb.client.close()


prefix = "/api"
app = FastAPI(lifespan=lifespan)
app.include_router(user.router, prefix=prefix + "/user", tags=["user "])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)