"""
Static file routes
"""
from flask import Blueprint, send_from_directory
from app.config import Config
import os

static_bp = Blueprint("static", __name__)

@static_bp.route("/<path:filename>")
def serve_static(filename):
    """Serve static files from uploads folder"""
    upload_folder = Config.UPLOAD_FOLDER
    if os.path.exists(os.path.join(upload_folder, filename)):
        return send_from_directory(upload_folder, filename)
    return {"message": "File not found"}, 404
