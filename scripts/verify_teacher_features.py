import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import certifi

# Load environment variables
load_dotenv()

# Configuration (Mocking app context)
# MONGO_URI now read from environment
MONGO_URI = os.environ.get("MONGO_URI")

def verify():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.get_database() # Gets webcrawlers_db from URI
    
    # 1. Test Public Announcement
    teacher = db.users.find_one({"role": "Teacher"})
    if not teacher:
        print("[FAIL] No teacher found in database.")
        # Try finding any user to see if connection is ok
        any_user = db.users.find_one()
        if any_user:
            print(f"[INFO] Found a user but not a teacher. Role: {any_user.get('role')}")
        else:
            print("[FAIL] No users found in 'users' collection.")
        return

    print(f"[SUCCESS] Testing with teacher: {teacher['name']}")

    # Insert a mock public announcement
    announcement_data = {
        "user_id": teacher["_id"],
        "author_name": teacher["name"],
        "author_role": teacher["role"],
        "title": "Automated Test Announcement",
        "content": "This is a test announcement.",
        "subject": "Testing",
        "timestamp": datetime.utcnow()
    }
    db.public_announcements.insert_one(announcement_data)
    print("[SUCCESS] Public announcement inserted successfully.")

    # 2. Test Multi-Circle Action (Circles++)
    # Find circles created by this teacher
    circles = list(db.groups.find({"created_by": teacher["_id"]}).limit(2))
    if len(circles) < 1:
        print(f"[WARNING] Teacher {teacher['name']} has no circles. Creating one for testing...")
        group_data = {
            "name": "Test Circle",
            "group_code": "TEST-1234",
            "created_by": teacher["_id"],
            "created_at": datetime.utcnow(),
            "members": [teacher["_id"]],
            "resources": []
        }
        db.groups.insert_one(group_data)
        circles = list(db.groups.find({"created_by": teacher["_id"]}).limit(2))

    group_ids = [c["_id"] for c in circles]
    
    # Mock upload resource to multiple circles
    resource_data = {
        "user_id": teacher["_id"],
        "title": "Circles++ Test Resource",
        "subject": "Automation",
        "semester": "Mixed",
        "resource_type": "Multi-Circle Reference",
        "year_batch": "General",
        "tags": ["CirclesPlus"],
        "description": "Shared via Circles++ to multiple circles.",
        "file_path": "static/uploads/test.pdf",
        "privacy": "private",
        "college": teacher.get("college", "Unknown"),
        "created_at": datetime.utcnow(),
        "avg_rating": 0,
        "download_count": 0
    }
    res_result = db.resources.insert_one(resource_data)
    res_id = res_result.inserted_id

    for gid in group_ids:
        db.groups.update_one({"_id": gid}, {"$push": {"resources": res_id}})
    
    print(f"[SUCCESS] Resource shared with {len(group_ids)} circles via Circles++ simulation.")

if __name__ == "__main__":
    verify()
