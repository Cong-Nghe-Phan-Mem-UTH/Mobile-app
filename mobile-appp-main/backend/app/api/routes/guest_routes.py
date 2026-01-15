# src/api/routes/guest_routes.py
"""
Guest Routes

"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import logging

# Import models
from app.models.guest_model import GuestModel
from app.models.order_model import OrderModel, OrderStatus
from app.models.dish_model import DishModel, DishSnapshotModel, DishStatus
from app.models.table_model import TableModel, TableStatus
from app.models.tenant_model import TenantModel

# Import database
from app.infrastructure.databases import get_session

# Import utilities
from app.utils.jwt import create_access_token, create_refresh_token, verify_access_token
from app.utils.errors import AuthError, NotFoundError, EntityError
from app.config import Config

# Import socket plugin
from app.plugins.socket_plugin import get_socketio

logger = logging.getLogger(__name__)

# Create Blueprint
bp = Blueprint('guest', __name__)


# ==================== MIDDLEWARE/DECORATORS ====================

def guest_auth_required(f):
    """Decorator yêu cầu guest phải đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthError('Vui lòng đăng nhập')
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = verify_access_token(token)
        if not payload:
            raise AuthError('Token không hợp lệ hoặc đã hết hạn')
        
        # Check if guest token
        guest_id = payload.get('guestId')
        if not guest_id:
            raise AuthError('Token không hợp lệ')
        
        # Get guest from database
        session = get_session()
        try:
            guest = session.query(GuestModel).filter(
                GuestModel.id == guest_id
            ).first()
            
            if not guest:
                raise AuthError('Phiên đăng nhập đã hết hạn')
            
            # Store in g object
            g.guest_id = guest.id
            g.guest = guest
            g.table_number = guest.table_number
            g.tenant_id = guest.tenant_id
            g.session = session
            
        except AuthError:
            session.close()
            raise
        except Exception as e:
            session.close()
            logger.error(f"Guest auth error: {e}")
            raise AuthError('Xác thực thất bại')
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            if hasattr(g, 'session'):
                g.session.close()
    
    return decorated_function


# ==================== AUTHENTICATION ====================

@bp.route('/auth/login', methods=['POST'])
def guest_login():
    """
    Guest login qua QR code
    
    Request body:
    {
        "name": "Nguyễn Văn A",
        "table_token": "qr-token-abc123"
    }
    """
    session = get_session()
    try:
        data = request.get_json()
        
        if not data or 'table_token' not in data:
            raise EntityError('Thiếu thông tin QR token')
        
        table_token = data['table_token']
        name = data.get('name', 'Khách')
        
        # Find table by token
        table = session.query(TableModel).filter(
            TableModel.token == table_token
        ).first()
        
        if not table:
            raise NotFoundError('Mã QR không hợp lệ')
        
        # Check if guest already exists for this table
        existing_guest = session.query(GuestModel).filter(
            GuestModel.table_number == table.number,
            GuestModel.tenant_id == table.tenant_id
        ).order_by(GuestModel.created_at.desc()).first()
        
        if existing_guest:
            # Update existing guest
            existing_guest.name = name
            existing_guest.updated_at = datetime.utcnow()
            guest = existing_guest
        else:
            # Create new guest
            guest = GuestModel(
                tenant_id=table.tenant_id,
                name=name,
                table_number=table.number
            )
            session.add(guest)
        
        session.commit()
        session.refresh(guest)
        
        # Create tokens
        access_token = create_access_token(
            data={'guestId': guest.id, 'tableNumber': guest.table_number},
            is_guest=True
        )
        
        refresh_token = create_refresh_token(
            data={'guestId': guest.id},
            is_guest=True
        )
        
        # Store refresh token
        guest.refresh_token = refresh_token
        guest.refresh_token_expires_at = datetime.utcnow() + timedelta(
            seconds=Config.GUEST_REFRESH_TOKEN_EXPIRES_IN
        )
        session.commit()
        
        logger.info(f"Guest logged in: {name} at table {table.number}")
        
        # Emit socket event
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('guest_joined', {
                    'guestId': guest.id,
                    'guestName': name,
                    'tableNumber': table.number,
                    'tenantId': table.tenant_id
                }, room=f'tenant_{table.tenant_id}')
        except Exception as e:
            logger.warning(f"Socket emit failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'data': {
                'guest': {
                    'id': guest.id,
                    'name': guest.name,
                    'tableNumber': guest.table_number
                },
                'accessToken': access_token,
                'refreshToken': refresh_token,
                'expiresIn': Config.GUEST_ACCESS_TOKEN_EXPIRES_IN
            }
        }), 200
        
    except (EntityError, NotFoundError) as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        session.rollback()
        logger.error(f"Guest login error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Đăng nhập thất bại. Vui lòng thử lại'
        }), 500
    finally:
        session.close()


@bp.route('/auth/logout', methods=['POST'])
@guest_auth_required
def guest_logout():
    """Guest logout"""
    try:
        guest = g.guest
        
        # Clear refresh token
        guest.refresh_token = None
        guest.refresh_token_expires_at = None
        g.session.commit()
        
        logger.info(f"Guest logged out: {g.guest_id}")
        
        return jsonify({
            'success': True,
            'message': 'Đăng xuất thành công'
        }), 200
        
    except Exception as e:
        logger.error(f"Guest logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Đăng xuất thất bại'
        }), 500


@bp.route('/auth/refresh-token', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    session = get_session()
    try:
        data = request.get_json()
        refresh_token = data.get('refreshToken')
        
        if not refresh_token:
            raise EntityError('Thiếu refresh token')
        
        from app.utils.jwt import verify_refresh_token
        
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise AuthError('Refresh token không hợp lệ')
        
        guest_id = payload.get('guestId')
        
        # Get guest
        guest = session.query(GuestModel).filter(
            GuestModel.id == guest_id,
            GuestModel.refresh_token == refresh_token
        ).first()
        
        if not guest:
            raise AuthError('Refresh token không hợp lệ')
        
        # Check expiry
        if guest.refresh_token_expires_at and guest.refresh_token_expires_at < datetime.utcnow():
            raise AuthError('Refresh token đã hết hạn')
        
        # Create new access token
        new_access_token = create_access_token(
            data={'guestId': guest.id, 'tableNumber': guest.table_number},
            is_guest=True
        )
        
        return jsonify({
            'success': True,
            'data': {
                'accessToken': new_access_token,
                'expiresIn': Config.GUEST_ACCESS_TOKEN_EXPIRES_IN
            }
        }), 200
        
    except (EntityError, AuthError) as e:
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        logger.error(f"Refresh token error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Làm mới token thất bại'
        }), 500
    finally:
        session.close()


# ==================== MENU ====================

@bp.route('/menu', methods=['GET'])
def get_menu():
    """
    Xem menu (không cần đăng nhập)
    Query params: ?search=phở&category=Món%20chính
    """
    session = get_session()
    try:
        search = request.args.get('search', '')
        category = request.args.get('category')
        tenant_id = request.args.get('tenantId', type=int)
        
        # Query dishes
        query = session.query(DishModel).filter(
            DishModel.status == DishStatus.AVAILABLE
        )
        
        if tenant_id:
            query = query.filter(DishModel.tenant_id == tenant_id)
        
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                (DishModel.name.ilike(search_pattern)) |
                (DishModel.description.ilike(search_pattern))
            )
        
        if category:
            query = query.filter(DishModel.category == category)
        
        dishes = query.all()
        
        # Format response
        menu_data = {
            'dishes': [{
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'description': dish.description,
                'image': dish.image,
                'category': dish.category,
                'status': dish.status.value
            } for dish in dishes]
        }
        
        # Get unique categories
        categories = session.query(DishModel.category).filter(
            DishModel.status == DishStatus.AVAILABLE
        ).distinct().all()
        
        menu_data['categories'] = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'data': menu_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get menu error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Không thể tải menu'
        }), 500
    finally:
        session.close()


@bp.route('/dishes/<int:dish_id>', methods=['GET'])
def get_dish_detail(dish_id):
    """Xem chi tiết món ăn"""
    session = get_session()
    try:
        dish = session.query(DishModel).filter(
            DishModel.id == dish_id
        ).first()
        
        if not dish or dish.status == DishStatus.UNAVAILABLE:
            raise NotFoundError('Món ăn không tồn tại')
        
        return jsonify({
            'success': True,
            'data': {
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'description': dish.description,
                'image': dish.image,
                'category': dish.category,
                'status': dish.status.value
            }
        }), 200
        
    except NotFoundError as e:
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        logger.error(f"Get dish detail error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Không thể tải thông tin món ăn'
        }), 500
    finally:
        session.close()


# ==================== ORDERS - Đặt món ====================

@bp.route('/orders', methods=['POST'])
@guest_auth_required
def create_orders():
    """
    Đặt món
    Request body: { "orders": [{"dish_id": 1, "quantity": 2, "notes": "..."}] }
    """
    try:
        data = request.get_json()
        
        if not data or 'orders' not in data or not data['orders']:
            raise EntityError('Vui lòng chọn ít nhất 1 món')
        
        guest = g.guest
        session = g.session
        
        created_orders = []
        
        for order_data in data['orders']:
            dish_id = order_data.get('dish_id')
            quantity = order_data.get('quantity', 1)
            notes = order_data.get('notes', '')
            
            # Get dish
            dish = session.query(DishModel).filter(
                DishModel.id == dish_id
            ).first()
            
            if not dish or dish.status != DishStatus.AVAILABLE:
                continue
            
            # Create dish snapshot
            dish_snapshot = DishSnapshotModel(
                dish_id=dish.id,
                name=dish.name,
                price=dish.price,
                description=dish.description,
                image=dish.image,
                category=dish.category,
                status=dish.status.value
            )
            session.add(dish_snapshot)
            session.flush()
            
            # Create order
            order = OrderModel(
                tenant_id=guest.tenant_id,
                guest_id=guest.id,
                table_number=guest.table_number,
                dish_snapshot_id=dish_snapshot.id,
                quantity=quantity,
                notes=notes,
                status=OrderStatus.PENDING
            )
            session.add(order)
            created_orders.append(order)
        
        if not created_orders:
            raise EntityError('Không có món hợp lệ để đặt')
        
        session.commit()
        
        logger.info(f"Orders created: {len(created_orders)} by guest {g.guest_id}")
        
        # Emit socket event
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('new_orders', {
                    'guestId': guest.id,
                    'guestName': guest.name,
                    'tableNumber': guest.table_number,
                    'orderCount': len(created_orders),
                    'tenantId': guest.tenant_id
                }, room=f'tenant_{guest.tenant_id}')
        except Exception as e:
            logger.warning(f"Socket emit failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Đặt món thành công',
            'data': {
                'orderIds': [order.id for order in created_orders],
                'totalOrders': len(created_orders)
            }
        }), 201
        
    except EntityError as e:
        g.session.rollback()
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        g.session.rollback()
        logger.error(f"Create orders error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Đặt món thất bại. Vui lòng thử lại'
        }), 500


# ==================== ORDERS - Xem lịch sử ====================

@bp.route('/orders', methods=['GET'])
@guest_auth_required
def get_orders():
    """Xem lịch sử đặt món"""
    try:
        status = request.args.get('status')
        session = g.session
        
        # Query orders
        query = session.query(OrderModel).filter(
            OrderModel.guest_id == g.guest_id
        )
        
        if status:
            try:
                status_enum = OrderStatus[status.upper()]
                query = query.filter(OrderModel.status == status_enum)
            except KeyError:
                pass
        
        orders = query.order_by(OrderModel.created_at.desc()).all()
        
        # Format response
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'status': order.status.value,
                'quantity': order.quantity,
                'notes': order.notes,
                'createdAt': order.created_at.isoformat(),
                'dish': {
                    'name': order.dish_snapshot.name,
                    'image': order.dish_snapshot.image,
                    'price': order.dish_snapshot.price
                },
                'totalPrice': order.dish_snapshot.price * order.quantity
            })
        
        return jsonify({
            'success': True,
            'data': orders_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get orders error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Không thể tải lịch sử đơn hàng'
        }), 500


@bp.route('/orders/<int:order_id>', methods=['GET'])
@guest_auth_required
def get_order_detail(order_id):
    """Xem chi tiết đơn hàng"""
    try:
        session = g.session
        
        order = session.query(OrderModel).filter(
            OrderModel.id == order_id,
            OrderModel.guest_id == g.guest_id
        ).first()
        
        if not order:
            raise NotFoundError('Đơn hàng không tồn tại')
        
        order_data = {
            'id': order.id,
            'status': order.status.value,
            'tableNumber': order.table_number,
            'quantity': order.quantity,
            'notes': order.notes,
            'createdAt': order.created_at.isoformat(),
            'dish': {
                'name': order.dish_snapshot.name,
                'image': order.dish_snapshot.image,
                'price': order.dish_snapshot.price,
                'description': order.dish_snapshot.description
            },
            'totalPrice': order.dish_snapshot.price * order.quantity
        }
        
        return jsonify({
            'success': True,
            'data': order_data
        }), 200
        
    except NotFoundError as e:
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        logger.error(f"Get order detail error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Không thể tải thông tin đơn hàng'
        }), 500


# ==================== PAYMENT ====================

@bp.route('/payment/request', methods=['POST'])
@guest_auth_required
def request_payment():
    """Yêu cầu thanh toán"""
    try:
        session = g.session
        
        # Get all unpaid orders
        orders = session.query(OrderModel).filter(
            OrderModel.guest_id == g.guest_id,
            OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.READY, OrderStatus.SERVED])
        ).all()
        
        if not orders:
            raise EntityError('Không có đơn hàng nào cần thanh toán')
        
        # Calculate total
        total_amount = sum(
            order.dish_snapshot.price * order.quantity 
            for order in orders
        )
        
        logger.info(f"Payment requested by guest {g.guest_id}: {len(orders)} orders")
        
        # Emit socket event
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('payment_requested', {
                    'guestId': g.guest.id,
                    'guestName': g.guest.name,
                    'tableNumber': g.guest.table_number,
                    'orderCount': len(orders),
                    'totalAmount': total_amount,
                    'tenantId': g.guest.tenant_id
                }, room=f'tenant_{g.guest.tenant_id}')
        except Exception as e:
            logger.warning(f"Socket emit failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Yêu cầu thanh toán đã được gửi đến nhân viên',
            'data': {
                'orderCount': len(orders),
                'totalAmount': total_amount
            }
        }), 200
        
    except EntityError as e:
        return jsonify({'success': False, 'message': str(e.description)}), e.code
    except Exception as e:
        logger.error(f"Request payment error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Không thể gửi yêu cầu thanh toán'
        }), 500


# Export blueprint
__all__ = ['bp']
