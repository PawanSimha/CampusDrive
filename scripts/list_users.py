import sys
import os
from flask import Flask
from pymongo import MongoClient
import certifi
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"], tlsCAFile=certifi.where())
db = client.get_database()

users = db.users.find()
print("List of Users in the Database:\n" + "-"*50)
for u in users:
    print(f"[{u.get('role', 'Unknown Role')}] Name: {u.get('name')}, Email: {u.get('email')}, Status: {u.get('status', 'N/A')}")
