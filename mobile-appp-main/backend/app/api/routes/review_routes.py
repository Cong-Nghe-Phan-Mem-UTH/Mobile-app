"""
Review routes - Restaurant reviews
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.databases import get_session
from app.models.review_model import ReviewModel
from app.models.tenant_model import TenantModel
from app.models.customer_model import CustomerModel
from app.api.decorators import require_auth
from datetime import datetime

review_bp = Blueprint("review", __name__)


@review_bp.route("/restaurants/<int:restaurant_id>/reviews", methods=["GET"])
def get_restaurant_reviews(restaurant_id):
    """Get reviews for a restaurant"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    session = get_session()
    try:
        reviews = session.query(ReviewModel).filter(
            ReviewModel.tenant_id == restaurant_id
        ).order_by(ReviewModel.created_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return jsonify({
            "data": {
                "items": [{
                    "id": r.id,
                    "customer_id": r.customer_id,
                    "customer_name": session.query(CustomerModel.name).filter(
                        CustomerModel.id == r.customer_id
                    ).scalar() if r.customer_id else "Anonymous",
                    "rating": r.rating,
                    "comment": r.comment,
                    "dish_ratings": r.dish_ratings,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in reviews],
                "total": session.query(ReviewModel).filter(
                    ReviewModel.tenant_id == restaurant_id
                ).count()
            },
            "message": "Lấy danh sách đánh giá thành công!"
        }), 200
    finally:
        session.close()


@review_bp.route("/restaurants/<int:restaurant_id>/reviews", methods=["POST"])
def create_review(restaurant_id):
    """Create a review for a restaurant"""
    # Get customer from token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization required"}), 401
    
    try:
        token = auth_header.split(' ')[1]
        from app.utils.jwt import verify_access_token
        payload = verify_access_token(token)
        
        if not payload or payload.get('role') != 'Customer':
            return jsonify({"message": "Invalid customer token"}), 401
        
        customer_id = payload.get('customer_id')
    except:
        return jsonify({"message": "Invalid token"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        # Check if restaurant exists
        restaurant = session.query(TenantModel).filter(
            TenantModel.id == restaurant_id
        ).first()
        
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404
        
        # Check if customer already reviewed
        existing_review = session.query(ReviewModel).filter(
            ReviewModel.tenant_id == restaurant_id,
            ReviewModel.customer_id == customer_id
        ).first()
        
        if existing_review:
            return jsonify({"message": "You have already reviewed this restaurant"}), 400
        
        # Create review
        review = ReviewModel(
            tenant_id=restaurant_id,
            customer_id=customer_id,
            rating=data.get('rating'),
            comment=data.get('comment'),
            dish_ratings=data.get('dish_ratings')
        )
        session.add(review)
        session.commit()
        session.refresh(review)
        
        return jsonify({
            "data": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat() if review.created_at else None
            },
            "message": "Tạo đánh giá thành công!"
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@review_bp.route("/reviews/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    """Update a review"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization required"}), 401
    
    try:
        token = auth_header.split(' ')[1]
        from app.utils.jwt import verify_access_token
        payload = verify_access_token(token)
        
        if not payload or payload.get('role') != 'Customer':
            return jsonify({"message": "Invalid customer token"}), 401
        
        customer_id = payload.get('customer_id')
    except:
        return jsonify({"message": "Invalid token"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    session = get_session()
    try:
        review = session.query(ReviewModel).filter(
            ReviewModel.id == review_id,
            ReviewModel.customer_id == customer_id
        ).first()
        
        if not review:
            return jsonify({"message": "Review not found"}), 404
        
        # Update fields
        if 'rating' in data:
            review.rating = data['rating']
        if 'comment' in data:
            review.comment = data['comment']
        if 'dish_ratings' in data:
            review.dish_ratings = data['dish_ratings']
        
        session.commit()
        session.refresh(review)
        
        return jsonify({
            "data": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "updated_at": review.updated_at.isoformat() if review.updated_at else None
            },
            "message": "Cập nhật đánh giá thành công!"
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()


@review_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    """Delete a review"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Authorization required"}), 401
    
    try:
        token = auth_header.split(' ')[1]
        from app.utils.jwt import verify_access_token
        payload = verify_access_token(token)
        
        if not payload or payload.get('role') != 'Customer':
            return jsonify({"message": "Invalid customer token"}), 401
        
        customer_id = payload.get('customer_id')
    except:
        return jsonify({"message": "Invalid token"}), 401
    
    session = get_session()
    try:
        review = session.query(ReviewModel).filter(
            ReviewModel.id == review_id,
            ReviewModel.customer_id == customer_id
        ).first()
        
        if not review:
            return jsonify({"message": "Review not found"}), 404
        
        session.delete(review)
        session.commit()
        
        return jsonify({"message": "Xóa đánh giá thành công!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        session.close()
