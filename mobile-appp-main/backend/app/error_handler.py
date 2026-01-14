"""
Error handler for Flask application
"""
from flask import jsonify
from app.utils.errors import EntityError, AuthError, ForbiddenError, NotFoundError

def setup_error_handler(app):
    """Setup error handlers"""
    
    @app.errorhandler(EntityError)
    def handle_entity_error(error):
        return jsonify({
            'message': error.detail,
            'statusCode': error.status_code
        }), error.status_code
    
    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        response = jsonify({
            'message': error.detail,
            'statusCode': error.status_code
        })
        response.set_cookie('session_token', '', max_age=0)
        return response, error.status_code
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        return jsonify({
            'message': error.detail,
            'statusCode': error.status_code
        }), error.status_code
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return jsonify({
            'message': error.detail,
            'statusCode': error.status_code
        }), error.status_code
    
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            'message': 'Resource not found',
            'statusCode': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            'message': 'Internal server error',
            'statusCode': 500
        }), 500

