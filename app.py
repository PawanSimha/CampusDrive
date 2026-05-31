"""
Campus Drive App — Entry Point

Slim app factory with Flask extensions, MongoDB connection,
and Blueprint registration. All routes live in routes/*.py.
"""

from flask import Flask, request
from pymongo import MongoClient
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from bson.objectid import ObjectId
import certifi
import logging
from logging.handlers import RotatingFileHandler
import os
import tempfile

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
# MongoDB Connection (Lazy — safe for serverless)
# -------------------------
_db_client = None
_db_instance = None

def get_db():
    global _db_client, _db_instance
    if _db_instance is not None:
        return _db_instance
    _db_client = MongoClient(
        app.config["MONGO_URI"],
        tlsCAFile=certifi.where(),
        maxPoolSize=50,
        wTimeoutMS=2500,
        serverSelectionTimeoutMS=5000
    )
    _db_instance = _db_client.get_database()
    try:
        _db_instance.resources.create_index([("download_count", -1)])
        _db_instance.resources.create_index([("avg_rating", -1)])
        _db_instance.resources.create_index([("created_at", -1)])
    except Exception:
        pass
    return _db_instance

class _DBProxy:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = _DBProxy()

# -------------------------
# Logging Configuration (Serverless-compatible)
# -------------------------
if not app.debug:
    try:
        log_dir = os.path.join(tempfile.gettempdir(), 'campusdrive_logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'campusconnect.log'),
            maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    except (OSError, PermissionError):
        pass
    app.logger.setLevel(logging.INFO)
    app.logger.info('CampusDrive Startup')

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
# Production URL Context (for templates)
# -------------------------
@app.context_processor
def inject_site_url():
    """Inject SITE_URL into all templates.
    Uses VERCEL_URL env var when deployed, falls back to request.url_root locally.
    """
    vercel_url = os.environ.get("VERCEL_URL")
    if vercel_url:
        site_url = f"https://{vercel_url}/"
    else:
        site_url = request.url_root
    return dict(SITE_URL=site_url)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
