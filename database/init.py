"""
Init script for a MongoDB database from a JSON configuration file
"""

import pymongo
import json
import sys
import os

hostname = os.getenv("MONGO_DB_HOSTNAME")
username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
if not hostname or not username or not password:
    print("All Environment vairables are not set {MONGO_DB_HOSTNAME, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD} not set.", file=sys.stderr)
    sys.exit(1)
    
config_file = {}
with open("config.json", "r") as file:
    config_file = json.loads(file.read())
    
uri = f"mongodb://{username}:{password}@{hostname}:27017/?authSource=admin"
client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

try:
    client.admin.command('ping')
    
    db = client["epa_database"]
    for collection in config_file.get("collections", []):
        db.create_collection(collection.get("name", ""))
        new_collection = db[collection.get("name", "")]
        for idx in collection.get("indexes", []):
            if idx.get("expireAfterSeconds", None):
                new_collection.create_index(idx.get("field", ""), unique=idx.get("unique", False), expireAfterSeconds=idx.get("expireAfterSeconds", 0))
            else:
                new_collection.create_index(idx.get("field", ""), unique=idx.get("unique", False))
            
    print(f"MongoDB database at {hostname}:27017 initialized")
    
except Exception as e:
    
    print(f"error: Failed to initialize MongoDB at {hostname}:27017, {e}", file=sys.stderr)
    
finally:
    client.close()
    
    