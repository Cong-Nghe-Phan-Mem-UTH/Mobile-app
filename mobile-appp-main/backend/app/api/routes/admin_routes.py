"""
Admin routes
"""
from flask import Blueprint, request, jsonify, g
from app.infrastructure.databases import get_session
from app.models.tenant_model import TenantModel, TenantStatus
from app.models.account_model import AccountModel, AccountRole
from app.api.decorators import require_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/restaurants", methods=["GET"])
@require_admin
def admin_get_restaurants():
    """Get all restaurants (Admin only)"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    status = request.args.get('status')
    
    session = get_session()
    try:
        query = session.query(TenantModel)
        
        if status:
            query = query.filter(TenantModel.status == TenantStatus(status))
        
        restaurants = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            "data": [{
                "id": r.id,
                "name": r.name,
                "slug": r.slug,
                "email": r.email,
                "phone": r.phone,
                "address": r.address,
                "logo": r.logo,
                "description": r.description,
                "status": r.status.value,
                "subscription": r.subscription.value,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in restaurants],
            "message": "Lấy danh sách nhà hàng thành công!"
        }), 200
    finally:
        session.close()


@admin_bp.route("/restaurants/<int:restaurant_id>/status", methods=["PUT"])
@require_admin
def update_restaurant_status(restaurant_id):
    """Update restaurant status (Admin only)"""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        restaurant = session.query(TenantModel).filter(
            TenantModel.id == restaurant_id
        ).first()
        
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404
        
        try:
            restaurant.status = TenantStatus(data['status'])
            session.commit()
            session.refresh(restaurant)
            
            return jsonify({
                "data": {
                    "id": restaurant.id,
                    "status": restaurant.status.value
                },
                "message": "Cập nhật trạng thái nhà hàng thành công!"
            }), 200
        except ValueError:
            return jsonify({"message": "Invalid status"}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@admin_bp.route("/users", methods=["GET"])
@require_admin
def admin_get_users():
    """Get all users (Admin only)"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    role = request.args.get('role')
    
    session = get_session()
    try:
        query = session.query(AccountModel)
        
        if role:
            query = query.filter(AccountModel.role == AccountRole(role))
        
        users = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            "data": [{
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "avatar": u.avatar,
                "role": u.role.value,
                "tenant_id": u.tenant_id,
                "created_at": u.created_at.isoformat() if u.created_at else None
            } for u in users],
            "message": "Lấy danh sách người dùng thành công!"
        }), 200
    finally:
        session.close()
