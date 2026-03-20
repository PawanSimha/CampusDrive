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

# Generate the hash for 'password123'
new_password = "password123"
hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")

# Update all users in the database
result = db.users.update_many(
    {}, 
    {"$set": {"password": hashed_pw}}
)

print(f"Success! {result.modified_count} user accounts have been updated.")
print("All users can now log in using the password: password123")
