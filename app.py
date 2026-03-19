"""
Campus-Drive App — Entry Point

Slim app factory with Flask extensions, MongoDB connection,
and Blueprint registration. All routes live in routes/*.py.
"""

from flask import Flask
from pymongo import MongoClient
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
import certifi

from config import Config
from models.user import User

# -------------------------
# Create Flask App
# -------------------------
app = Flask(__name__)
app.config.from_object(Config)

# -------------------------
# MongoDB Connection
# -------------------------
client = MongoClient(
    app.config["MONGO_URI"],
    tlsCAFile=certifi.where()
)
db = client.get_database()

# -------------------------
# Flask Extensions
# -------------------------
bcrypt = Bcrypt(app)
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

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(admin_bp)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
