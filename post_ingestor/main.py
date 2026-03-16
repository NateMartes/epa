import os
import json
import base64
import urllib.parse
from typing import List, Dict, Any
from pymongo import MongoClient


def lambda_handler(event, context):
    """
    Handles:
    1) MSK/Kafka events (base64-encoded values in records dict)
    2) Custom test events with "event": "INGEST_POSTS" (plain JSON records)
    """
    try:
        env_vars = load_env()

        # MSK/Kafka event detection
        if event.get("eventSource") == "aws:kafka" and isinstance(event.get("records"), dict):
            posts = parse_kafka_event(event)
            ingest_posts(posts, env_vars)
            return {"statusCode": 200, "body": json.dumps({"message": "Posts ingested successfully"})}

        # Custom test event detection
        if event.get("event") == "INGEST_POSTS" and isinstance(event.get("records"), list):
            ingest_posts(event["records"], env_vars)
            return {"statusCode": 200, "body": json.dumps({"message": "Posts ingested successfully"})}

        # Unsupported event format
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Unsupported event format",
                "received_eventSource": event.get("eventSource"),
                "has_records_dict": isinstance(event.get("records"), dict),
                "has_event_field": "event" in event
            })
        }
    except Exception as e:
        # CRITICAL: Always return a response, even on error
        print(f"ERROR in lambda_handler: {type(e).__name__}: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }


def load_env() -> Dict[str, str]:
    """Loads all required EPA_* environment variables."""
    username = os.getenv("EPA_MONGODB_USERNAME", "")
    password = os.getenv("EPA_MONGODB_PASSWORD", "")
    hostname = os.getenv("EPA_MONGODB_HOSTNAME", "")
    port = os.getenv("EPA_MONGODB_PORT", "")
    
    # URL-encode credentials to handle special characters in MongoDB URI
    encoded_username = urllib.parse.quote_plus(username)
    encoded_password = urllib.parse.quote_plus(password)
    
    return {
        "EPA_MONGODB_HOSTNAME": hostname,
        "EPA_MONGODB_PORT": port,
        "EPA_MONGODB_USERNAME": username,
        "EPA_MONGODB_PASSWORD": password,
        "EPA_MONGODB_SESSION_TOKEN_COLLECTION": os.getenv("EPA_MONGODB_SESSION_TOKEN_COLLECTION", ""),
        "EPA_MONGODB_DATABASE_NAME": os.getenv("EPA_MONGODB_DATABASE_NAME", ""),
        "EPA_MONGODB_USER_COLLECTION": os.getenv("EPA_MONGODB_USER_COLLECTION", ""),
        "EPA_MONGODB_POSTS_COLLECTION": os.getenv("EPA_MONGODB_POSTS_COLLECTION", ""),
        "EPA_MONGO_URI": f"mongodb://{encoded_username}:{encoded_password}@{hostname}:{port}/?authSource=admin"
    }


def parse_kafka_event(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Decodes base64-encoded Kafka records into JSON objects.
    CRITICAL: All values are decoded BEFORE reaching ingestion logic.
    """
    posts = []
    records = event.get("records", {})
    
    if not isinstance(records, dict):
        print(f"Warning: records field is not a dict (type: {type(records).__name__})")
        return posts

    for topic_partition, record_list in records.items():
        if not isinstance(record_list, list):
            print(f"Warning: records['{topic_partition}'] is not a list")
            continue
            
        for idx, record in enumerate(record_list):
            if not isinstance(record, dict):
                print(f"Warning: records['{topic_partition}'][{idx}] is not a dict")
                continue
                
            b64_value = record.get("value")
            if not b64_value:
                print(f"Warning: records['{topic_partition}'][{idx}] has no 'value' field")
                continue
                
            try:
                # CRITICAL DECODING STEP: base64 → UTF-8 → JSON
                decoded_bytes = base64.b64decode(b64_value)
                decoded_str = decoded_bytes.decode("utf-8")
                payload = json.loads(decoded_str)
                posts.append(payload)
                print(f"Decoded record {idx} from {topic_partition}: post_id={payload.get('post_id')}")
            except Exception as e:
                print(f"Failed to decode record {idx} from {topic_partition}: {e}")
                continue
                
    print(f"Successfully decoded {len(posts)} records from Kafka event")
    return posts


def post_validation(payload: Dict[str, Any]) -> bool:
    """
    Validates post structure before insertion.
    Returns True if valid, False otherwise.
    """
    required_fields = {
        "post_id", "title", "content", "category", 
        "category_slug", "created_at", "created_by"
    }
    
    if not isinstance(payload, dict):
        return False
        
    # Check all required fields exist and are non-empty
    for field in required_fields:
        value = payload.get(field)
        if value is None or value == "":
            print(f"Validation failed: missing/empty field '{field}' in post {payload.get('post_id')}")
            return False
            
    return True


def get_mongo_collection(env_vars: Dict[str, str]):
    """Validates env vars and returns MongoDB collection object."""
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
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    mongo_uri = env_vars["EPA_MONGO_URI"]
    mongo_db = env_vars["EPA_MONGODB_DATABASE_NAME"]
    mongo_collection = env_vars["EPA_MONGODB_POSTS_COLLECTION"]

    client = None
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Trigger connection check
        client.admin.command('ping')
        db = client[mongo_db]
        return db[mongo_collection], client  # Return client so caller can close it
    except Exception as e:
        if client:
            client.close()
        raise ValueError(f"Failed to connect to MongoDB: {e}")


def ingest_posts(records: List[Dict[str, Any]], env_vars: Dict[str, str]) -> int:
    """
    Inserts validated, DECODED post records into MongoDB.
    CRITICAL: Only DECODED JSON objects are stored (never base64 strings).
    """
    if not records:
        print("No records to ingest")
        return 0

    collection = None
    mongo_client = None
    try:
        collection, mongo_client = get_mongo_collection(env_vars)
    except Exception as e:
        print(f"Failed to get MongoDB collection: {e}")
        raise

    try:
        inserted = 0
        for post in records:
            # Validate before insertion (skip invalid records)
            if not post_validation(post):
                print(f"Skipping invalid post: {post.get('post_id')}")
                continue
                
            try:
                result = collection.insert_one(post)
                if result.acknowledged and result.inserted_id:
                    inserted += 1
                    print(f"Inserted post {post.get('post_id')} (MongoDB ID: {result.inserted_id})")
            except Exception as e:
                print(f"Failed to insert post {post.get('post_id')}: {e}")
                continue

        print(f"Ingestion complete: {inserted} of {len(records)} records inserted")
        return inserted
    finally:
        if mongo_client:
            mongo_client.close()