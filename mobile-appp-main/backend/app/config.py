"""
Configuration settings for the Flask application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('ACCESS_TOKEN_SECRET') or 'your-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Database
    DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI') or 'postgresql://bigboy:bigboy123@localhost:5432/bigboy_db'
    
    # JWT
    ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', 'your-access-token-secret')
    REFRESH_TOKEN_SECRET = os.environ.get('REFRESH_TOKEN_SECRET', 'your-refresh-token-secret')
    ACCESS_TOKEN_EXPIRES_IN = int(os.environ.get('ACCESS_TOKEN_EXPIRES_IN', 900))  # 15 minutes
    REFRESH_TOKEN_EXPIRES_IN = int(os.environ.get('REFRESH_TOKEN_EXPIRES_IN', 604800))  # 7 days
    GUEST_ACCESS_TOKEN_EXPIRES_IN = int(os.environ.get('GUEST_ACCESS_TOKEN_EXPIRES_IN', 7200))  # 2 hours
    GUEST_REFRESH_TOKEN_EXPIRES_IN = int(os.environ.get('GUEST_REFRESH_TOKEN_EXPIRES_IN', 604800))  # 7 days
    
    # Initial Owner Account
    INITIAL_EMAIL_OWNER = os.environ.get('INITIAL_EMAIL_OWNER', 'admin@bigboy.com')
    INITIAL_PASSWORD_OWNER = os.environ.get('INITIAL_PASSWORD_OWNER', '123456')
    
    # Server
    PORT = int(os.environ.get('PORT', 4000))
    DOMAIN = os.environ.get('DOMAIN', 'localhost')
    PROTOCOL = os.environ.get('PROTOCOL', 'http')
    PRODUCTION = os.environ.get('PRODUCTION', 'false').lower() == 'true'
    PRODUCTION_URL = os.environ.get('PRODUCTION_URL', '')
    DOCKER = os.environ.get('DOCKER', 'false').lower() == 'true'
    
    # Upload
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
    UPLOAD_FOLDER = os.path.join(_base_dir, _upload_folder) if not os.path.isabs(_upload_folder) else _upload_folder
    
    # Client
    CLIENT_URL = os.environ.get('CLIENT_URL', 'http://localhost:3000')
    
    # Google OAuth (optional)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_AUTHORIZED_REDIRECT_URI = os.environ.get('GOOGLE_AUTHORIZED_REDIRECT_URI', '')
    GOOGLE_REDIRECT_CLIENT_URL = os.environ.get('GOOGLE_REDIRECT_CLIENT_URL', '')
    
    # Multi-tenant
    TENANT_HEADER = os.environ.get('TENANT_HEADER', 'X-Tenant-ID')
    DEFAULT_TENANT_ID = os.environ.get('DEFAULT_TENANT_ID', 'default')
    
    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Other
    SERVER_TIMEZONE = os.environ.get('SERVER_TIMEZONE', 'Asia/Ho_Chi_Minh')
    PAUSE_SOME_ENDPOINTS = os.environ.get('PAUSE_SOME_ENDPOINTS', 'false').lower() == 'true'
    
    CORS_HEADERS = 'Content-Type'
    
    @property
    def API_URL(self):
        if self.PRODUCTION:
            return self.PRODUCTION_URL
        return f"{self.PROTOCOL}://{self.DOMAIN}:{self.PORT}"

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

