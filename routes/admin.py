"""
Admin routes — admin dashboard, approve/reject/delete users, delete resources
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from bson.objectid import ObjectId

from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    from app import db

    users = list(db.users.find())
    resources = list(db.resources.find())

    # Get pending approvals
    pending_users = list(db.users.find({"status": "pending"}).sort("created_at", -1))

    # Get contact messages
    contact_messages = list(db.contact_messages.find().sort("timestamp", -1).limit(20))

    # Get recent teacher activities (last 50)
    activities = list(db.activities.find().sort("timestamp", -1).limit(50))

    # Get teacher-specific stats
    teachers = list(db.users.find({"role": "Teacher"}))
    teacher_stats = []
    for teacher in teachers:
        uploads = db.resources.count_documents({"user_id": teacher["_id"]})
        groups_created = db.groups.count_documents({"created_by": teacher["_id"]})
        teacher_stats.append({
            "name": teacher["name"],
            "email": teacher["email"],
            "uploads": uploads,
            "groups": groups_created
        })

    return render_template("admin.html", users=users, resources=resources, activities=activities, teacher_stats=teacher_stats, pending_users=pending_users, contact_messages=contact_messages)


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
    return redirect(url_for("admin.admin_dashboard"))


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
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/delete_user/<user_id>")
@login_required
@admin_required
def delete_user(user_id):
    from app import db

    db.users.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/delete_resource/<resource_id>")
@login_required
@admin_required
def delete_resource(resource_id):
    from app import db

    db.resources.delete_one({"_id": ObjectId(resource_id)})
    return redirect(url_for("admin.admin_dashboard"))
