from flask import Blueprint, jsonify, g
from app.api.decorators.guest_auth_required import guest_auth_required
from app.models.order_model import OrderModel
from app.models.dish_model import DishModel

bp = Blueprint("history", __name__)


@bp.route("/history/orders", methods=["GET"])
@guest_auth_required
def get_order_history():
    session = g.session
    guest = g.guest

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
