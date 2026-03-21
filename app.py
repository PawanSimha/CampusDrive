"""
Campus Drive App — Entry Point

Slim app factory with Flask extensions, MongoDB connection,
and Blueprint registration. All routes live in routes/*.py.
"""

from flask import Flask
from pymongo import MongoClient
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from bson.objectid import ObjectId
import certifi
import logging
from logging.handlers import RotatingFileHandler
import os

from config import Config
from models.user import User

# -------------------------
# Create Flask App
# -------------------------
app = Flask(__name__)
app.config.from_object(Config)

# -------------------------
# Security Enhancements
# -------------------------
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# -------------------------
# MongoDB Connection
# -------------------------
client = MongoClient(
    app.config["MONGO_URI"],
    tlsCAFile=certifi.where(),
    maxPoolSize=50,
    wTimeoutMS=2500
)
db = client.get_database()

# Scalability Indexes
db.resources.create_index([("download_count", -1)])
db.resources.create_index([("avg_rating", -1)])
db.resources.create_index([("created_at", -1)])

# -------------------------
# Logging Configuration (Production)
# -------------------------
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/campusconnect.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('CampusConnect Startup')

# -------------------------
# Flask Extensions
# -------------------------
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user)
    return None


# -------------------------
# Register Blueprints
# -------------------------
from routes.auth import auth_bp
from routes.main import main_bp
from routes.resources import resources_bp
from routes.groups import groups_bp
from routes.admin import admin_bp
from routes.errors import errors_bp
from routes.aradhaya import aradhaya_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(aradhaya_bp)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
