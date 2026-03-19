import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import certifi

# Configuration (Mocking app context)
MONGO_URI = "mongodb+srv://webcrawler_user:WebCrawler%40123@cluster0.ldwgs0e.mongodb.net/webcrawlers_db?retryWrites=true&w=majority"

def verify():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database()
    
    # 1. Ensure we have an announcement to pin
    ann = db.public_announcements.find_one()
    if not ann:
        print("[INFO] No announcement found, creating one...")
        db.public_announcements.insert_one({
            "title": "Pin Test Announcement",
            "content": "This is a test for pinning.",
            "timestamp": datetime.utcnow(),
            "author_name": "Admin",
            "author_role": "admin"
        })
        ann = db.public_announcements.find_one({"title": "Pin Test Announcement"})

    print(f"[INFO] Using announcement: {ann['title']} (Pinned Status: {ann.get('is_pinned', False)})")
    
    # 2. Toggle Pin Status
    new_status = not ann.get("is_pinned", False)
    db.public_announcements.update_one(
        {"_id": ann["_id"]},
        {"$set": {"is_pinned": new_status}}
    )
    print(f"[SUCCESS] Announcement toggled to: {'Pinned' if new_status else 'Unpinned'}")

    # 3. Verify Sort Logic
    # Insert another unpinned announcement
    db.public_announcements.insert_one({
        "title": "Fresh Unpinned Announcement",
        "content": "Should appear below pinned one.",
        "timestamp": datetime.utcnow(),
        "is_pinned": False
    })

    sorted_list = list(db.public_announcements.find().sort([("is_pinned", -1), ("timestamp", -1)]))
    
    if sorted_list[0]["is_pinned"] == True:
        print("[SUCCESS] Sorting logic verified: Pinned announcement is at the top.")
    else:
        print("[FAIL] Pinned announcement is NOT at the top.")

if __name__ == "__main__":
    verify()
