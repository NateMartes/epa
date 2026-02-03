"""
Init script for a MongoDB database from a JSON configuration file
"""

import pymongo
import json
import sys
import os

hostname = os.getenv("EPA_MONGODB_HOSTNAME")
port = os.getenv("EPA_MONGODB_PORT")
username = os.getenv("EPA_MONGODB_USERNAME")
password = os.getenv("EPA_MONGODB_PASSWORD")
dbname = hostname = os.getenv("EPA_MONGODB_DATABASE_NAME")
if not hostname or \
    not port or \
    not username or \
    not password or \
    not dbname:
    print("All Environment vairables are not set {MONGO_DB_HOSTNAME, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD} not set.", file=sys.stderr)
    sys.exit(1)
    
config_file = {}
with open("config.json", "r") as file:
    config_file = json.loads(file.read())
    
uri = f"mongodb://{username}:{password}@{hostname}:{port}/?authSource=admin"
client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

try:
    client.admin.command('ping')
    
    db = client[dbname]
    for collection in config_file.get("collections", []):
        db.create_collection(collection.get("name", ""))
        new_collection = db[collection.get("name", "")]
        for idx in collection.get("indexes", []):
            if idx.get("expireAfterSeconds", None):
                new_collection.create_index(idx.get("field", ""), 
                    unique=idx.get("unique", False),
                    sparse=idx.get("sparse", False),
                    expireAfterSeconds=idx.get("expireAfterSeconds", 0))
                                            
            else:
                new_collection.create_index(idx.get("field", ""), 
                    unique=idx.get("unique", False), 
                    sparse=idx.get("sparse", False))
            
    print(f"MongoDB database at {hostname}:{port} initialized")
    
except Exception as e:
    
    print(f"error: Failed to initialize MongoDB at {hostname}:{port}, {e}", file=sys.stderr)
    
finally:
    client.close()
    
    