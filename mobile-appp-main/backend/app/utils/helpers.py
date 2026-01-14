"""
Helper utilities
"""
import os
import secrets
import hashlib
from pathlib import Path


def create_folder(folder_path: str) -> None:
    """Create folder if it doesn't exist"""
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def generate_qr_token() -> str:
    """Generate QR token for table"""
    return secrets.token_urlsafe(32)


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    import unicodedata
    import re
    
    # Normalize unicode
    name = unicodedata.normalize('NFD', name)
    # Remove diacritics
    name = name.encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace spaces with hyphens
    name = name.lower().strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name


def hash_string(text: str) -> str:
    """Hash a string using SHA256"""
    return hashlib.sha256(text.encode()).hexdigest()

