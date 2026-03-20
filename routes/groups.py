"""
Group/Community routes — groups, create, join, detail, announcements, share/upload resources
"""

import os
import uuid
import re
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from utils.helpers import allowed_file, generate_group_code

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups")
@login_required
def groups():
    from app import db

    # Get all groups
    if current_user.role == "Student":
        all_groups = list(db.groups.find({"members": ObjectId(current_user.id)}).sort("created_at", -1))
    else:
        all_groups = list(db.groups.find().sort("created_at", -1))

    # Get user's joined groups
    user_groups = list(db.groups.find({"members": ObjectId(current_user.id)}))

    return render_template("groups.html", groups=all_groups, user_groups=user_groups)


@groups_bp.route("/circles_plus", methods=["GET", "POST"])
@login_required
def circles_plus():
    from app import db

    if current_user.role not in ["Teacher", "admin"]:
        flash("Only teachers and admins can access Circles++")
        return redirect(url_for("groups.groups"))

    # Get circles created by the teacher
    user_circles = list(db.groups.find({"created_by": ObjectId(current_user.id)}))

    if request.method == "POST":
        group_ids = request.form.getlist("group_ids")
        action = request.form.get("action")

        if not group_ids:
            flash("Please select at least one circle.")
            return redirect(url_for("groups.circles_plus"))

        if action == "announce":
            title = request.form.get("announcement_title")
            content = request.form.get("announcement_content")

            if not title or not content:
                flash("Announcement title and content are required.")
                return redirect(url_for("groups.circles_plus"))

            for gid in group_ids:
                db.group_announcements.insert_one({
                    "group_id": ObjectId(gid),
                    "user_id": ObjectId(current_user.id),
                    "author_name": current_user.name,
                    "author_role": current_user.role,
                    "title": title,
                    "content": content,
                    "timestamp": datetime.utcnow()
                })
            
            flash(f"📢 Broadcast successful! Announcement posted to {len(group_ids)} circles.")

        elif action == "upload":
            title = request.form.get("resource_title")
            subject = request.form.get("resource_subject")
            file = request.files.get("file")

            if not title or not subject or not file or file.filename == "":
                flash("Resource title, subject, and file are required.")
                return redirect(url_for("groups.circles_plus"))

            if allowed_file(file.filename):
                original_name = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + original_name
                filepath = os.path.join("static/uploads", unique_name)
                file.save(filepath)

                # Create the resource
                result = db.resources.insert_one({
                    "user_id": ObjectId(current_user.id),
                    "title": title,
                    "subject": subject,
                    "semester": "Mixed",
                    "resource_type": "Multi-Circle Reference",
                    "year_batch": "General",
                    "tags": ["CirclesPlus"],
                    "description": f"Shared via Circles++ to {len(group_ids)} circles.",
                    "file_path": filepath,
                    "privacy": "private", # Private to the circles
                    "college": current_user.college,
                    "created_at": datetime.utcnow(),
                    "avg_rating": 0,
                    "download_count": 0
                })

                resource_id = result.inserted_id

                # Add resource to all selected groups
                for gid in group_ids:
                    db.groups.update_one(
                        {"_id": ObjectId(gid)},
                        {"$push": {"resources": resource_id}}
                    )
                
                flash(f"📂 Broadcast successful! Resource uploaded to {len(group_ids)} circles.")
            else:
                flash("Invalid file type.")

        return redirect(url_for("groups.circles_plus"))

    return render_template("circles_plus.html", user_circles=user_circles)


@groups_bp.route("/create_group", methods=["GET", "POST"])
@login_required
def create_group():
    from app import db

    # Only teachers can create groups
    if current_user.role not in ["Teacher", "admin"]:
        flash("Only teachers can create groups")
        return redirect(url_for("groups.groups"))

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        group_code = request.form["group_code"].strip().upper()

        # Strict Format Validation (AAAA-0000)
        if not re.match(r'^[A-Z]{4}-\d{4}$', group_code):
            flash("Error: Invalid code format. Please use 'AAAA-0000' (e.g., MATH-1234).")
            return redirect(url_for("groups.create_group"))

        # Validate unique group code
        if db.groups.find_one({"group_code": group_code}):
            flash(f"Error: The circle code '{group_code}' is already assigned. Please choose another.")
            return redirect(url_for("groups.create_group"))

        group_data = {
            "name": name,
            "description": description,
            "group_code": group_code,
            "created_by": ObjectId(current_user.id),
            "creator_name": current_user.name,
            "created_at": datetime.utcnow(),
            "members": [ObjectId(current_user.id)], # Creator is the first member
            "resources": []
        }

        db.groups.insert_one(group_data)

        # Log activity
        db.activities.insert_one({
            "user_id": ObjectId(current_user.id),
            "user_name": current_user.name,
            "action": "created_group",
            "details": {"group_name": name, "group_code": group_code},
            "timestamp": datetime.utcnow()
        })

        flash(f"Group created successfully! Group Code: {group_code}")
        return redirect(url_for("groups.groups"))

    return render_template("create_group.html")


@groups_bp.route("/join_group", methods=["GET", "POST"])
@login_required
def join_group():
    from app import db

    if request.method == "POST":
        search_query = request.form["search"]
        escaped_search = re.escape(search_query)

        # Search by group name or code
        group = db.groups.find_one({
            "$or": [
                {"group_code": search_query.upper()},
                {"name": {"$regex": escaped_search, "$options": "i"}}
            ]
        })

        if not group:
            flash("Group not found")
            return redirect(url_for("groups.join_group"))

        # Check if already a member
        if ObjectId(current_user.id) in group.get("members", []):
            flash("You are already a member of this group")
            return redirect(url_for("groups.group_detail", group_id=str(group["_id"])))

        # Add user to group
        db.groups.update_one(
            {"_id": group["_id"]},
            {"$push": {"members": ObjectId(current_user.id)}}
        )

        # Log activity
        db.activities.insert_one({
            "user_id": ObjectId(current_user.id),
            "user_name": current_user.name,
            "action": "joined_group",
            "details": {"group_name": group["name"]},
            "timestamp": datetime.utcnow()
        })

        flash(f"Successfully joined {group['name']}")
        return redirect(url_for("groups.group_detail", group_id=str(group["_id"])))

    return render_template("join_group.html")


@groups_bp.route("/group/<group_id>")
@login_required
def group_detail(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    # Get member details
    members = list(db.users.find({"_id": {"$in": group.get("members", [])}}))

    # Get group resources
    resources = list(db.resources.find({"_id": {"$in": group.get("resources", [])}}))

    # Get group announcements
    announcements = list(db.group_announcements.find({"group_id": ObjectId(group_id)}).sort("timestamp", -1))

    # Get group messages
    messages = list(db.group_messages.find({"group_id": ObjectId(group_id)}).sort("timestamp", 1))

    # Check if user is a member, creator, or admin
    is_member = (ObjectId(current_user.id) in group.get("members", [])) or (current_user.role == 'admin')
    is_creator = str(group.get("created_by")) == current_user.id

    # Get user's own resources for sharing dropdown (only for teachers/admins)
    my_resources = []
    if current_user.role in ["Teacher", "admin"] and (is_member or is_creator):
        my_resources = list(db.resources.find({"user_id": ObjectId(current_user.id)}).sort("created_at", -1))

    return render_template("group_detail.html", group=group, members=members, resources=resources, announcements=announcements, messages=messages, is_member=is_member, is_creator=is_creator, my_resources=my_resources)


@groups_bp.route("/group/<group_id>/announce", methods=["POST"])
@login_required
def post_announcement(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    # Only teachers and admins can post announcements
    if current_user.role not in ["Teacher", "admin"]:
        flash("Only teachers and admins can post announcements")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Membership check
    if ObjectId(current_user.id) not in group.get("members", []):
        flash("Error: You must be a member of this circle to post announcements.")
        return redirect(url_for("groups.groups"))

    title = request.form["title"]
    content = request.form["content"]

    db.group_announcements.insert_one({
        "group_id": ObjectId(group_id),
        "user_id": ObjectId(current_user.id),
        "author_name": current_user.name,
        "author_role": current_user.role,
        "title": title,
        "content": content,
        "timestamp": datetime.utcnow()
    })

    # Log activity
    db.activities.insert_one({
        "user_id": ObjectId(current_user.id),
        "user_name": current_user.name,
        "action": "posted_announcement",
        "details": {"group_name": group["name"], "announcement_title": title},
        "timestamp": datetime.utcnow()
    })

    flash("📢 Announcement posted successfully!")
    return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/group/<group_id>/message", methods=["POST"])
@login_required
def post_message(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    # Membership check for any message post
    if ObjectId(current_user.id) not in group.get("members", []):
        flash("Error: You must be a member of this circle to send messages.")
        return redirect(url_for("groups.groups"))

    message_content = request.form.get("message")
    
    if not message_content or not message_content.strip():
        flash("Announcement cannot be empty.")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    attachment_path = None
    attachment_name = None

    # Handle file attachment (Only for Teachers/Admins)
    if "file" in request.files and current_user.role in ["Teacher", "admin"]:
        file = request.files["file"]
        if file and file.filename != "":
            if allowed_file(file.filename):
                original_name = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + original_name
                # Ensure directory exists
                upload_folder = "static/uploads/groups"
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, unique_name).replace("\\", "/")
                file.save(filepath)
                attachment_path = filepath
                attachment_name = original_name
            else:
                flash("Invalid file type. Supported: PDF, Word, Excel, PPT, Images.")

    db.group_messages.insert_one({
        "group_id": ObjectId(group_id),
        "sender_id": ObjectId(current_user.id),
        "sender_name": current_user.name,
        "content": message_content.strip(),
        "attachment_path": attachment_path,
        "attachment_name": attachment_name,
        "timestamp": datetime.utcnow()
    })
    
    flash("💬 Announcement posted to the circle!")
    return redirect(url_for("groups.group_detail", group_id=group_id))

@groups_bp.route("/group/<group_id>/share_resource", methods=["POST"])
@login_required
def share_resource_to_group(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    # Only teachers and admins can share resources
    if current_user.role not in ["Teacher", "admin"]:
        flash("Only teachers and admins can share resources to groups")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Membership check
    if ObjectId(current_user.id) not in group.get("members", []):
        flash("Error: You must be a member of this circle to share resources.")
        return redirect(url_for("groups.groups"))

    resource_id = request.form["resource_id"]

    # Check if resource already shared
    if ObjectId(resource_id) in group.get("resources", []):
        flash("This resource is already shared in this group")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Add resource to group
    db.groups.update_one(
        {"_id": ObjectId(group_id)},
        {"$push": {"resources": ObjectId(resource_id)}}
    )

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})
    flash(f"📂 Resource '{resource['title']}' shared to group!")
    return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/group/<group_id>/delete_announcement/<ann_id>")
@login_required
def delete_circle_announcement(group_id, ann_id):
    from app import db
    if current_user.role != "admin":
        flash("Unauthorized deletion attempt.")
        return redirect(url_for("groups.group_detail", group_id=group_id))
    
    db.group_announcements.delete_one({"_id": ObjectId(ann_id)})
    flash("Announcement permanently purged.")
    return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/group/<group_id>/upload_resource", methods=["POST"])
@login_required
def upload_to_group(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    if current_user.role not in ["Teacher", "admin"]:
        flash("Only teachers and admins can upload resources to groups")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Membership check
    if ObjectId(current_user.id) not in group.get("members", []):
        flash("Error: You must be a member of this circle to upload files.")
        return redirect(url_for("groups.groups"))

    title = request.form["title"]
    subject = request.form["subject"]
    description = request.form.get("description", "")
    file = request.files["file"]

    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        unique_name = str(uuid.uuid4()) + "_" + original_name
        filepath = os.path.join("static/uploads", unique_name)
        file.save(filepath)

        # Create the resource
        result = db.resources.insert_one({
            "user_id": ObjectId(current_user.id),
            "title": title,
            "subject": subject,
            "semester": "",
            "resource_type": "Study Material",
            "year_batch": "",
            "tags": [],
            "description": description,
            "file_path": filepath,
            "privacy": "public",
            "college": current_user.college,
            "created_at": datetime.utcnow(),
            "avg_rating": 0,
            "download_count": 0
        })

        # Add resource to group automatically
        db.groups.update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"resources": result.inserted_id}}
        )

        flash(f"📂 File '{title}' uploaded and shared to group!")
    else:
        flash("Invalid file type")

    return redirect(url_for("groups.group_detail", group_id=group_id))


@groups_bp.route("/group/<group_id>/remove/<member_id>")
@login_required
def remove_member(group_id, member_id):
    from app import db
    
    group = db.groups.find_one({"_id": ObjectId(group_id)})
    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))
        
    # Security check: only creator can remove members
    if str(group.get("created_by")) != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for("groups.group_detail", group_id=group_id))
        
    # Prevent self-removal
    if member_id == current_user.id:
        flash("Creators cannot remove themselves from their own circle.")
        return redirect(url_for("groups.group_detail", group_id=group_id))
        
    # Remove from members list
    db.groups.update_one(
        {"_id": ObjectId(group_id)},
        {"$pull": {"members": ObjectId(member_id)}}
    )
    
    flash("Successfully removed member.")
    return redirect(url_for("groups.group_detail", group_id=group_id))

@groups_bp.route("/join_group_direct/<group_id>")
@login_required
def join_group_direct(group_id):
    from app import db

    group = db.groups.find_one({"_id": ObjectId(group_id)})

    if not group:
        flash("Group not found")
        return redirect(url_for("groups.groups"))

    # Check if already a member
    if ObjectId(current_user.id) in group.get("members", []):
        flash("You are already a member of this group")
        return redirect(url_for("groups.group_detail", group_id=group_id))

    # Add user to group
    db.groups.update_one(
        {"_id": group["_id"]},
        {"$push": {"members": ObjectId(current_user.id)}}
    )

    # Log activity
    db.activities.insert_one({
        "user_id": ObjectId(current_user.id),
        "user_name": current_user.name,
        "action": "joined_group",
        "details": {"group_name": group["name"]},
        "timestamp": datetime.utcnow()
    })

    flash(f"✅ Successfully joined {group['name']}!")
    return redirect(url_for("groups.group_detail", group_id=group_id))
