from pymongo import MongoClient
from decouple import config


client = MongoClient(config('MONGO_URI'))

db = client["SupportAI"]

tickets_collection = db['tickets']
users_collection = db['users']
counters_collection = db['counters']
classification_overrides_collection = db['classification_overrides']
status_history_collection = db['status_history']
comments_collection = db["ticket_comments"]