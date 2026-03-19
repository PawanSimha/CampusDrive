"""
User model for Flask-Login integration
"""

from flask_login import UserMixin


class User(UserMixin):
    """User class for Flask-Login, wrapping MongoDB user documents"""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.name = user_data["name"]
        self.email = user_data["email"]
        self.role = user_data["role"]
        self.college = user_data["college"]
