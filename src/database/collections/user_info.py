from src.database.mongo import MongoEntry


class User(MongoEntry):
    info: str
