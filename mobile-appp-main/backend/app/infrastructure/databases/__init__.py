"""
Database initialization and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.infrastructure.databases.base import Base
from app.config import Config

engine = None
SessionLocal = None

def init_db(app):
    """Initialize database"""
    global engine, SessionLocal
    
    database_uri = app.config['DATABASE_URI']
    
    # Add connection timeout for PostgreSQL
    if 'postgresql' in database_uri.lower() and 'connect_timeout' not in database_uri.lower():
        separator = '&' if '?' in database_uri else '?'
        database_uri = f"{database_uri}{separator}connect_timeout=10"
    
    engine = create_engine(
        database_uri,
        echo=app.config.get('DEBUG', False),
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20
    )
    
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    
    # Import all models to ensure they are registered
    from app.models import (
        tenant_model,
        branch_model,
        account_model,
        dish_model,
        table_model,
        order_model,
        guest_model,
        discount_model,
        review_model,
        reservation_model,
        refresh_token_model,
        socket_model,
        customer_model,
        customer_history_model
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    return SessionLocal

def get_session():
    """Get database session"""
    return SessionLocal()

