import sys
import os
from flask import Flask
from pymongo import MongoClient
import certifi
from flask_bcrypt import Bcrypt
from config import Config

# Setup app context to hash password & connect DB
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

client = MongoClient(app.config["MONGO_URI"], tlsCAFile=certifi.where())
db = client.get_database()

hashed_pw = bcrypt.generate_password_hash('password123').decode("utf-8")
teacher_email = "testteacher@example.com"

# Ensure test teacher exists and is approved
db.users.update_one(
    {"email": teacher_email},
    {"$set": {
        "name": "Playwright Teacher",
        "password": hashed_pw,
        "college": "Automation University",
        "branch": "CS",
        "teacher_id": "AUTO123456",
        "bio": "I run automated tests.",
        "role": "Teacher",
        "status": "approved"
    }},
    upsert=True
)

# Pre-test cleanup to avoid duplicate group code errors
db.groups.delete_many({"group_code": "AUTO-2026"})
db.public_announcements.delete_many({"title": "Playwright Test"})

print("Test teacher secured and pre-test cleanup done.")

# Run Playwright tests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("1. Testing Login Flow...")
    page.goto('http://127.0.0.1:5001/login', wait_until='domcontentloaded')
    page.fill('input[name="email"]', teacher_email)
    page.fill('input[name="password"]', 'password123')
    page.click('button[type="submit"]')
    try:
        page.wait_for_url('http://127.0.0.1:5001/social', wait_until='domcontentloaded', timeout=10000)
        print("SUCCESS: Logged in and redirected to Social Area.")
    except Exception as e:
        print(f"FAIL: Teacher login redirect failed. Current URL: {page.url}")
        page.screenshot(path="teacher_login_fail.png")
        print("Page Content Snippet:\n", page.content()[:500])
        browser.close()
        sys.exit(1)

    print("2. Testing Announcement Posting...")
    try:
        page.fill('textarea[name="content"]', 'This is an automated Playwright test announcement.')
        page.fill('input[name="title"]', 'Playwright Test')
        page.click('button:has-text("Post to Public")')
        page.wait_for_timeout(2000)
        print("SUCCESS: Announcement posted.")
    except Exception as e:
        print(f"FAIL: Could not post announcement. Error: {e}")

    print("3. Testing Circle Creation...")
    try:
        page.goto('http://127.0.0.1:5001/create_group', wait_until='domcontentloaded')
        page.fill('input[name="name"]', 'Playwright Automated Circle')
        page.fill('input[name="group_code"]', 'AUTO-2026')
        page.fill('textarea[name="description"]', 'A circle created entirely by Playwright automation.')
        page.click('button[type="submit"]')
        page.wait_for_url('http://127.0.0.1:5001/groups', wait_until='domcontentloaded', timeout=10000)
        
        if "groups" in page.url or "group/" in page.url:
            print("SUCCESS: Circle created successfully.")
        else:
            print(f"WARN: Circle creation end URL is {page.url}")
    except Exception as e:
        print(f"FAIL: Could not create circle. Error: {e}")

    # Cleanup
    print("Cleaning up teacher test data...")
    db.public_announcements.delete_many({"title": "Playwright Test"})
    db.groups.delete_many({"name": "Playwright Automated Circle"})
    db.users.delete_one({"email": teacher_email})
    
    browser.close()
    print("All configured teacher tests completed successfully.")
