"""
Dish routes
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.databases import get_session
from app.models.dish_model import DishModel, DishStatus
from app.api.decorators import require_employee
from flask import g

dish_bp = Blueprint("dish", __name__)


@dish_bp.route("", methods=["GET"])
def get_dishes():
    """Get list of dishes"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    tenant_id = request.args.get('tenant_id', type=int)
    
    session = get_session()
    try:
        query = session.query(DishModel)
        
        if tenant_id:
            query = query.filter(DishModel.tenant_id == tenant_id)
        
        if category:
            query = query.filter(DishModel.category == category)
        
        if status:
            query = query.filter(DishModel.status == DishStatus(status))
        
        total = query.count()
        dishes = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            "data": {
                "items": [{
                    "id": d.id,
                    "tenant_id": d.tenant_id,
                    "name": d.name,
                    "price": d.price,
                    "description": d.description,
                    "image": d.image,
                    "category": d.category,
                    "status": d.status.value,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                    "updated_at": d.updated_at.isoformat() if d.updated_at else None
                } for d in dishes],
                "total": total,
                "page": page,
                "limit": limit
            },
            "message": "Lấy danh sách món ăn thành công!"
        }), 200
    finally:
        session.close()


@dish_bp.route("/<int:dish_id>", methods=["GET"])
def get_dish(dish_id):
    """Get dish by ID"""
    session = get_session()
    try:
        dish = session.query(DishModel).filter(DishModel.id == dish_id).first()
        
        if not dish:
            return jsonify({"message": "Dish not found"}), 404
        
        return jsonify({
            "data": {
                "id": dish.id,
                "tenant_id": dish.tenant_id,
                "name": dish.name,
                "price": dish.price,
                "description": dish.description,
                "image": dish.image,
                "category": dish.category,
                "status": dish.status.value,
                "created_at": dish.created_at.isoformat() if dish.created_at else None,
                "updated_at": dish.updated_at.isoformat() if dish.updated_at else None
            },
            "message": "Lấy thông tin món ăn thành công!"
        }), 200
    finally:
        session.close()


@dish_bp.route("", methods=["POST"])
@require_employee
def create_dish():
    """Create a new dish"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    if not g.current_user.tenant_id:
        return jsonify({"message": "User must belong to a tenant"}), 403
    
    session = get_session()
    try:
        dish = DishModel(
            tenant_id=g.current_user.tenant_id,
            name=data.get('name'),
            price=data.get('price'),
            description=data.get('description'),
            image=data.get('image'),
            category=data.get('category'),
            status=DishStatus(data.get('status', 'Available'))
        )
        
        session.add(dish)
        session.commit()
        session.refresh(dish)
        
        return jsonify({
            "data": {
                "id": dish.id,
                "tenant_id": dish.tenant_id,
                "name": dish.name,
                "price": dish.price,
                "description": dish.description,
                "image": dish.image,
                "category": dish.category,
                "status": dish.status.value
            },
            "message": "Tạo món ăn thành công!"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@dish_bp.route("/<int:dish_id>", methods=["PUT"])
@require_employee
def update_dish(dish_id):
    """Update a dish"""
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        dish = session.query(DishModel).filter(DishModel.id == dish_id).first()
        
        if not dish:
            return jsonify({"message": "Dish not found"}), 404
        
        # Check tenant access
        if dish.tenant_id != g.current_user.tenant_id:
            return jsonify({"message": "Access denied"}), 403
        
        # Update fields
        if 'name' in data:
            dish.name = data['name']
        if 'price' in data:
            dish.price = data['price']
        if 'description' in data:
            dish.description = data['description']
        if 'image' in data:
            dish.image = data['image']
        if 'category' in data:
            dish.category = data['category']
        if 'status' in data:
            dish.status = DishStatus(data['status'])
        
        session.commit()
        session.refresh(dish)
        
        return jsonify({
            "data": {
                "id": dish.id,
                "tenant_id": dish.tenant_id,
                "name": dish.name,
                "price": dish.price,
                "description": dish.description,
                "image": dish.image,
                "category": dish.category,
                "status": dish.status.value
            },
            "message": "Cập nhật món ăn thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@dish_bp.route("/<int:dish_id>", methods=["DELETE"])
@require_employee
def delete_dish(dish_id):
    """Delete a dish"""
    session = get_session()
    try:
        dish = session.query(DishModel).filter(DishModel.id == dish_id).first()
        
        if not dish:
            return jsonify({"message": "Dish not found"}), 404
        
        # Check tenant access
        if dish.tenant_id != g.current_user.tenant_id:
            return jsonify({"message": "Access denied"}), 403
        
        session.delete(dish)
        session.commit()
        
        return jsonify({"message": "Xóa món ăn thành công!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()

