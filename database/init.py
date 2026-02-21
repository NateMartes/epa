"""
Init script for a MongoDB database from a JSON configuration file
"""
from pymongo import errors
import pymongo
import json
import sys
import os

hostname = os.getenv("EPA_MONGODB_HOSTNAME")
port = os.getenv("EPA_MONGODB_PORT")
username = os.getenv("EPA_MONGODB_USERNAME")
password = os.getenv("EPA_MONGODB_PASSWORD")
dbname = os.getenv("EPA_MONGODB_DATABASE_NAME")
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
    
uri = f"mongodb://{username}:{password}@{hostname}:{port}/"
client = None

tries = 10
while True:
    try:
        print(f"Waiting for response from {hostname}:{port} ...")
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=10000)
        break
    except errors.ConnectionFailure:
        tries -= 1
        if tries == 0:
            print(f"Failed to connect to {hostname}:{port} after 10 tries", file=sys.stderr)
            sys.exit(1)
            
print("Connected.")
def get_index_defition(map):
    
    name = map.get("field", "")
    index_type = pymongo.ASCENDING
    if map.get("descending", None):
        index_type = pymongo.DESCENDING
    
    return (name, index_type)
    
def create_compound_index(collection, fields):
    
    index_defition = []
    for idx_part in fields:
        index_defition.append(get_index_defition(idx_part))
        
    collection.create_index(index_defition)
    
def create_index_with_expire_time(collection, index):

    index_defition = [get_index_defition(index)]
    collection.create_index(index_defition, 
        unique=index.get("unique", False),
        sparse=index.get("sparse", False),
        expireAfterSeconds=index.get("expireAfterSeconds", 0))
    
def create_standard_index(collection, index):
    
    index_defition = [get_index_defition(index)]
    collection.create_index(index_defition, 
        unique=index.get("unique", False), 
        sparse=index.get("sparse", False))
try:
    client.admin.command('ping')
    dbs = client.list_database_names()
    for name in dbs:
        if name == dbname:
            print("Database already exists, aborting")
            sys.exit(0)
    
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
                    
        documents = collection.get("init", [])
        if documents:
            new_collection.insert_many(documents)
                    
    print(f"MongoDB database at {hostname}:{port} initialized")
    
except Exception as e:
    
    print(f"error: Failed to initialize MongoDB at {hostname}:{port}, {e}", file=sys.stderr)
    sys.exit(1)
    
finally:
    client.close()
    
    