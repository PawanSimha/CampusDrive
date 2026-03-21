"""
Main routes — home, contact, dashboard, profile
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_required, current_user
from bson.objectid import ObjectId

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    from app import db

    # Fetch 3 latest resources for Content Highlights
    latest_resources = list(db.resources.find({"privacy": "public"}).sort("created_at", -1).limit(3))
    return render_template("home.html", latest_resources=latest_resources)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    from app import db

    # Show user's uploaded resources and activity
    my_resources = list(db.resources.find({"user_id": ObjectId(current_user.id)}).sort("created_at", -1))
    total_users = db.users.count_documents({})
    total_resources = db.resources.count_documents({})
    total_groups = db.groups.count_documents({})
    total_downloads = sum(r.get("download_count", 0) for r in db.resources.find({}, {"download_count": 1}))
    return render_template("dashboard.html", user=current_user, my_resources=my_resources, total_users=total_users, total_resources=total_resources, total_groups=total_groups, total_downloads=total_downloads)


@main_bp.route("/profile")
@login_required
def profile():
    from app import db

    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    my_resources = list(db.resources.find({"user_id": ObjectId(current_user.id)}).sort("created_at", -1))
    my_reviews_count = db.reviews.count_documents({"user_id": ObjectId(current_user.id)})

    # Get favorited resources
    fav_ids = user_data.get("favorites", [])
    favorite_resources = list(db.resources.find({"_id": {"$in": fav_ids}})) if fav_ids else []

    return render_template("profile.html", user=user_data, resources=my_resources, reviews_count=my_reviews_count, favorite_resources=favorite_resources)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    from app import db

    if request.method == "POST":
        sender_name = request.form["name"]
        sender_email = request.form["email"]
        subject = request.form["subject"]
        message_body = request.form["message"]

        # Store contact message in database
        db.contact_messages.insert_one({
            "name": sender_name,
            "email": sender_email,
            "subject": subject,
            "message": message_body,
            "timestamp": datetime.utcnow(),
            "read": False
        })

        flash("✅ Your message has been sent successfully! We'll get back to you soon.")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")


@main_bp.route("/robots.txt")
@main_bp.route("/sitemap.xml")
@main_bp.route("/ai.txt")
@main_bp.route("/humans.txt")
def static_from_root():
    from flask import current_app
    return send_from_directory(current_app.static_folder, request.path[1:])
