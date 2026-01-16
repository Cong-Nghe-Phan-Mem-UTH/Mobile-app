"""
QR Code routes - Quét mã QR menu
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.databases import get_session
from app.models.table_model import TableModel
from app.models.tenant_model import TenantModel

qr_bp = Blueprint("qr", __name__)


@qr_bp.route("/scan", methods=["POST"])
def scan_qr_code():
    """Scan QR code to get restaurant and table info"""
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({"message": "Invalid request"}), 400
    
    token = data.get('token')
    
    session = get_session()
    try:
        # Find table by token
        table = session.query(TableModel).filter(
            TableModel.token == token
        ).first()
        
        if not table:
            return jsonify({"message": "Invalid QR code"}), 404
        
        # Get restaurant info
        restaurant = session.query(TenantModel).filter(
            TenantModel.id == table.tenant_id
        ).first()
        
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404
        
        return jsonify({
            "data": {
                "restaurant": {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "slug": restaurant.slug,
                    "logo": restaurant.logo,
                    "address": restaurant.address
                },
                "table": {
                    "number": table.number,
                    "capacity": table.capacity,
                    "status": table.status.value
                },
                "token": token
            },
            "message": "Quét mã QR thành công!"
        }), 200
    finally:
        session.close()

