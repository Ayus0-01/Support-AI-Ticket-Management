from pymongo import MongoClient
from decouple import config


client = MongoClient(config('MONGO_URI'))

db = client["SupportAI"]

tickets_collection = db['tickets']
users_collection = db['users']