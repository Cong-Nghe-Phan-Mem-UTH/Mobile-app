"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.databases import get_session
from app.models.account_model import AccountModel, AccountRole
from app.models.tenant_model import TenantModel, TenantStatus
from app.utils.crypto import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token
from app.utils.helpers import generate_slug
from app.api.decorators import require_auth
from app.config import Config
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new restaurant (tenant)"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        # Check if email already exists
        existing_tenant = session.query(TenantModel).filter(
            TenantModel.email == data.get('email')
        ).first()
        if existing_tenant:
            return jsonify({"message": "Email already registered"}), 400
        
        # Generate slug
        slug = generate_slug(data.get('name', ''))
        base_slug = slug
        counter = 1
        while session.query(TenantModel).filter(TenantModel.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create tenant
        tenant = TenantModel(
            name=data.get('name'),
            slug=slug,
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            description=data.get('description'),
            status=TenantStatus.ACTIVE
        )
        session.add(tenant)
        session.flush()
        
        # Create owner account
        hashed_password = hash_password(data.get('password'))
        owner = AccountModel(
            name=data.get('name'),
            email=data.get('email'),
            password=hashed_password,
            role=AccountRole.OWNER,
            tenant_id=tenant.id
        )
        session.add(owner)
        session.commit()
        
        return jsonify({
            "data": {
                "id": tenant.id,
                "name": tenant.name,
                "slug": tenant.slug,
                "email": tenant.email,
                "status": tenant.status.value
            },
            "message": "Đăng ký thành công!"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        user = session.query(AccountModel).filter(
            AccountModel.email == data.get('email')
        ).first()
        
        if not user or not verify_password(data.get('password'), user.password):
            return jsonify({"message": "Incorrect email or password"}), 401
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "role": user.role.value,
            "tenant_id": user.tenant_id
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Save refresh token to database
        from app.models.refresh_token_model import RefreshTokenModel
        
        refresh_token_model = RefreshTokenModel(
            token=refresh_token,
            account_id=user.id,
            expires_at=datetime.utcnow() + timedelta(seconds=Config.REFRESH_TOKEN_EXPIRES_IN)
        )
        session.add(refresh_token_model)
        session.commit()
        
        return jsonify({
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            },
            "message": "Đăng nhập thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    """Refresh access token"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    refresh_token = data.get('refresh_token')
    payload = verify_refresh_token(refresh_token)
    
    if not payload:
        return jsonify({"message": "Invalid refresh token"}), 401
    
    session = get_session()
    try:
        # Verify token exists in database
        from app.models.refresh_token_model import RefreshTokenModel
        
        token_model = session.query(RefreshTokenModel).filter(
            RefreshTokenModel.token == refresh_token
        ).first()
        
        if not token_model or token_model.expires_at < datetime.utcnow():
            return jsonify({"message": "Refresh token expired or invalid"}), 401
        
        # Get user
        user_id = payload.get("sub")
        user = session.query(AccountModel).filter(AccountModel.id == user_id).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 401
        
        # Create new tokens
        token_data = {
            "sub": user.id,
            "role": user.role.value,
            "tenant_id": user.tenant_id
        }
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Update refresh token
        token_model.token = new_refresh_token
        token_model.expires_at = datetime.utcnow() + timedelta(seconds=Config.REFRESH_TOKEN_EXPIRES_IN)
        session.commit()
        
        return jsonify({
            "data": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            },
            "message": "Refresh token thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user_info():
    """Get current user information"""
    from flask import g
    return jsonify({
        "data": {
            "id": g.current_user.id,
            "name": g.current_user.name,
            "email": g.current_user.email,
            "avatar": g.current_user.avatar,
            "role": g.current_user.role.value,
            "tenant_id": g.current_user.tenant_id
        },
        "message": "Lấy thông tin user thành công!"
    }), 200
