import os
import json
import base64
from typing import List, Dict, Any
from pymongo import MongoClient


def lambda_handler(event, context):
    """
    Supports:
    1) MSK / Kafka trigger event shape (records dict with base64-encoded 'value' fields)
    2) Custom test events with "event": "INGEST_POSTS" containing plain JSON records
    """
    env_vars = load_env()

    # MSK/Kafka event: records dict with base64-encoded values
    if event.get("eventSource") == "aws:kafka" and isinstance(event.get("records"), dict):
        posts = parse_kafka_event(event)
        inserted = ingest_posts(posts, env_vars)
        return {"statusCode": 200, "body": {"inserted": inserted}}

    # Custom test event: plain JSON records
    if event.get("event") != "INGEST_POSTS":
        return {"statusCode": 400, "body": {"error": "Unsupported event type"}}

    records = event.get("records") or []
    inserted = ingest_posts(records, env_vars)
    return {"statusCode": 200, "body": {"inserted": inserted}}


def load_env() -> Dict[str, str]:
    """
    Reads environment variables needed for Mongo insertion.
    All EPA_* variables must be set for successful execution.
    """
    username = os.getenv("EPA_MONGODB_USERNAME", "")
    password = os.getenv("EPA_MONGODB_PASSWORD", "")
    hostname = os.getenv("EPA_MONGODB_HOSTNAME", "")
    port = os.getenv("EPA_MONGODB_PORT", "")
    
    return {
        "EPA_MONGODB_HOSTNAME": hostname,
        "EPA_MONGODB_PORT": port,
        "EPA_MONGODB_USERNAME": username,
        "EPA_MONGODB_PASSWORD": password,
        "EPA_MONGODB_SESSION_TOKEN_COLLECTION": os.getenv("EPA_MONGODB_SESSION_TOKEN_COLLECTION", ""),
        "EPA_MONGODB_DATABASE_NAME": os.getenv("EPA_MONGODB_DATABASE_NAME", ""),
        "EPA_MONGODB_USER_COLLECTION": os.getenv("EPA_MONGODB_USER_COLLECTION", ""),
        "EPA_MONGODB_POSTS_COLLECTION": os.getenv("EPA_MONGODB_POSTS_COLLECTION", ""),
        # Constructed URI (not read from env)
        "EPA_MONGO_URI": f"mongodb://{username}:{password}@{hostname}:{port}/"
    }


def parse_kafka_event(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Decodes base64-encoded Kafka records into JSON post objects.
    This ensures encoded input is ALWAYS decoded before storage.
    """
    posts = []
    for _tp, rec_list in event.get("records", {}).items():
        if not isinstance(rec_list, list):
            continue
        for rec in rec_list:
            if not isinstance(rec, dict):
                continue
            b64_value = rec.get("value")
            if not b64_value:
                continue
            try:
                # Decode base64 BEFORE storage
                decoded = base64.b64decode(b64_value).decode("utf-8")
                payload = json.loads(decoded)
                posts.append(payload)
            except Exception as e:
                print(f"Failed to decode Kafka record: {e}")
                continue
    return posts


def get_mongo_collection(env_vars: Dict[str, str]):
    """
    Returns pymongo collection object after validating required environment variables.
    """
    required_vars = {
        "EPA_MONGODB_USERNAME": env_vars.get("EPA_MONGODB_USERNAME"),
        "EPA_MONGODB_PASSWORD": env_vars.get("EPA_MONGODB_PASSWORD"),
        "EPA_MONGODB_HOSTNAME": env_vars.get("EPA_MONGODB_HOSTNAME"),
        "EPA_MONGODB_PORT": env_vars.get("EPA_MONGODB_PORT"),
        "EPA_MONGODB_DATABASE_NAME": env_vars.get("EPA_MONGODB_DATABASE_NAME"),
        "EPA_MONGODB_POSTS_COLLECTION": env_vars.get("EPA_MONGODB_POSTS_COLLECTION")
    }

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Got values: {{{', '.join(f'{k}: {v[:3]}***' if v else f'{k}: <empty>' for k, v in required_vars.items())}}}"
        )

    mongo_uri = env_vars["EPA_MONGO_URI"]
    mongo_db = env_vars["EPA_MONGODB_DATABASE_NAME"]
    mongo_collection = env_vars["EPA_MONGODB_POSTS_COLLECTION"]

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client[mongo_db]
    return db[mongo_collection]


def ingest_posts(records: List[Dict[str, Any]], env_vars: Dict[str, str]) -> int:
    """
    Inserts decoded post records into MongoDB.
    CRITICAL: Records MUST be decoded BEFORE reaching this function.
    Returns count of successfully inserted documents.
    """
    if not records:
        return 0

    collection = get_mongo_collection(env_vars)
    inserted = 0

    for post in records:
        post_id = post.get("post_id")
        if not post_id:
            print(f"Skipping record without post_id: {post}")
            continue

        try:
            # CRITICAL: Store DECODED JSON objects (not base64 strings)
            result = collection.insert_one(post)
            if result.acknowledged and result.inserted_id:
                inserted += 1
        except Exception as e:
            print(f"Failed to insert post {post_id}: {e}")
            continue

    return inserted