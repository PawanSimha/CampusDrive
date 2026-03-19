"""
Resource routes — upload, social, subjects, edit, delete, download, detail, favorites, privacy
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from utils.helpers import allowed_file

resources_bp = Blueprint("resources", __name__)


@resources_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    from app import db

    if request.method == "POST":
        title = request.form["title"]
        subject = request.form["subject"]
        semester = request.form["semester"]
        resource_type = request.form["resource_type"]
        year_batch = request.form["year_batch"]
        tags = request.form["tags"].split(",")
        description = request.form["description"]
        privacy = request.form["privacy"]

        file = request.files["file"]

        if file and allowed_file(file.filename):
            # Secure File Naming
            original_name = secure_filename(file.filename)
            unique_name = str(uuid.uuid4()) + "_" + original_name
            filepath = os.path.join("static/uploads", unique_name)
            file.save(filepath)

            db.resources.insert_one({
                "user_id": ObjectId(current_user.id),
                "title": title,
                "subject": subject,
                "semester": semester,
                "resource_type": resource_type,
                "year_batch": year_batch,
                "tags": tags,
                "description": description,
                "file_path": filepath,
                "privacy": privacy,
                "college": current_user.college,
                "created_at": datetime.utcnow(),
                "avg_rating": 0,
                "download_count": 0
            })

            # Log activity if user is a teacher
            if current_user.role in ["Teacher", "admin"]:
                db.activities.insert_one({
                    "user_id": ObjectId(current_user.id),
                    "user_name": current_user.name,
                    "action": "uploaded_resource",
                    "details": {"resource_title": title, "subject": subject},
                    "timestamp": datetime.utcnow()
                })

            flash("Resource uploaded successfully")
            return redirect(url_for("resources.social"))

        else:
            flash("Invalid file type")

    return render_template("upload.html")


@resources_bp.route("/social")
@login_required
def social():
    from app import db

    search = request.args.get("search")
    subject = request.args.get("subject")
    semester = request.args.get("semester")
    resource_type = request.args.get("resource_type")
    branch = request.args.get("branch")
    privacy = request.args.get("privacy")
    year_batch = request.args.get("year_batch")
    sort_by = request.args.get("sort")

    # Base privacy filter: Public OR My Private Files
    privacy_filter = {
        "$or": [
            {"privacy": "public"},
            {"user_id": ObjectId(current_user.id)}
        ]
    }

    # Start constructing the final query
    query = {"$and": [privacy_filter]}

    # Unified search across title, subject, tags, description
    if search:
        search_filter = {
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"subject": {"$regex": search, "$options": "i"}},
                {"tags": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        }
        query["$and"].append(search_filter)

    if subject:
        query["$and"].append({"subject": {"$regex": subject, "$options": "i"}})

    if semester:
        query["$and"].append({"semester": semester})

    if resource_type:
        query["$and"].append({"resource_type": resource_type})

    if branch:
        query["$and"].append({"branch": branch})

    if privacy:
        query["$and"].append({"privacy": privacy})

    if year_batch:
        query["$and"].append({"year_batch": year_batch})

    # Sorting logic
    if sort_by == "rating":
        resources = list(db.resources.find(query).sort("avg_rating", -1))
    elif sort_by == "popular":
        resources = list(db.resources.find(query).sort("download_count", -1))
    elif sort_by == "latest":
        resources = list(db.resources.find(query).sort("created_at", -1))
    else:
        resources = list(db.resources.find(query).sort("created_at", -1))

    # Get distinct values for filter dropdowns
    all_subjects = db.resources.distinct("subject")
    all_branches = db.users.distinct("branch")

    return render_template("social.html", resources=resources, subjects=all_subjects, branches=all_branches)


@resources_bp.route("/subjects")
@login_required
def subjects():
    from app import db

    subjects = db.resources.distinct("subject")
    return render_template("subjects.html", subjects=subjects)


@resources_bp.route("/edit_resource/<resource_id>", methods=["GET", "POST"])
@login_required
def edit_resource(resource_id):
    from app import db

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})

    if not resource:
        flash("Resource not found")
        return redirect(url_for("main.profile"))

    # Only owner can edit
    if str(resource["user_id"]) != current_user.id:
        flash("You can only edit your own resources")
        return redirect(url_for("resources.social"))

    if request.method == "POST":
        db.resources.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {
                "title": request.form["title"],
                "subject": request.form["subject"],
                "semester": request.form["semester"],
                "resource_type": request.form["resource_type"],
                "year_batch": request.form["year_batch"],
                "tags": request.form["tags"].split(","),
                "description": request.form["description"],
                "privacy": request.form["privacy"]
            }}
        )
        flash("Resource updated successfully")
        return redirect(url_for("resources.resource_detail", resource_id=resource_id))

    return render_template("edit_resource.html", resource=resource)


@resources_bp.route("/delete_my_resource/<resource_id>")
@login_required
def delete_my_resource(resource_id):
    from app import db

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})

    if not resource:
        flash("Resource not found")
        return redirect(url_for("main.profile"))

    # Only owner can delete
    if str(resource["user_id"]) != current_user.id:
        flash("You can only delete your own resources")
        return redirect(url_for("resources.social"))

    # Delete the file from filesystem
    if os.path.exists(resource["file_path"]):
        os.remove(resource["file_path"])

    # Delete reviews for this resource
    db.reviews.delete_many({"resource_id": ObjectId(resource_id)})

    # Delete the resource
    db.resources.delete_one({"_id": ObjectId(resource_id)})

    flash("Resource deleted successfully")
    return redirect(url_for("main.profile"))


@resources_bp.route("/toggle_favorite/<resource_id>")
@login_required
def toggle_favorite(resource_id):
    from app import db

    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    favorites = user_data.get("favorites", [])

    resource_oid = ObjectId(resource_id)

    if resource_oid in favorites:
        # Remove from favorites
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"favorites": resource_oid}}
        )
        flash("Resource removed from favorites")
    else:
        # Add to favorites
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$push": {"favorites": resource_oid}}
        )
        flash("⭐ Resource added to favorites!")

    return redirect(url_for("resources.resource_detail", resource_id=resource_id))


@resources_bp.route("/toggle_privacy/<resource_id>")
@login_required
def toggle_privacy(resource_id):
    from app import db

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})

    if not resource:
        flash("Resource not found")
        return redirect(url_for("resources.social"))

    # Only the uploader can toggle privacy
    if str(resource["user_id"]) != current_user.id:
        flash("You can only change privacy of your own resources")
        return redirect(url_for("resources.social"))

    # Toggle privacy
    new_privacy = "private" if resource["privacy"] == "public" else "public"
    db.resources.update_one(
        {"_id": ObjectId(resource_id)},
        {"$set": {"privacy": new_privacy}}
    )

    flash(f"Resource privacy changed to {new_privacy}")
    return redirect(url_for("resources.resource_detail", resource_id=resource_id))


@resources_bp.route("/download/<resource_id>")
@login_required
def download(resource_id):
    from app import db

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})

    if not resource:
        return "Resource not found"

    # Access control again
    if resource["privacy"] == "private":
        # STRICT: Only owner can download private files
        if str(resource["user_id"]) != str(current_user.id):
            flash("⛔ Access Denied: This resource is private and only visible to the owner.")
            return redirect(url_for("resources.social"))

    db.resources.update_one(
        {"_id": ObjectId(resource_id)},
        {"$inc": {"download_count": 1}}
    )

    # Fix for Windows paths
    file_path = resource["file_path"].replace("\\", "/")

    # Force download
    return send_file(file_path, as_attachment=True)


@resources_bp.route("/resource/<resource_id>", methods=["GET", "POST"])
@login_required
def resource_detail(resource_id):
    from app import db

    resource = db.resources.find_one({"_id": ObjectId(resource_id)})

    if not resource:
        return "Resource not found"

    # Access Control Logic
    if resource["privacy"] == "private":
        if str(resource["user_id"]) != str(current_user.id):
            flash("⛔ Access Denied: This resource is private and only visible to the owner.")
            return redirect(url_for("resources.social"))

    # Handle Review Submission
    if request.method == "POST":
        rating = int(request.form["rating"])
        review_text = request.form.get("comment", request.form.get("review", ""))

        existing_review = db.reviews.find_one({
            "resource_id": ObjectId(resource_id),
            "user_id": ObjectId(current_user.id)
        })

        if existing_review:
            db.reviews.update_one(
                {"_id": existing_review["_id"]},
                {"$set": {"rating": rating, "comment": review_text, "reviewer_name": current_user.name}}
            )
        else:
            db.reviews.insert_one({
                "resource_id": ObjectId(resource_id),
                "user_id": ObjectId(current_user.id),
                "reviewer_name": current_user.name,
                "rating": rating,
                "comment": review_text,
                "created_at": datetime.utcnow()
            })

        # Recalculate Average Rating
        all_reviews = list(db.reviews.find({"resource_id": ObjectId(resource_id)}))
        avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)

        db.resources.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": {"avg_rating": round(avg_rating, 2)}}
        )

        flash("✅ Review submitted successfully!")
        return redirect(url_for("resources.resource_detail", resource_id=resource_id))

    reviews = list(db.reviews.find({"resource_id": ObjectId(resource_id)}))

    # Check if current user has favorited this resource
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    is_favorited = ObjectId(resource_id) in user_data.get("favorites", [])

    return render_template(
        "resource_detail.html",
        resource=resource,
        reviews=reviews,
        is_favorited=is_favorited
    )
