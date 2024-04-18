from pymongo import MongoClient
class MongoDB(object):
    def __init__(self, host: str = 'localhost',
                 port: int = 27017,
                 db_name: str = None,
                 collection: str = None):
        self._client = MongoClient(f'mongodb://{host}:{port}')
        self._collection = self._client[db_name][collection]

    def create_user(self, user: dict):
        try:
            if self._collection.find_one({"username": user.get('username')}) == None:
                self._collection.insert_one(user)
                print(f"Added New user: {user.get('username')}")
            else:
                print(f"User: {user.get('username')} in collection")
        except Exception as ex:
            print("[create_user] Some problem...")
            print(ex)

    def get_all_users(self):
        try:
            data = self._collection.find()
            print("Get all users")
            return data
        except Exception as ex:
            print("[get_all] Some problem...")
            print(ex)

    def find_by_username(self, username: str):
        try:
            data = self._collection.find_one({"username": username})
            print("Get user by username")
            return data
        except Exception as ex:
            print("[find_by_username] Some problem...")
            print(ex)

    def change_user(self, username: str, key: str, value: str,user:dict):
        try:
            if self._collection.find_one({"username": user.get('username')}) is not None:
                self._collection.update_one({"username": username}, {"$set": {key: value}})
            else:
                print(f'User: {username} not find')
        except Exception as ex:
            print("[change_user] Some problem...")
            print(ex)