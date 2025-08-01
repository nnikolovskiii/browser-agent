from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from src.database.collections.user_info import User
from src.database.mongo import MongoDBDatabase
from src.database.singletons import get_mongo_db


class UserInfoPayload(BaseModel):
    info: str


router = APIRouter()
db_dep = Annotated[MongoDBDatabase, Depends(get_mongo_db)]


@router.get("/{user_id}")
async def get_user_info(user_id: str, db: db_dep):
    try:
        user_info = await db.get_entry(ObjectId(user_id), User)
        if user_info:
            return user_info
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "User not found"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"An error occurred: {e}"})


@router.post("/")
async def create_user_info(payload: UserInfoPayload, db: db_dep):
    try:
        user_info = User(info=payload.info)
        await db.add_entry(user_info)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User info saved"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"An error occurred: {e}"})
