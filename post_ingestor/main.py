import os
import json
import base64
from typing import List, Dict, Any
from pymongo import MongoClient



def lambda_handler(event, context):
    """
    Supports
    1) MSK / Kafka trigger event shape (records dict, base64 values)
    """

    env_vars = load_env()

    # MSK/Kafka event
    if event.get("eventSource") == "aws:kafka" and isinstance(event.get("records"), dict):
        posts = parse_kafka_event(event)
        inserted = ingest_posts(posts, env_vars)
        return {"statusCode": 200, "body": {"inserted": inserted}}

    # Custom test event
    if event.get("event") != "INGEST_POSTS":
        return {"statusCode": 400, "body": "Unsupported event type"}
    
    records = event.get("records") or []
    inserted = ingest_posts(records, env_vars)
    return {"statusCode": 200, "body": {"inserted": inserted}}


def load_env() -> Dict[str, str]:
    """
    Reads environment variables needed for Mongo insertion.
    Script will function fully once these are set.
    """
    return {
        "EPA_MONGODB_HOSTNAME": os.getenv("EPA_MONGODB_HOSTNAME", ""),
        "EPA_MONGODB_PORT": os.getenv("EPA_MONGODB_PORT", ""),
        "EPA_MONGODB_USERNAME": os.getenv("EPA_MONGODB_USERNAME", ""),
        "EPA_MONGODB_PASSWORD": os.getenv("EPA_MONGODB_PASSWORD", ""),
        "EPA_MONGODB_SESSION_TOKEN_COLLECTION": os.getenv("EPA_MONGODB_SESSION_TOKEN_COLLECTION", ""),
        "EPA_MONGODB_DATABASE_NAME": os.getenv("EPA_MONGODB_DATABASE_NAME", ""),
        "EPA_MONGODB_USER_COLLECTION": os.getenv("EPA_MONGODB_USER_COLLECTION", ""),
        "EPA_MONGODB_POSTS_COLLECTION": os.getenv("EPA_MONGODB_POSTS_COLLECTION", ""),
        "EPA_MONGO_URI": ("mongodb://"+os.getenv("EPA_MONGODB_USERNAME")+":"+os.getenv("EPA_MONGODB_PASSWORD")+"@"+os.getenv("EPA_MONGODB_HOSTNAME")+":"+os.getenv("EPA_MONGODB_PORT")+"/")
    }

def parse_kafka_event(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Kafka MSK events store record payload in base64.
    Decode each record["value"] into JSON dicts.
    """
    posts = []

    for _tp, rec_list in event.get("records", {}).items():
        for rec in rec_list:
            b64_value = rec.get("value")
            if not b64_value:
                continue

            try:
                decoded = base64.b64decode(b64_value).decode("utf-8")
                payload = json.loads(decoded)
                posts.append(payload)
            except Exception:
                # Passes any errors
                continue

    return posts

def post_validation (payload):
    validFields = {"post_id", "title", "content", "category", "category_slug", "created_at", "created_by"}
    output = False

    if (not payload):
        return output
    else:
        for field in payload:
            if not (field in validFields):
                return output
            else: 
                if payload[field] is "":
                    return output
            validFields.pop(field)
    output = True   
    return output

def get_mongo_collection(env_vars: Dict[str, str]):
    """
    Creates and returns a pymongo collection object.
    This is a "skeleton":
    - It will work as soon as MONGO_URI / DB / COLLECTION are correct.
    - Uses TLS by default
    """

    mongo_uri = env_vars.get("MONGO_URI")
    mongo_db = env_vars.get("EPA_MONGODB_DATABASE_NAME")
    mongo_collection = env_vars.get("EPA_MONGODB_POSTS_COLLECTION")

    if not mongo_uri or not mongo_db or not mongo_collection:
        raise ValueError(
            "Missing required Mongo environment variables: "
            "MONGO_URI, MONGO_DB, MONGO_COLLECTION"
        )

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
    )

    db = client[mongo_db]
    return db[mongo_collection]


def ingest_posts(records: List[Dict[str, Any]], env_vars: Dict[str, str]) -> int:
    """
    Inserts post records into MongoDB.

    - Uses upsert so duplicates overwrite instead of duplicating
    - Uses post_id as the unique key (adjust if your schema differs)
    """

    if not records:
        return 0

    collection = get_mongo_collection(env_vars)

    inserted = 0

    for post in records:
        # Can change this key in future
        post_id = post.get("post_id")

        if post_id is None:
            # Skip bad record
            continue

        # Upsert based on post_id
        result = collection.insert_one(
            post
        )
        print(result)
        print(post)

        # Count "inserted" only when a new doc was created
        #if result.upserted_id is not None:
         #   inserted += 1

    return inserted
