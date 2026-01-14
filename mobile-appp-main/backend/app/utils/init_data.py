"""
Initialize default data
"""
from app.infrastructure.databases import get_session
from app.models.account_model import AccountModel, AccountRole
from app.utils.crypto import hash_password
from app.config import Config


def init_admin_account():
    """Initialize default admin account if not exists"""
    session = get_session()
    try:
        # Check if admin exists
        admin = session.query(AccountModel).filter(
            AccountModel.email == Config.INITIAL_EMAIL_OWNER
        ).first()
        
        if not admin:
            hashed_password = hash_password(Config.INITIAL_PASSWORD_OWNER)
            admin = AccountModel(
                name="Admin",
                email=Config.INITIAL_EMAIL_OWNER,
                password=hashed_password,
                role=AccountRole.ADMIN,
                tenant_id=None  # Admin has no tenant
            )
            session.add(admin)
            session.commit()
            print(f"✅ Created default admin account: {Config.INITIAL_EMAIL_OWNER}")
        else:
            print(f"ℹ️  Admin account already exists: {Config.INITIAL_EMAIL_OWNER}")
    except Exception as e:
        print(f"❌ Error initializing admin account: {e}")
        session.rollback()
    finally:
        session.close()

