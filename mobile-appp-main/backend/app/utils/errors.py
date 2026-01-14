"""
Custom exceptions for Flask
"""
from werkzeug.exceptions import HTTPException

class EntityError(HTTPException):
    """Entity validation error"""
    code = 400
    description = "Entity validation error"

class AuthError(HTTPException):
    """Authentication error"""
    code = 401
    description = "Authentication error"

class ForbiddenError(HTTPException):
    """Forbidden error"""
    code = 403
    description = "Forbidden"

class NotFoundError(HTTPException):
    """Not found error"""
    code = 404
    description = "Resource not found"
