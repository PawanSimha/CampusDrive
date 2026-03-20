import sys
import os
import time
from flask import Flask
from pymongo import MongoClient
import certifi
from flask_bcrypt import Bcrypt
from config import Config
from bson.objectid import ObjectId

# Setup app context
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

client = MongoClient(app.config["MONGO_URI"], tlsCAFile=certifi.where())
db = client.get_database()

hashed_pw = bcrypt.generate_password_hash('admin123').decode("utf-8")
admin_email = "admin_test_auto@example.com"

# Ensure test admin exists
db.users.update_one(
    {"email": admin_email},
    {"$set": {
        "name": "Playwright Admin",
        "password": hashed_pw,
        "role": "admin",
        "status": "approved"
    }},
    upsert=True
)
print("Test admin secured in DB.")

# Run Playwright tests
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    BASE_URL = 'http://127.0.0.1:5001'

    print("1. Testing Admin Login Flow...")
    page.goto(f'{BASE_URL}/login', wait_until='domcontentloaded')
    page.fill('input[name="email"]', admin_email)
    page.fill('input[name="password"]', 'admin123')
    page.click('button[type="submit"]')
    try:
        page.wait_for_url(f'{BASE_URL}/dashboard', wait_until='domcontentloaded', timeout=10000)
        print("SUCCESS: Admin logged in and redirected to Dashboard.")
    except Exception as e:
        print(f"FAIL: Admin login redirect failed. Current URL: {page.url}")
        page.screenshot(path="admin_login_fail.png")
        browser.close()
        sys.exit(1)

    print("2. Verifying ADMIN tag in Header...")
    admin_tag = page.locator('span:has-text("ADMIN")')
    if admin_tag.count() == 0:
        print("FAIL: ADMIN tag not found in header.")
        browser.close()
        sys.exit(1)
    print("SUCCESS: ADMIN tag is visible.")

    print("3. Testing Admin Hub Access...")
    page.goto(f'{BASE_URL}/admin/database')
    page.wait_for_url(f'{BASE_URL}/admin/database', wait_until='domcontentloaded', timeout=10000)
    if page.locator('h1:has-text("Database.")').count() == 0:
        print("FAIL: Could not access Admin Hub (Database).")
        browser.close()
        sys.exit(1)
    print("SUCCESS: Admin Hub (Database view) accessible.")

    print("4. Testing Approvals View Access...")
    page.goto(f'{BASE_URL}/admin/approvals')
    page.wait_for_url(f'{BASE_URL}/admin/approvals', wait_until='domcontentloaded', timeout=10000)
    if page.locator('h1:has-text("Approvals.")').count() == 0:
        print("FAIL: Could not access Admin Hub (Approvals).")
        browser.close()
        sys.exit(1)
    print("SUCCESS: Admin Hub (Approvals view) accessible.")

    # Cleanup
    print("Cleaning up admin test data...")
    db.users.delete_one({"email": admin_email})
    
    browser.close()
    print("All admin flows verified successfully!")
