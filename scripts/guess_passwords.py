import sys
from flask import Flask
from pymongo import MongoClient
import certifi
from flask_bcrypt import Bcrypt
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

client = MongoClient(app.config["MONGO_URI"], tlsCAFile=certifi.where())
db = client.get_database()

users = db.users.find()

common_passwords = [
    "password", "password123", "123456", "12345678", "admin", "admin123", 
    "teacher", "teacher123", "student", "student123", "Pawan123", "yamuna",
    "PawanSimha", "PawanSimha@gmail.com", "test"
]

print("Attempting to identify plaintext passwords...")
for u in users:
    email = u.get("email")
    hashed = u.get("password", "")
    if not hashed:
        continue
    
    found = False
    name = u.get("name", "").split()[0].lower()
    email_prefix = email.split("@")[0] if email else ""
    local_dict = common_passwords + [name, name+"123", email, email_prefix, email_prefix+"123"]
    
    for pwd in local_dict:
        try:
            if bcrypt.check_password_hash(hashed, pwd):
                print(f"[{u.get('role')}] {email} -> Password: {pwd}")
                found = True
                break
        except Exception:
            pass
    if not found:
        print(f"[{u.get('role')}] {email} -> (Hash could not be easily reversed)")
