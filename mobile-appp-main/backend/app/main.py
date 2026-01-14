"""
Main entry point for Flask application
"""
from app.create_app import create_app
import os
import sys

app = create_app()

if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get('PORT', 4000))
    # Disable debug in production
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    
    # Print startup info
    print(f"🚀 Starting Flask app on port {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Environment: {'Production' if app.config.get('PRODUCTION') else 'Development'}")
    print(f"🔗 API URL: {app.config.get('API_URL')}")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=debug)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
