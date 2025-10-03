#!/usr/bin/env python3
"""
WSGI Configuration for Hostinger Deployment
Production entry point for the Flask dictation app
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment to production
os.environ.setdefault('FLASK_ENV', 'production')

# Load environment variables from production file
from dotenv import load_dotenv

# Try to load production environment file first
env_files = ['.env.production', '.env']
for env_file in env_files:
    env_path = project_root / env_file
    if env_path.exists():
        load_dotenv(env_path)
        break

# Import the Flask application
try:
    from app import app as application
    
    # Ensure database tables are created
    with application.app_context():
        from app import db, ensure_admin_accounts_startup
        try:
            db.create_all()
            ensure_admin_accounts_startup()
            print("✅ Database initialized successfully for production")
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
    
    print("🚀 Flask application loaded successfully for production")
    
except Exception as e:
    print(f"❌ Error loading Flask application: {e}")
    # Create a simple error application
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"Application startup error: {e}", 500

# For debugging in production (remove in final deployment)
if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=8000)
