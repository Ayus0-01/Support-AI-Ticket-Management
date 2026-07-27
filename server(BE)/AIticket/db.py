from pymongo import MongoClient
from decouple import config
client = MongoClient(config('MONGO_URI'))
db = client.get_default_database()
tickets_collection = db['tickets']
users_collection = db['users']