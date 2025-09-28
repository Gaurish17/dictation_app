#!/usr/bin/env python3
"""
Startup Admin Fix - Creates admin accounts on every app startup
For Render deployments where SQLite doesn't persist
"""

import os
import sys
import hashlib
from datetime import datetime, timezone

def hash_password(password):
    """Hash password using SHA256 (same as in app.py)"""
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_admin_accounts():
    """Ensure admin accounts exist - run on every startup"""
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import Flask app components
        from app import app, db, User
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Check if admin accounts exist
            admin_exists = User.query.filter_by(username='admin').first()
            
            if not admin_exists:
                admin_user = User(
                    username='admin',
                    password_hash=hash_password('admin123'),
                    role='admin',
                    is_active=True,
                    is_locked=False,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(admin_user)
                print("✅ Created admin account")
            
            # Convert any existing superuser accounts to admin
            superuser_accounts = User.query.filter_by(role='superuser').all()
            for user in superuser_accounts:
                user.role = 'admin'
                print(f"✅ Converted {user.username} from superuser to admin")
            
            db.session.commit()
            print("💾 Admin accounts ensured")
            
            return True
            
    except Exception as e:
        print(f"❌ Error ensuring admin accounts: {e}")
        return False

if __name__ == "__main__":
    ensure_admin_accounts()
