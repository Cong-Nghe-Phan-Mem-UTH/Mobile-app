from flask import Blueprint, request, jsonify, g
from app.infrastructure.databases import get_session
from app.models.guest_model import GuestModel
from app.models.order_model import OrderModel
from app.models.dish_model import DishModel
from app.utils.jwt import verify_access_token

bp = Blueprint("history", __name__)


def guest_auth():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, jsonify({
            "success": False,
            "message": "Vui lòng đăng nhập"
        }), 401
    token = auth_header.split(" ")[1]
    payload = verify_access_token(token)
    if not payload or "guestId" not in payload:
        return None, jsonify({
            "success": False,
            "message": "Token không hợp lệ"
        }), 401
    session = get_session()
    guest = session.query(GuestModel).filter(
        GuestModel.id == payload["guestId"]
    ).first()
    if not guest:
        session.close()
        return None, jsonify({
            "success": False,
            "message": "Phiên đăng nhập đã hết hạn"
        }), 401
    g.session = session
    g.guest = guest
    return guest, None, None
@bp.route("/history/orders", methods=["GET"])
def get_order_history():
    guest, error_response, status_code = guest_auth()
    if error_response:
        return error_response, status_code
    session = g.session
    try:
        orders = (
            session.query(OrderModel, DishModel)
            .join(DishModel, OrderModel.dish_id == DishModel.id)
            .filter(OrderModel.guest_id == guest.id)
            .order_by(OrderModel.created_at.desc())
            .all()
        )
        data = []
        for order, dish in orders:
            data.append({
                "orderId": order.id,
                "dishName": dish.name,
                "quantity": order.quantity,
                "notes": order.notes,
                "price": dish.price,
                "totalPrice": dish.price * order.quantity,
                "createdAt": order.created_at.isoformat()
            })
        return jsonify({
            "success": True,
            "data": data
        }), 200
    finally:
        session.close()
