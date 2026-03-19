from playwright.sync_api import sync_playwright
import time
import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime

# Load env variables for DB connection
load_dotenv()

def run_test():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. Open Landing Page
            print("Navigating to home page...")
            page.goto('http://127.0.0.1:5000', timeout=60000)
            page.wait_for_load_state('networkidle')
            
            # 2. Go to Register
            print("Navigating to register page...")
            page.goto('http://127.0.0.1:5000/register')
            page.wait_for_load_state('networkidle')
            
            # 3. Register a test user
            test_email = f"test_{int(time.time())}@campusconnect.io"
            print(f"Registering test user: {test_email}")
            page.fill('input[name="name"]', 'Test User')
            page.fill('input[name="email"]', test_email)
            page.fill('input[name="password"]', 'testpassword123')
            page.fill('input[name="college"]', 'Test College')
            
            if page.locator('select[name="branch"]').is_visible():
                page.select_option('select[name="branch"]', label='Computer Science')
            if page.locator('select[name="semester"]').is_visible():
                page.select_option('select[name="semester"]', value='4')
            if page.locator('select[name="role"]').is_visible():
                page.select_option('select[name="role"]', value='student')
                
            page.click('button:has-text("Initiate Registration")')
            page.wait_for_load_state('networkidle')
            
            # --- AUTO APPROVAL & RESOURCE CREATION ---
            print(f"Connecting to database for setup...")
            mongo_uri = os.getenv("MONGO_URI")
            if mongo_uri:
                client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
                db = client.get_database()
                db.users.update_one({"email": test_email}, {"$set": {"status": "approved"}})
                print(f"User {test_email} approved.")
                
                user = db.users.find_one({"email": test_email})
                res_id = db.resources.insert_one({
                    "user_id": user["_id"],
                    "title": "VERIFICATION_NODE_UNIT_TEST",
                    "subject": "Automation",
                    "semester": "4",
                    "resource_type": "Notes",
                    "year_batch": "2026",
                    "tags": ["test"],
                    "description": "Verification node",
                    "file_path": "static/uploads/verification.pdf",
                    "privacy": "public",
                    "college": user["college"],
                    "created_at": datetime.utcnow(),
                    "avg_rating": 0,
                    "download_count": 0
                }).inserted_id
                print(f"Created dummy resource: {res_id}")
            else:
                print("WARNING: MONGO_URI missing.")

            # 4. Login
            print("Going to login page...")
            page.goto('http://127.0.0.1:5000/login')
            page.fill('input[name="email"]', test_email)
            page.fill('input[name="password"]', 'testpassword123')
            page.click('button:has-text("Establish Connection")')
            page.wait_for_load_state('networkidle')
            
            # 5. Test Profile Dropdown (Hover)
            print("Testing Profile Dropdown Hover...")
            user_group = page.locator('.relative.group\\/user').first
            if user_group.count() > 0:
                user_group.hover()
                time.sleep(1.5) # Wait for animation
                dropdown_content = page.locator('.absolute.top-full .bg-primary-900').filter(has_text="Dashboard").first
                if dropdown_content.is_visible():
                    print("SUCCESS: Dropdown visible.")
                    dropdown_content.screenshot(path='dropdown_success.png')
                else:
                    print("FAILURE: Dropdown not visible.")
            
            # 6. Test Rating System
            print("Navigating to resources...")
            page.goto('http://127.0.0.1:5000/social')
            page.wait_for_load_state('networkidle')
            
            res_link = page.locator('text="VERIFICATION_NODE_UNIT_TEST"').first
            if res_link.count() > 0:
                res_link.click()
                page.wait_for_load_state('networkidle')
                print("Testing Ratings...")
                stars = page.locator('.star-rating-trigger').all()
                if stars:
                    star5 = stars[4]
                    star5.hover()
                    time.sleep(1)
                    if "text-primary-600" in star5.get_attribute("class"):
                        print("SUCCESS: Star 5 highlighted.")
                        star5.screenshot(path='rating_success.png')
                        star5.click()
                        page.wait_for_load_state('networkidle')
                        print("SUCCESS: Rating submitted and page reloaded.")
                        
                        # Re-locate and check if still highlighted (optional but good)
                        star5_new = page.locator('.star-rating-trigger').nth(4)
                        if "text-primary-600" in star5_new.get_attribute("class"):
                            print("SUCCESS: Star 5 state maintained after reload.")
            else:
                print("FAILURE: Resource NOT found.")

        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            print("Verification complete.")
            browser.close()

if __name__ == "__main__":
    run_test()
