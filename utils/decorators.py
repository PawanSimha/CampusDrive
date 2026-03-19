"""
Custom decorators for CampusConnect App
"""

from functools import wraps
from flask_login import current_user


def admin_required(func):
    """Restrict access to admin users only"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            return "Admin access only"
        return func(*args, **kwargs)
    return wrapper
