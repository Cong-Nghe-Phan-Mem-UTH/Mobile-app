"""
Routes package - Register all blueprints
"""
from app.api.routes.auth_routes import auth_bp
from app.api.routes.dish_routes import dish_bp
from app.api.routes.restaurant_routes import restaurant_bp
from app.api.routes.order_routes import order_bp
from app.api.routes.table_routes import table_bp
from app.api.routes.guest_routes import guest_bp
from app.api.routes.admin_routes import admin_bp
from app.api.routes.static_routes import static_bp
from app.api.routes.customer_routes import customer_bp
from app.api.routes.mobile_routes import mobile_bp
from app.api.routes.review_routes import review_bp
from app.api.routes.reservation_routes import reservation_bp
from app.api.routes.history_routes import history_bp
from app.api.routes.membership_routes import membership_bp
from app.api.routes.qr_routes import qr_bp

def register_routes(app):
    # Register static route FIRST
    app.register_blueprint(static_bp, url_prefix="/static")
    
    # Register API routes
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(dish_bp, url_prefix="/api/v1/dishes")
    app.register_blueprint(restaurant_bp, url_prefix="/api/v1/restaurants")
    app.register_blueprint(order_bp, url_prefix="/api/v1/orders")
    app.register_blueprint(table_bp, url_prefix="/api/v1/tables")
    app.register_blueprint(guest_bp, url_prefix="/api/v1/guest")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    
    # Mobile App routes
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customer")
    app.register_blueprint(mobile_bp, url_prefix="/api/v1/mobile")
    app.register_blueprint(review_bp, url_prefix="/api/v1")
    app.register_blueprint(reservation_bp, url_prefix="/api/v1")
    app.register_blueprint(history_bp, url_prefix="/api/v1")
    app.register_blueprint(membership_bp, url_prefix="/api/v1/membership")
    app.register_blueprint(qr_bp, url_prefix="/api/v1/qr")

