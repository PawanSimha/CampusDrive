"""
Authentication routes — register, login, logout
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register")
def register():
    return render_template("register.html")


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    from app import db, bcrypt
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        college = request.form["college"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        role = "Student"

        if db.users.find_one({"email": email}):
            flash("Email already exists")
            return redirect(url_for("auth.register_student"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "college": college,
            "branch": branch,
            "semester": semester,
            "role": role,
            "status": "pending",
            "favorites": [],
            "created_at": datetime.utcnow()
        })
        flash("Registration submitted! Please wait for admin approval.")
        return redirect(url_for("auth.login"))
    return render_template("register_student.html")


@auth_bp.route("/register/teacher", methods=["GET", "POST"])
def register_teacher():
    from app import db, bcrypt
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        college = request.form["college"]
        branch = request.form["branch"]
        teacher_id = request.form["teacher_id"]
        bio = request.form.get("bio", "")
        role = "Teacher"

        # Regex Validation for Teacher ID: 4 uppercase letters + 6 digits
        import re
        if not re.match(r"^[A-Z]{4}[0-9]{6}$", teacher_id):
            flash("❌ Invalid Teacher ID format. Must be 4 uppercase letters followed by 6 digits (e.g., ABCD123456).")
            return redirect(url_for("auth.register_teacher"))

        if db.users.find_one({"email": email}):
            flash("Email already exists")
            return redirect(url_for("auth.register_teacher"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "college": college,
            "branch": branch,
            "teacher_id": teacher_id,
            "bio": bio,
            "role": role,
            "status": "pending",
            "favorites": [],
            "created_at": datetime.utcnow()
        })
        flash("Faculty registration submitted! Admin will verify your credentials and Teacher ID.")
        return redirect(url_for("auth.login"))
    return render_template("register_teacher.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app import db, bcrypt
    from models.user import User

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):
            # Check if user is approved (admin always approved)
            if user["role"] != "admin" and user.get("status", "approved") == "pending":
                flash("⏳ Your account is pending admin approval. Please wait.")
                return redirect(url_for("auth.login"))
            if user["role"] != "admin" and user.get("status") == "rejected":
                flash("❌ Your registration has been rejected by the admin.")
                return redirect(url_for("auth.login"))

            login_user(User(user), remember=True)
            # Redirect admin to dashboard, others to social area
            if user["role"] == "admin":
                return redirect(url_for("main.dashboard"))
            else:
                return redirect(url_for("resources.social"))

        flash("Invalid credentials")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
