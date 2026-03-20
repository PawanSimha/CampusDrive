import sys
import os
import time
from flask import Flask
from pymongo import MongoClient
import certifi
from flask_bcrypt import Bcrypt
from config import Config
from bson.objectid import ObjectId

# Setup app context to hash password & connect DB
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

client = MongoClient(app.config["MONGO_URI"], tlsCAFile=certifi.where())
db = client.get_database()

hashed_pw = bcrypt.generate_password_hash('password123').decode("utf-8")
student_email = "student_test_auto@example.com"

# Ensure test student exists
db.users.update_one(
    {"email": student_email},
    {"$set": {
        "name": "Playwright Student",
        "password": hashed_pw,
        "college": "Automation University",
        "branch": "CS",
        "role": "Student",
        "favorites": [] # clear favorites for clean test
    }},
    upsert=True
)
print("Test student secured in DB.")

# Ensure there is at least one teacher user
teacher_user = db.users.find_one({"role": "Teacher"})
if not teacher_user:
    print("Need a teacher user to create test content.")
    sys.exit(1)

# Clean up any potential lingering test data from failed runs
db.public_announcements.delete_many({"title": "E2E Student Test Announcement"})
db.resources.delete_many({"title": "E2E Student Test Resource"})

# Create a test announcement
announcement_res = db.public_announcements.insert_one({
    "user_id": ObjectId(teacher_user["_id"]),
    "author_name": teacher_user["name"],
    "author_role": "Teacher",
    "title": "E2E Student Test Announcement",
    "content": "This should be liked by the student.",
    "subject": "Testing",
    "timestamp": __import__('datetime').datetime.utcnow()
})
announcement_id = announcement_res.inserted_id

# Create a test resource
resource_res = db.resources.insert_one({
    "user_id": ObjectId(teacher_user["_id"]),
    "title": "E2E Student Test Resource",
    "subject": "Testing",
    "semester": "1",
    "resource_type": "Notes",
    "year_batch": "2026",
    "tags": ["test"],
    "description": "This should be liked by the student.",
    "file_path": "static/uploads/dummy.pdf",
    "privacy": "public",
    "college": teacher_user.get("college", "Automation University"),
    "created_at": __import__('datetime').datetime.utcnow(),
    "avg_rating": 0,
    "download_count": 0,
    "uploader_name": teacher_user.get("name", "Test Teacher")
})
resource_id = resource_res.inserted_id

print("Test content injected.")

# Run Playwright tests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    BASE_URL = 'http://127.0.0.1:5001'

    print("1. Testing Login Flow...")
    page.goto(f'{BASE_URL}/login', wait_until='domcontentloaded')
    page.fill('input[name="email"]', student_email)
    page.fill('input[name="password"]', 'password123')
    page.click('button[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/social', wait_until='domcontentloaded', timeout=10000)
    
    if "social" not in page.url:
        print(f"FAIL: Expected /social after login, got {page.url}")
        browser.close()
        sys.exit(1)
    print("SUCCESS: Logged in and redirected to Social Area.")

    print("2. Testing Social Area Rendering & Restrictions...")
    if page.locator('button:has-text("Post to Public")').count() > 0:
        print("FAIL: Student can see 'Post to Public' button.")
        browser.close()
        sys.exit(1)
    
    if page.locator('#btn-announcements').count() == 0 or page.locator('#btn-notes').count() == 0:
        print("FAIL: Social tabs are missing.")
        browser.close()
        sys.exit(1)
    print("SUCCESS: UI correctly restricted (cannot post) but tabs are visible.")

    print("3. Testing Liking Functionality on Announcements...")
    ann_like_sel = f'a[href="/toggle_favorite/{announcement_id}"]'
    page.wait_for_selector(ann_like_sel, timeout=5000)
    page.click(ann_like_sel)
    page.wait_for_timeout(2000) # Wait for potential redirect or UI update
    print("SUCCESS: Liked announcement.")

    print("4. Testing Liking Functionality on Resources...")
    page.click('#btn-notes')
    time.sleep(1) # wait for tab animation
    res_like_sel = f'a[href="/toggle_favorite/{resource_id}"]'
    page.wait_for_selector(res_like_sel, timeout=5000)
    page.click(res_like_sel)
    page.wait_for_timeout(2000)
    print("SUCCESS: Liked resource.")

    print("5. Testing Vault Rendering...")
    page.click('a.nav-link:has-text("Vault")')
    page.wait_for_selector('text=E2E Student Test Announcement', timeout=10000)
    
    if page.locator('text=E2E Student Test Announcement').count() == 0:
        print("FAIL: Liked announcement did not appear in Vault.")
        browser.close()
        sys.exit(1)
    if page.locator('text=E2E Student Test Resource').count() == 0:
        print("FAIL: Liked resource did not appear in Vault.")
        browser.close()
        sys.exit(1)
    print("SUCCESS: Both liked items correctly populated the Vault.")

    print("6. Testing Upload Restrictions...")
    page.goto(f'{BASE_URL}/upload')
    page.wait_for_url(f'{BASE_URL}/upload', timeout=10000)
    
    if page.locator('select[name="privacy"]').count() > 0:
        print("FAIL: Privacy dropdown is visible to student.")
        browser.close()
        sys.exit(1)
    print("SUCCESS: Privacy dropdown successfully hidden for student.")

    # Cleanup DB
    print("Cleaning up test data...")
    db.public_announcements.delete_one({"_id": announcement_id})
    db.resources.delete_one({"_id": resource_id})
    db.users.delete_one({"email": student_email})
    
    browser.close()
    print("All student flows verified successfully! ✨")
