"""
Utility helper functions for CampusConnect App
"""

import random
import string


# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {"pdf", "docx", "ppt", "pptx", "xlsx", "xls", "png", "jpg", "jpeg"}


def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_group_code():
    """Generate a unique group code in format AAAA-0000"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"
