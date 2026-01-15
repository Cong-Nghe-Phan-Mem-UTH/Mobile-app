# src/api/routes/guest_routes.py

from flask import Blueprint, request, jsonify, g
from functools import wraps
from datetime import datetime
import logging

from app.infrastructure.databases import get_session

from app.models.guest_model import GuestModel
from app.models.table_model import TableModel
from app.models.dish_model import DishModel, DishSnapshotModel, DishStatus
from app.models.order_model import OrderModel, OrderStatus

from app.utils.jwt import create_access_token, verify_access_token
from app.utils.errors import EntityError, AuthError, NotFoundError

logger = logging.getLogger(__name__)

bp = Blueprint("guest", __name__)


# AUTH DECORATOR
def guest_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthError("Vui lòng đăng nhập")

        token = auth_header.split(" ")[1]
        payload = verify_access_token(token)

        if not payload or "guestId" not in payload:
            raise AuthError("Token không hợp lệ hoặc đã hết hạn")

        session = get_session()
        try:
            guest = session.query(GuestModel).filter(
                GuestModel.id == payload["guestId"]
            ).first()

            if not guest:
                raise AuthError("Phiên đăng nhập đã hết hạn")

            g.session = session
            g.guest = guest
            g.guest_id = guest.id
            g.table_number = guest.table_number
            g.tenant_id = guest.tenant_id

            return f(*args, **kwargs)
        finally:
            session.close()

    return decorated


# AUTH
@bp.route("/login", methods=["POST"])
def guest_login():
    session = get_session()
    try:
        data = request.get_json() or {}
        table_token = data.get("table_token")
        name = data.get("name", "Khách")

        if not table_token:
            raise EntityError("Thiếu table_token")

        table = session.query(TableModel).filter(
            TableModel.token == table_token
        ).first()

        if not table:
            raise NotFoundError("QR không hợp lệ")

        # Không tạo guest trùng cho cùng bàn
        guest = session.query(GuestModel).filter(
            GuestModel.table_number == table.number,
            GuestModel.tenant_id == table.tenant_id
        ).first()

        if not guest:
            guest = GuestModel(
                tenant_id=table.tenant_id,
                table_number=table.number,
                name=name,
                created_at=datetime.utcnow()
            )
            session.add(guest)
            session.commit()
            session.refresh(guest)
        else:
            guest.name = name
            guest.updated_at = datetime.utcnow()
            session.commit()

        access_token = create_access_token(
            data={"guestId": guest.id, "tableNumber": guest.table_number},
            is_guest=True
        )

        return jsonify({
            "success": True,
            "message": "Đăng nhập thành công",
            "data": {
                "guest": {
                    "id": guest.id,
                    "name": guest.name,
                    "tableNumber": guest.table_number
                },
                "accessToken": access_token
            }
        }), 200

    finally:
        session.close()


# ORDERS - CREATE
@bp.route("/orders", methods=["POST"])
@guest_auth_required
def create_orders():
    data = request.get_json() or {}
    orders_data = data.get("orders")

    if not orders_data:
        raise EntityError("Vui lòng chọn ít nhất 1 món")

    session = g.session
    guest = g.guest

    created_orders = []

    for item in orders_data:
        dish_id = item.get("dish_id")
        quantity = item.get("quantity", 1)
        notes = item.get("notes", "")

        dish = session.query(DishModel).filter(
            DishModel.id == dish_id,
            DishModel.status == DishStatus.AVAILABLE
        ).first()

        if not dish:
            continue

        # Tạo snapshot
        snapshot = DishSnapshotModel(
            dish_id=dish.id,
            name=dish.name,
            price=dish.price,
            description=dish.description,
            image=dish.image,
            category=dish.category,
            status=dish.status.value
        )
        session.add(snapshot)
        session.flush()

        order = OrderModel(
            tenant_id=guest.tenant_id,
            guest_id=guest.id,
            table_number=guest.table_number,
            dish_snapshot_id=snapshot.id,
            quantity=quantity,
            notes=notes,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow()
        )
        session.add(order)
        created_orders.append(order)

    if not created_orders:
        raise EntityError("Không có món hợp lệ để đặt")

    session.commit()

    return jsonify({
        "success": True,
        "message": "Đặt món thành công",
        "data": {
            "orderIds": [o.id for o in created_orders],
            "totalOrders": len(created_orders)
        }
    }), 201


# ORDERS - LIST
@bp.route("/orders", methods=["GET"])
@guest_auth_required
def get_orders():
    session = g.session
    guest = g.guest

    orders = session.query(OrderModel).filter(
        OrderModel.guest_id == guest.id
    ).order_by(OrderModel.created_at.desc()).all()

    items = []
    for order in orders:
        snapshot = order.dish_snapshot
        items.append({
            "id": order.id,
            "status": order.status.value,
            "quantity": order.quantity,
            "notes": order.notes,
            "createdAt": order.created_at.isoformat(),
            "dish": {
                "name": snapshot.name,
                "price": snapshot.price,
                "image": snapshot.image
            },
            "totalPrice": snapshot.price * order.quantity
        })

    return jsonify({
        "success": True,
        "data": {
            "items": items,
            "total": len(items)
        }
    }), 200


__all__ = ["bp"]
