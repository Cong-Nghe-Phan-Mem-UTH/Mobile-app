"""
Mobile App routes - Restaurant listing, search, recommendations
"""
from flask import Blueprint, request, jsonify
from app.infrastructure.databases import get_session
from app.models.tenant_model import TenantModel, TenantStatus
from app.models.review_model import ReviewModel
from sqlalchemy import func, desc

mobile_bp = Blueprint("mobile", __name__)


@mobile_bp.route("/restaurants", methods=["GET"])
def get_restaurants_list():
    """Get list of restaurants for mobile app"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search')
    min_rating = request.args.get('min_rating', type=float)
    
    session = get_session()
    try:
        query = session.query(TenantModel).filter(
            TenantModel.status == TenantStatus.ACTIVE
        )
        
        # Search by name or address
        if search:
            query = query.filter(
                (TenantModel.name.ilike(f'%{search}%')) |
                (TenantModel.address.ilike(f'%{search}%'))
            )
        
        # Calculate average rating for each restaurant
        restaurants = query.all()
        restaurant_data = []
        
        for restaurant in restaurants:
            # Get average rating
            avg_rating = session.query(func.avg(ReviewModel.rating)).filter(
                ReviewModel.tenant_id == restaurant.id
            ).scalar() or 0.0
            
            # Filter by min_rating if provided
            if min_rating and avg_rating < min_rating:
                continue
            
            # Get review count
            review_count = session.query(func.count(ReviewModel.id)).filter(
                ReviewModel.tenant_id == restaurant.id
            ).scalar() or 0
            
            restaurant_data.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "slug": restaurant.slug,
                "address": restaurant.address,
                "phone": restaurant.phone,
                "logo": restaurant.logo,
                "description": restaurant.description,
                "average_rating": round(float(avg_rating), 1),
                "review_count": review_count
            })
        
        # Sort by rating
        restaurant_data.sort(key=lambda x: x['average_rating'], reverse=True)
        
        # Pagination
        total = len(restaurant_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = restaurant_data[start:end]
        
        return jsonify({
            "data": {
                "items": paginated_data,
                "total": total,
                "page": page,
                "limit": limit
            },
            "message": "Lấy danh sách nhà hàng thành công!"
        }), 200
    finally:
        session.close()


@mobile_bp.route("/restaurants/recommended", methods=["GET"])
def get_recommended_restaurants():
    """Get recommended restaurants (top rated)"""
    limit = request.args.get('limit', 10, type=int)
    
    session = get_session()
    try:
        # Get restaurants with highest ratings
        restaurants = session.query(
            TenantModel,
            func.avg(ReviewModel.rating).label('avg_rating'),
            func.count(ReviewModel.id).label('review_count')
        ).join(
            ReviewModel, TenantModel.id == ReviewModel.tenant_id, isouter=True
        ).filter(
            TenantModel.status == TenantStatus.ACTIVE
        ).group_by(
            TenantModel.id
        ).order_by(
            desc('avg_rating'),
            desc('review_count')
        ).limit(limit).all()
        
        restaurant_data = []
        for restaurant, avg_rating, review_count in restaurants:
            restaurant_data.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "slug": restaurant.slug,
                "address": restaurant.address,
                "phone": restaurant.phone,
                "logo": restaurant.logo,
                "description": restaurant.description,
                "average_rating": round(float(avg_rating or 0), 1),
                "review_count": review_count or 0
            })
        
        return jsonify({
            "data": restaurant_data,
            "message": "Lấy danh sách nhà hàng đề xuất thành công!"
        }), 200
    finally:
        session.close()


@mobile_bp.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def get_restaurant_detail(restaurant_id):
    """Get restaurant detail for mobile app"""
    session = get_session()
    try:
        restaurant = session.query(TenantModel).filter(
            TenantModel.id == restaurant_id,
            TenantModel.status == TenantStatus.ACTIVE
        ).first()
        
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404
        
        # Get average rating and review count
        avg_rating = session.query(func.avg(ReviewModel.rating)).filter(
            ReviewModel.tenant_id == restaurant.id
        ).scalar() or 0.0
        
        review_count = session.query(func.count(ReviewModel.id)).filter(
            ReviewModel.tenant_id == restaurant.id
        ).scalar() or 0
        
        return jsonify({
            "data": {
                "id": restaurant.id,
                "name": restaurant.name,
                "slug": restaurant.slug,
                "address": restaurant.address,
                "phone": restaurant.phone,
                "logo": restaurant.logo,
                "description": restaurant.description,
                "average_rating": round(float(avg_rating), 1),
                "review_count": review_count,
                "directions_url": f"https://www.google.com/maps/search/?api=1&query={restaurant.address}" if restaurant.address else None
            },
            "message": "Lấy thông tin nhà hàng thành công!"
        }), 200
    finally:
        session.close()


@mobile_bp.route("/restaurants/<int:restaurant_id>/directions", methods=["GET"])
def get_restaurant_directions(restaurant_id):
    """Get directions to restaurant (Google Maps URL)"""
    session = get_session()
    try:
        restaurant = session.query(TenantModel).filter(
            TenantModel.id == restaurant_id
        ).first()
        
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404
        
        if not restaurant.address:
            return jsonify({"message": "Restaurant address not available"}), 404
        
        # Generate Google Maps URL
        import urllib.parse
        encoded_address = urllib.parse.quote(restaurant.address)
        directions_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
        
        return jsonify({
            "data": {
                "restaurant_id": restaurant.id,
                "restaurant_name": restaurant.name,
                "address": restaurant.address,
                "directions_url": directions_url,
                "google_maps_url": directions_url
            },
            "message": "Lấy chỉ đường thành công!"
        }), 200
    finally:
        session.close()

