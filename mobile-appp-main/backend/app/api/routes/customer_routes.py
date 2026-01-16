"""
Customer routes - Mobile App
"""
from flask import Blueprint, request, jsonify, g
from app.infrastructure.databases import get_session
from app.models.customer_model import CustomerModel, MembershipTier
from app.utils.crypto import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token
from app.api.decorators import require_auth
from app.config import Config
from datetime import datetime, timedelta

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/register", methods=["POST"])
def customer_register():
    """Register a new customer"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        # Check if email already exists
        existing_customer = session.query(CustomerModel).filter(
            CustomerModel.email == data.get('email')
        ).first()
        if existing_customer:
            return jsonify({"message": "Email already registered"}), 400
        
        # Create customer
        hashed_password = hash_password(data.get('password'))
        customer = CustomerModel(
            name=data.get('name'),
            email=data.get('email'),
            password=hashed_password,
            phone=data.get('phone'),
            membership_tier=MembershipTier.IRON
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)
        
        return jsonify({
            "data": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "membership_tier": customer.membership_tier.value
            },
            "message": "Đăng ký thành công!"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@customer_bp.route("/login", methods=["POST"])
def customer_login():
    """Customer login"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        customer = session.query(CustomerModel).filter(
            CustomerModel.email == data.get('email')
        ).first()
        
        if not customer or not verify_password(data.get('password'), customer.password):
            return jsonify({"message": "Incorrect email or password"}), 401
        
        # Create tokens
        token_data = {
            "sub": customer.id,
            "role": "Customer",
            "customer_id": customer.id
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return jsonify({
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "membership_tier": customer.membership_tier.value,
                    "total_spending": customer.total_spending,
                    "points": customer.points
                }
            },
            "message": "Đăng nhập thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@customer_bp.route("/me", methods=["GET"])
@require_auth
def get_customer_info():
    """Get current customer information"""
    # Get customer from token
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    from app.utils.jwt import verify_access_token
    payload = verify_access_token(token)
    
    if not payload or payload.get('role') != 'Customer':
        return jsonify({"message": "Invalid customer token"}), 401
    
    customer_id = payload.get('customer_id')
    session = get_session()
    try:
        customer = session.query(CustomerModel).filter(
            CustomerModel.id == customer_id
        ).first()
        
        if not customer:
            return jsonify({"message": "Customer not found"}), 404
        
        return jsonify({
            "data": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "avatar": customer.avatar,
                "membership_tier": customer.membership_tier.value,
                "total_spending": customer.total_spending,
                "points": customer.points
            },
            "message": "Lấy thông tin khách hàng thành công!"
        }), 200
    finally:
        session.close()

