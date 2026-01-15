"""
Order routes
"""
from flask import Blueprint, request, jsonify, g
from app.infrastructure.databases import get_session
from app.models.order_model import OrderModel, OrderStatus
from app.models.dish_model import DishModel, DishSnapshotModel
from app.api.decorators import require_employee
from datetime import datetime

order_bp = Blueprint("order", __name__)


@order_bp.route("", methods=["POST"])
@require_employee
def create_orders():
    """Create orders"""
    if not g.current_user.tenant_id:
        return jsonify({"message": "User must belong to a tenant"}), 403
    
    data = request.get_json()
    if not data or 'orders' not in data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        orders = []
        table_number = data.get('table_number')
        
        for order_data in data['orders']:
            # Get dish
            dish = session.query(DishModel).filter(
                DishModel.id == order_data.get('dish_id')
            ).first()
            
            if not dish:
                return jsonify({"message": f"Dish {order_data.get('dish_id')} not found"}), 404
            
            # Check tenant access
            if dish.tenant_id != g.current_user.tenant_id:
                return jsonify({"message": "Access denied"}), 403
            
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
                tenant_id=g.current_user.tenant_id,
                table_number=order_data.get('table_number') or table_number,
                dish_snapshot_id=dish_snapshot.id,
                quantity=order_data.get('quantity', 1),
                notes=order_data.get('notes'),
                status=OrderStatus.PENDING
            )
            session.add(order)
            orders.append(order)
        
        session.commit()
        
        # Refresh orders
        for order in orders:
            session.refresh(order)
        
        return jsonify({
            "data": [{
                "id": o.id,
                "tenant_id": o.tenant_id,
                "table_number": o.table_number,
                "dish_snapshot_id": o.dish_snapshot_id,
                "quantity": o.quantity,
                "notes": o.notes,
                "status": o.status.value,
                "created_at": o.created_at.isoformat() if o.created_at else None
            } for o in orders],
            "message": f"Tạo thành công {len(orders)} đơn hàng!"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@order_bp.route("", methods=["GET"])
@require_employee
def get_orders():
    """Get list of orders"""
    if not g.current_user.tenant_id:
        return jsonify({"message": "User must belong to a tenant"}), 403
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    table_number = request.args.get('table_number', type=int)
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    session = get_session()
    try:
        query = session.query(OrderModel).filter(
            OrderModel.tenant_id == g.current_user.tenant_id
        )
        
        if table_number:
            query = query.filter(OrderModel.table_number == table_number)
        
        if status:
            query = query.filter(OrderModel.status == OrderStatus(status))
        
        if from_date:
            query = query.filter(OrderModel.created_at >= datetime.fromisoformat(from_date))
        
        if to_date:
            query = query.filter(OrderModel.created_at <= datetime.fromisoformat(to_date))
        
        total = query.count()
        orders = query.order_by(OrderModel.created_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return jsonify({
            "data": {
                "items": [{
                    "id": o.id,
                    "tenant_id": o.tenant_id,
                    "table_number": o.table_number,
                    "guest_id": o.guest_id,
                    "dish_snapshot_id": o.dish_snapshot_id,
                    "quantity": o.quantity,
                    "notes": o.notes,
                    "status": o.status.value,
                    "order_handler_id": o.order_handler_id,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                    "updated_at": o.updated_at.isoformat() if o.updated_at else None
                } for o in orders],
                "total": total
            },
            "message": "Lấy danh sách đơn hàng thành công!"
        }), 200
    finally:
        session.close()


@order_bp.route("/<int:order_id>", methods=["GET"])
@require_employee
def get_order(order_id):
    """Get order by ID"""
    session = get_session()
    try:
        order = session.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            return jsonify({"message": "Order not found"}), 404
        
        # Check tenant access
        if order.tenant_id != g.current_user.tenant_id:
            return jsonify({"message": "Access denied"}), 403
        
        return jsonify({
            "data": {
                "id": order.id,
                "tenant_id": order.tenant_id,
                "table_number": order.table_number,
                "guest_id": order.guest_id,
                "dish_snapshot_id": order.dish_snapshot_id,
                "quantity": order.quantity,
                "notes": order.notes,
                "status": order.status.value,
                "order_handler_id": order.order_handler_id,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None
            },
            "message": "Lấy đơn hàng thành công!"
        }), 200
    finally:
        session.close()


@order_bp.route("/<int:order_id>", methods=["PUT"])
@require_employee
def update_order(order_id):
    """Update order"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        order = session.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            return jsonify({"message": "Order not found"}), 404
        
        # Check tenant access
        if order.tenant_id != g.current_user.tenant_id:
            return jsonify({"message": "Access denied"}), 403
        
        # Update fields
        if 'status' in data:
            order.status = OrderStatus(data['status'])
        if 'order_handler_id' in data:
            order.order_handler_id = data['order_handler_id']
        else:
            order.order_handler_id = g.current_user.id
        
        session.commit()
        session.refresh(order)
        
        return jsonify({
            "data": {
                "id": order.id,
                "status": order.status.value,
                "order_handler_id": order.order_handler_id
            },
            "message": "Cập nhật đơn hàng thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@order_bp.route("/pay", methods=["POST"])
@require_employee
def pay_orders():
    """Pay orders for a table"""
    if not g.current_user.tenant_id:
        return jsonify({"message": "User must belong to a tenant"}), 403
    
    data = request.get_json()
    if not data or 'table_number' not in data:
        return jsonify({"message": "Invalid request"}), 400
    
    table_number = data['table_number']
    
    session = get_session()
    try:
        # Get unpaid orders for table
        orders = session.query(OrderModel).filter(
            OrderModel.tenant_id == g.current_user.tenant_id,
            OrderModel.table_number == table_number,
            OrderModel.status != OrderStatus.PAID
        ).all()
        
        if not orders:
            return jsonify({"message": "No unpaid orders found for this table"}), 404
        
        # Update orders to paid
        for order in orders:
            order.status = OrderStatus.PAID
            order.order_handler_id = g.current_user.id
            
            # Update customer history if order has customer_id
            if order.guest_id:
                # Check if guest is actually a customer
                from app.models.guest_model import GuestModel
                guest = session.query(GuestModel).filter(GuestModel.id == order.guest_id).first()
                # If guest has customer_id, update history
                # For now, we'll skip guest orders
                pass
        
        session.commit()
        
        # Update customer history for customer orders
        for order in orders:
            if hasattr(order, 'customer_id') and order.customer_id:
                from app.services.customer_service import update_customer_history_from_order
                update_customer_history_from_order(order.id, order.customer_id)
        
        return jsonify({
            "data": [{
                "id": o.id,
                "status": o.status.value,
                "order_handler_id": o.order_handler_id
            } for o in orders],
            "message": f"Thanh toán thành công {len(orders)} đơn!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()

