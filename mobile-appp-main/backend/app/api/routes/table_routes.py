from flask import Blueprint, jsonify, request
from app.models.table_model import TableModel
from app.infrastructure.databases import get_session

bp = Blueprint("table", __name__)


@bp.route("/tables/<int:table_id>", methods=["GET"])
def get_table_by_id(table_id):
    """
    Lấy thông tin bàn theo ID
    """
    session = get_session()
    try:
        table = session.query(TableModel).filter(
            TableModel.id == table_id
        ).first()

        if not table:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy bàn"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": table.id,
                "number": table.number,
                "status": table.status,
                "tenantId": table.tenant_id
            }
        }), 200
    finally:
        session.close()


@bp.route("/tables/token/<string:token>", methods=["GET"])
def get_table_by_token(token):
    """
    Lấy thông tin bàn qua QR token
    (dùng trước khi guest login)
    """
    session = get_session()
    try:
        table = session.query(TableModel).filter(
            TableModel.token == token
        ).first()

        if not table:
            return jsonify({
                "success": False,
                "message": "QR không hợp lệ"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": table.id,
                "number": table.number,
                "status": table.status,
                "tenantId": table.tenant_id
            }
        }), 200
    finally:
        session.close()
