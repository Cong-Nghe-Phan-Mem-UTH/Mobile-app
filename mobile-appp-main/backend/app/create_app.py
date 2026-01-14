"""
Flask application factory
"""
from flask import Flask, request
from flask_cors import CORS
from app.config import Config
from app.api.routes import register_routes
from app.api.middleware import setup_middleware
from app.infrastructure.databases import init_db
from app.error_handler import setup_error_handler
from app.utils.helpers import create_folder
from app.utils.init_data import init_admin_account

def create_app():
    app = Flask(__name__, static_folder=None, static_url_path=None)
    app.config.from_object(Config)
    
    # Set max content length for file uploads
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Ensure UTF-8 encoding for responses
    app.config['JSON_AS_ASCII'] = False
    
    # CORS
    CORS(app, 
         resources={
             r"/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-Tenant-ID"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })
    
    # Disable strict slashes
    app.url_map.strict_slashes = False
    
    @app.after_request
    def after_request(response):
        # Set charset to UTF-8 for all responses
        content_type = response.headers.get('Content-Type', 'application/json')
        if 'charset' not in content_type.lower():
            if 'application/json' in content_type:
                response.headers['Content-Type'] = 'application/json; charset=utf-8'
            elif 'text/html' in content_type:
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup error handler
    setup_error_handler(app)
    
    # Initialize database
    init_db(app)
    
    # Create upload folder
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    create_folder(upload_folder)
    
    # Health check endpoints
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'BigBoy API is running', 'version': '1.0.0'}, 200
    
    # Test endpoint
    @app.route('/test', methods=['GET'])
    def test():
        return {'message': 'API hoạt động bình thường!'}, 200
    
    # Register routes
    register_routes(app)
    
    # Initialize admin account
    with app.app_context():
        init_admin_account()
    
    return app

