"""
Sample Resources Seeding Script for CampusConnect App
Creates 10 sample resources across 5 subjects
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pymongo import MongoClient
from config import Config
from datetime import datetime
from bson.objectid import ObjectId
import uuid

# Initialize
client = MongoClient(Config.MONGO_URI)
db = client.get_database()

def create_dummy_file(filename):
    """Create a dummy PDF file"""
    filepath = os.path.join("static/uploads", filename)
    os.makedirs("static/uploads", exist_ok=True)
    with open(filepath, "w") as f:
        f.write(f"Sample content for {filename}")
    return filepath

def seed_resources():
    """Seed the database with 10 sample resources across 5 subjects"""
    
    print("🌱 Starting resource seeding process...")
    
    # Get a teacher user to assign as uploader
    teacher = db.users.find_one({"role": "Teacher"})
    if not teacher:
        print("❌ No teacher found. Please run seed_users.py first.")
        return
    
    resources_data = [
        # Mathematics (2 resources)
        {
            "title": "Calculus Notes - Differentiation & Integration",
            "subject": "Mathematics",
            "semester": "3",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["calculus", "differentiation", "integration"],
            "description": "Comprehensive notes covering differentiation and integration with solved examples.",
            "privacy": "public",
            "branch": "CSE"
        },
        {
            "title": "Linear Algebra - Matrices and Determinants",
            "subject": "Mathematics",
            "semester": "2",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["linear algebra", "matrices", "determinants"],
            "description": "Complete guide to matrices, determinants, and their applications.",
            "privacy": "public",
            "branch": "ISE"
        },
        
        # Physics (2 resources)
        {
            "title": "Mechanics - Laws of Motion",
            "subject": "Physics",
            "semester": "1",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["mechanics", "newton", "motion"],
            "description": "Detailed notes on Newton's laws of motion with practical examples.",
            "privacy": "public",
            "branch": "MECH"
        },
        {
            "title": "Thermodynamics - Heat and Energy",
            "subject": "Physics",
            "semester": "2",
            "resource_type": "Question Papers",
            "year_batch": "2023",
            "tags": ["thermodynamics", "heat", "energy"],
            "description": "Previous year question papers on thermodynamics.",
            "privacy": "public",
            "branch": "ECE"
        },
        
        # Computer Science (2 resources)
        {
            "title": "Data Structures - Trees and Graphs",
            "subject": "Computer Science",
            "semester": "3",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["data structures", "trees", "graphs"],
            "description": "In-depth coverage of tree and graph data structures with implementations.",
            "privacy": "public",
            "branch": "CSE"
        },
        {
            "title": "Algorithms - Sorting and Searching",
            "subject": "Computer Science",
            "semester": "4",
            "resource_type": "Solutions",
            "year_batch": "2024",
            "tags": ["algorithms", "sorting", "searching"],
            "description": "Solutions to common sorting and searching algorithm problems.",
            "privacy": "public",
            "branch": "ISE"
        },
        
        # Chemistry (2 resources)
        {
            "title": "Organic Chemistry - Hydrocarbons",
            "subject": "Chemistry",
            "semester": "1",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["organic chemistry", "hydrocarbons"],
            "description": "Complete notes on hydrocarbons and their reactions.",
            "privacy": "public",
            "branch": "CIVIL"
        },
        {
            "title": "Inorganic Chemistry - Periodic Table",
            "subject": "Chemistry",
            "semester": "1",
            "resource_type": "Study Material",
            "year_batch": "2024",
            "tags": ["inorganic chemistry", "periodic table"],
            "description": "Study material covering periodic table trends and properties.",
            "privacy": "public",
            "branch": "ECE"
        },
        
        # English (2 resources)
        {
            "title": "English Grammar - Tenses and Voice",
            "subject": "English",
            "semester": "1",
            "resource_type": "Notes",
            "year_batch": "2024",
            "tags": ["grammar", "tenses", "voice"],
            "description": "Comprehensive guide to English grammar focusing on tenses and voice.",
            "privacy": "public",
            "branch": "CSE"
        },
        {
            "title": "English Literature - Shakespeare's Works",
            "subject": "English",
            "semester": "2",
            "resource_type": "Study Material",
            "year_batch": "2024",
            "tags": ["literature", "shakespeare"],
            "description": "Analysis of Shakespeare's major works and themes.",
            "privacy": "public",
            "branch": "ISE"
        }
    ]
    
    for resource_data in resources_data:
        # Check if resource already exists
        existing = db.resources.find_one({"title": resource_data["title"]})
        if existing:
            print(f"✓ Resource already exists: {resource_data['title']}")
            continue
        
        # Create dummy file
        unique_name = str(uuid.uuid4()) + "_sample.pdf"
        filepath = create_dummy_file(unique_name)
        
        # Add resource to database
        resource_data.update({
            "user_id": teacher["_id"],
            "file_path": filepath,
            "college": teacher["college"],
            "created_at": datetime.utcnow(),
            "avg_rating": round(3 + (hash(resource_data["title"]) % 20) / 10, 1),  # Random rating 3.0-5.0
            "download_count": hash(resource_data["title"]) % 50  # Random downloads 0-49
        })
        
        db.resources.insert_one(resource_data)
        print(f"✅ Created Resource: {resource_data['title']} ({resource_data['subject']})")
    
    print("\n🎉 Resource seeding completed!")
    print(f"\n📋 Summary:")
    print(f"   - Mathematics: 2 resources")
    print(f"   - Physics: 2 resources")
    print(f"   - Computer Science: 2 resources")
    print(f"   - Chemistry: 2 resources")
    print(f"   - English: 2 resources")
    print(f"   Total: 10 resources")

if __name__ == "__main__":
    seed_resources()
