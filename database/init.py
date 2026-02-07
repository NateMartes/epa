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
    print("All Environment vairables are not set", file=sys.stderr)
    sys.exit(1)
    
config_file = {}
with open("config.json", "r") as file:
    config_file = json.loads(file.read())
    
uri = f"mongodb://{username}:{password}@{hostname}:{port}/?authSource=admin"
client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

def create_compound_index(collection, fields):
    
    index_defition = []
    for idx_part in idx.get("fields",[]):
        name = idx_part.get("field", "")
        ascending = idx_part.get("ascending", False)
        descending = idx_part.get("descending", False)
        if ascending:
            index_defition.append((name, pymongo.ASCENDING))
        elif descending:
            index_defition.append((name, pymongo.DESCENDING))
        else:
            print(f"Warning: compound index part {name} needs either 'ascending' or 'descending'. Skipping part")
        
    collection.create_index(index_defition)
    
def create_index_with_expire_time(collection, index):
    collection.create_index(index.get("field", ""), 
        unique=index.get("unique", False),
        sparse=index.get("sparse", False),
        expireAfterSeconds=index.get("expireAfterSeconds", 0))
    
def create_standard_index(collection, index):
    collection.create_index(index.get("field", ""), 
        unique=index.get("unique", False), 
        sparse=index.get("sparse", False))
try:
    client.admin.command('ping')
    
    db = client[dbname]
    for collection in config_file.get("collections", []):
        
        db.create_collection(collection.get("name", ""))
        new_collection = db[collection.get("name", "")]
        for idx in collection.get("indexes", []):
            if idx.get("compound",None):
                create_compound_index(new_collection, idx.get("fields", []))
            else:
                field_name = idx.get("field", "")
                if idx.get("expireAfterSeconds", None):
                    create_index_with_expire_time(new_collection, idx)
                else:
                    create_standard_index(new_collection, idx)
                    
    print(f"MongoDB database at {hostname}:{port} initialized")
    
except Exception as e:
    
    print(f"error: Failed to initialize MongoDB at {hostname}:{port}, {e}", file=sys.stderr)
    
finally:
    client.close()
    
    