"""
Admin routes — admin database, approvals, delete users/assets
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from bson.objectid import ObjectId

from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    # Deprecated master route. Redirect to the new Database dashboard.
    return redirect(url_for('admin.admin_database'))


@admin_bp.route("/admin/database")
@login_required
@admin_required
def admin_database():
    from app import db

    # Get users grouped by role
    all_users = list(db.users.find({"role": {"$ne": "admin"}}).sort("created_at", -1))
    
    teachers = [u for u in all_users if u.get("role") == "Teacher"]
    students = [u for u in all_users if u.get("role") == "Student"]

    # Calculate teacher stats dynamically
    teacher_stats = []
    for teacher in teachers:
        uploads = db.resources.count_documents({"user_id": teacher["_id"]})
        groups_created = db.groups.count_documents({"created_by": teacher["_id"]})
        teacher_stats.append({
            "id": teacher["_id"],
            "name": teacher["name"],
            "email": teacher["email"],
            "college": teacher.get("college"),
            "uploads": uploads,
            "groups": groups_created,
            "status": teacher.get("status", "approved")
        })

    # Get all circles (groups)
    all_groups = list(db.groups.find().sort("created_at", -1))

    return render_template("admin_database.html", teacher_stats=teacher_stats, students=students, groups=all_groups)


@admin_bp.route("/admin/approvals")
@login_required
@admin_required
def admin_approvals():
    from app import db

    # Fetch all pending users waiting for admin authorization
    pending_users = list(db.users.find({"status": "pending"}).sort("created_at", -1))

    return render_template("admin_approvals.html", pending_users=pending_users)


@admin_bp.route("/admin/approve_user/<user_id>")
@login_required
@admin_required
def approve_user(user_id):
    from app import db

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": "approved"}}
    )
    flash("✅ User approved successfully")
    return redirect(request.referrer or url_for("admin.admin_approvals"))


@admin_bp.route("/admin/reject_user/<user_id>")
@login_required
@admin_required
def reject_user(user_id):
    from app import db

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": "rejected"}}
    )
    flash("❌ User registration rejected")
    return redirect(request.referrer or url_for("admin.admin_approvals"))


@admin_bp.route("/admin/delete_public_announcement/<ann_id>")
@login_required
@admin_required
def delete_public_announcement(ann_id):
    from app import db

    db.public_announcements.delete_one({"_id": ObjectId(ann_id)})
    flash("Public Announcement deleted permanently")
    return redirect(request.referrer or url_for("resources.social"))


@admin_bp.route("/admin/delete_user/<user_id>")
@login_required
@admin_required
def delete_user(user_id):
    from app import db

    db.users.delete_one({"_id": ObjectId(user_id)})
    flash("User purged from database")
    return redirect(request.referrer or url_for("admin.admin_database"))


@admin_bp.route("/admin/delete_resource/<resource_id>")
@login_required
@admin_required
def delete_resource(resource_id):
    from app import db

    db.resources.delete_one({"_id": ObjectId(resource_id)})
    flash("Asset permanently deleted")
    return redirect(request.referrer or url_for("resources.social"))
