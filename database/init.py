"""
Init script for a MongoDB database from a JSON configuration file.
This script setups up a MongoDB instance (or cluster) with a defined database
and collections.
"""
from pymongo import errors
import argparse
import pymongo
import json
import sys
import os
import time

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

def database_exists(dbname: str, names: list):
    for name in names:
        if name == dbname:
            return True
    return False
    
def main(is_cluster = False):
    
    hostname = os.getenv("EPA_MONGODB_HOSTNAME")
    port = os.getenv("EPA_MONGODB_PORT")
    username = os.getenv("EPA_MONGODB_USERNAME")
    password = os.getenv("EPA_MONGODB_PASSWORD")
    dbname = os.getenv("EPA_MONGODB_DATABASE_NAME")
    if not all([hostname, port, username, password, dbname]):
        print(f"All Environment vairables are not set. Variables:\n \
            EPA_MONGODB_HOSTNAME={hostname}\n \
            EPA_MONGODB_PORT={port}\n \
            EPA_MONGODB_USERNAME={username}\n \
            EPA_MONGODB_PASSWORD={password}\n \
            EPA_MONGODB_DATABASE_NAME={dbname} \
        ", file=sys.stderr)
        sys.exit(1)
        
    config_file = {}
    with open("config.json", "r") as file:
        config_file = json.loads(file.read())
    
    uri = f"mongodb://{username}:{password}@{hostname}:{port}/"
    if is_cluster:
        uri = f"mongodb+srv://{username}:{password}@{hostname}/?tls=false"
        
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    tries = 10
    while True:
        try:
            print(f"Waiting for response from {hostname} ...", flush=True)
            client.admin.command("ping")
            break
        except errors.ConnectionFailure:
            tries -= 1
            if tries == 0:
                print(f"Failed to connect to {hostname} after 10 tries", file=sys.stderr)
                sys.exit(1)
            time.sleep(10)
                
    print("Connected.")
    if not dbname:
        print("Databse name not given.", file=sys.stderr)
        sys.exit(1)
        
    try:
        if database_exists(dbname, client.list_database_names()):
            print("Database exists, aborting...")
            sys.exit(0)
            
        db = client[dbname]
        for collection in config_file.get("collections", []):
            
            db.create_collection(collection.get("name", ""))
            new_collection = db[collection.get("name", "")]
            for idx in collection.get("indexes", []):
                if idx.get("compound",None):
                    create_compound_index(new_collection, idx.get("fields", []))
                else:
                    if idx.get("expireAfterSeconds", None):
                        create_index_with_expire_time(new_collection, idx)
                    else:
                        create_standard_index(new_collection, idx)
                        
            documents = collection.get("init", [])
            if documents:
                new_collection.insert_many(documents)
                        
        print(f"MongoDB database at {hostname} initialized")
        
    except Exception as e:
        
        print(f"error: Failed to initialize MongoDB at {hostname}, {e}", file=sys.stderr)
        sys.exit(1)
        
    finally:
        client.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="init", description="MongoDB init script", usage="%(prog)s [options]")
    parser.add_argument(
        "-c", 
        "--is-cluster", 
        action="store_true", 
        default=False, 
        help="True if the MongoDB instance runs as a cluster, \
              will call MongoDB with the srv+ protocal and connect to the primary node"
    )
    args = parser.parse_args()    
    main(is_cluster=args.is_cluster)
    