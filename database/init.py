"""
Init script for a MongoDB database from a JSON configuration file
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
    
def init_replica_set(client, replica_set_name, hosts):
    members = []
    count = 0
    
    for _ in hosts:
        members.append({
            '_id': count, 'host': hosts[count]
        })
        count += 1
        
    config = {
        '_id': replica_set_name,
        'members': members
    }
    
    # Make sure replica set does not already exist
    try:
        status = client.admin.command('replSetGetStatus')
        print("Replica set status:", status['ok'])
        if status['ok'] == 1.0:
            print("Replica set already exists")
            return
    except errors.OperationFailure as e:
        print(f"Failed to get replica set status: {e}")
   
    # Make replica set
    try:
        client.admin.command('replSetInitiate', config)
        print(f"Replica set '{replica_set_name}' initiated successfully")
    except errors.OperationFailure as e:
        print(f"Failed to initiate replica set: {e}", file=sys.stderr)
       
    # Wait for set to be ready
    tries = 5
    while True:
        try:
            print("Waiting for replica set to be ready...")
            status = client.admin.command('replSetGetStatus')
            print("Replica set status:", status['ok'])
            if status['ok'] == 1.0:
                return
            else:
                tries -= 1
                if tries == 0:
                    print("Failed to wait for replica set to be ready, aborting...", file=sys.stderr)
                    sys.exit(1)
                else:
                    time.sleep(5)
                    continue
        except errors.OperationFailure as e:
            print(f"Failed to get replica set status: {e}")
            sys.exit(1)
    
def main(is_replica_set = False, replica_set_name = "", nodes = []):
    
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
        
    uri = f"mongodb://{username}:{password}@{hostname}:{port}/?directConnection=true"
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
    
    tries = 10
    while True:
        try:
            print(f"Waiting for response from {hostname}:{port} ...", flush=True)
            client.admin.command("ping")
            break
        except errors.ConnectionFailure:
            tries -= 1
            if tries == 0:
                print(f"Failed to connect to {hostname}:{port} after 10 tries", file=sys.stderr)
                sys.exit(1)
            time.sleep(10)
                
    print("Connected.")
    
    if is_replica_set:
        print(f"Setting up replica set '{replica_set_name}'")
        init_replica_set(client, replica_set_name, nodes)
    
    try:
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
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="init", description="MongoDB init script", usage="%(prog)s [options]")
    parser.add_argument("-c", "--is-replica-set", action="store_true", default=False, help="True if the MongoDB instance runs as a cluster")
    parser.add_argument("-r", "--replica-set-name", type=str, default="", help="The name of the replica set for the MongoDB cluster")
    parser.add_argument("-n", "--nodes", type=str, default="", help="A comma seperated list of hostnames for the nodes in the cluster")
    args = parser.parse_args()
    
    if args.is_replica_set:
        if args.replica_set_name == "" or args.nodes == "":
            print("init: error: if replica set, set name and nodes must be given", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        
    nodes_split = args.nodes.split(",")
    main(
        is_replica_set=args.is_replica_set,
        replica_set_name=args.replica_set_name, 
        nodes=nodes_split
    )
    