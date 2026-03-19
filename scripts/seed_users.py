"""
Database Seeding Script for CampusConnect App
Creates hardcoded admin, teacher, and student accounts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from config import Config
from dotenv import load_dotenv

load_dotenv()

# Initialize
bcrypt = Bcrypt()
client = MongoClient(Config.MONGO_URI)
db = client.get_database()

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.generate_password_hash(password).decode("utf-8")

def seed_users():
    """Seed the database with predefined users"""
    
    print("🌱 Starting user seeding process...")
    
    # 1. HARDCODED ADMIN
    admin_data = {
        "name": "Pawan Simha",
        "email": "PawanSimha@gmail.com",
        "password": hash_password("pawansimha@123"),
        "college": "Ramaiah Institute of Technology",
        "branch": "CSE",
        "semester": "8",
        "role": "admin"
    }
    
    if db.users.find_one({"email": admin_data["email"]}):
        print(f"✓ Admin already exists: {admin_data['email']}")
    else:
        db.users.insert_one(admin_data)
        print(f"✅ Created Admin: {admin_data['email']}")
    
    # 2. TEACHER ACCOUNTS
    teachers = [
        {"name": "Yamuna", "email": "yamuna@teacher.com"},
        {"name": "Sushma", "email": "sushma@teacher.com"},
        {"name": "Sushmitha", "email": "sushmitha@teacher.com"},
        {"name": "Bhoomika", "email": "bhoomika@teacher.com"},
        {"name": "Harish", "email": "harish@teacher.com"}
    ]
    
    for teacher in teachers:
        teacher_data = {
            "name": teacher["name"],
            "email": teacher["email"],
            "password": hash_password("teacher@123"),  # Common password for all teachers
            "college": "Ramaiah Institute of Technology",
            "branch": "Faculty",
            "semester": "N/A",
            "role": "Teacher"
        }
        
        if db.users.find_one({"email": teacher_data["email"]}):
            print(f"✓ Teacher already exists: {teacher_data['email']}")
        else:
            db.users.insert_one(teacher_data)
            print(f"✅ Created Teacher: {teacher_data['name']} ({teacher_data['email']})")
    
    # 3. STUDENT ACCOUNTS (30 students)
    branches = ["CSE", "ISE", "ECE", "MECH", "CIVIL"]
    semesters = ["1", "2", "3", "4", "5", "6", "7", "8"]
    
    for i in range(1, 31):
        student_data = {
            "name": f"Student - {i}",
            "email": f"student{i}@student.com",
            "password": hash_password(f"Student{i}@123"),
            "college": "Ramaiah Institute of Technology",
            "branch": branches[i % len(branches)],  # Distribute across branches
            "semester": semesters[i % len(semesters)],  # Distribute across semesters
            "role": "Student"
        }
        
        if db.users.find_one({"email": student_data["email"]}):
            print(f"✓ Student already exists: {student_data['email']}")
        else:
            db.users.insert_one(student_data)
            print(f"✅ Created Student: {student_data['name']} ({student_data['email']})")
    
    print("\n🎉 User seeding completed!")
    print("\n📋 Summary:")
    print(f"   - Admin: 1 account")
    print(f"   - Teachers: 5 accounts")
    print(f"   - Students: 30 accounts")
    print("\n🔑 Login Credentials:")
    print(f"   Admin: PawanSimha@gmail.com / pawansimha@123")
    print(f"   Teachers: <name>@teacher.com / teacher@123")
    print(f"   Students: student<N>@student.com / Student<N>@123")

if __name__ == "__main__":
    seed_users()
