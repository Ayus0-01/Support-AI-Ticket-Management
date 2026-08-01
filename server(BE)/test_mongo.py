from pymongo import MongoClient

uri = "mongodb+srv://aiticket:<supportai123>@cluster0.a6ff7jc.mongodb.net/SupportAI?appName=Cluster0"

try:
    client = MongoClient(uri)
    client.admin.command("ping")
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Error:")
    print(e)