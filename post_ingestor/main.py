import os

def lambda_handler(event, context):
    """
    Expects:
      event = {
        "event": "INGEST_POSTS",
        "records": [ {...}, {...} ]
      }
    """
    # FILL WITH REAL VALUES LATER
    env_vars = []
    env_vars["KAFKA_TOKEN"] =  os.getenv("KAFKA_TOKEN", "KAFKA_TOKEN")
    env_vars["MONGO_SECRET"] =  os.getenv("MONGO_SECRET", "MONGO_SECRET")
    env_vars["MONGO_URI"] =  os.getenv("MONGO_URI", "MONGO_URI")
    env_vars["MONGO_DB"] =  os.getenv("MONGO_DB", "MONGO_DB")
    env_vars["MONGO_COLLECTION"] =  os.getenv("MONGO_COLLECTION", "posts")

    if event.get("event") != "INGEST_POSTS":
        return {"statusCode": 400, "body": "Unsupported event type"}

    records = event.get("records") or []
    inserted = ingest_posts(records, env_vars)

    return {"statusCode": 200, "body": {"inserted": inserted}}


def ingest_posts(records, env_vars):
    """
    Takes list of post records and inserts them into MongoDB.
    Skeleton only until env setup.

    env_vars = ["KAFKA_TOKEN", "MONGO_SECRET", "MONGO_URI", "MONGO_DB", "MONGO_COLLECTION"]
    
    Example:

    env_vars[KAFKA_TOKEN] = "123456789"
    print(env_vars[KAFKA_TOKEN]) = 123456789
    
    """

    if not records:
        return 0

    # --- MongoDB client placeholder ---
    # Example (fill later):
    # from pymongo import MongoClient
    # client = MongoClient(MONGO_URI, tls=True, authMechanism="...")
    # collection = client[MONGO_DB][MONGO_COLLECTION]

    inserted = 0
    for post in records:
        inserted += 1
    return inserted
