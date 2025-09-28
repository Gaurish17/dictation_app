#!/usr/bin/env python3
"""
Render SQLite Admin Fix Script
For fixing admin login issues on Render with SQLite
"""

import os
import sys
import hashlib
import sqlite3
from datetime import datetime, timezone

def hash_password(password):
    """Hash password using SHA256 (same as in app.py)"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_accounts_render():
    """Create admin accounts specifically for Render environment"""
    
    print("🔧 Render SQLite Admin Fix")
    print("==========================")
    
    # Render typically puts SQLite in the instance folder
    possible_db_paths = [
        '/opt/render/project/src/instance/dictation_app.db',
        '/opt/render/project/src/dictation_app.db',
        './instance/dictation_app.db',
        './dictation_app.db',
        'dictation_app.db'
    ]
    
    db_found = False
    
    for db_path in possible_db_paths:
        try:
            # Ensure directory exists
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"📁 Created directory: {db_dir}")
            
            print(f"🔍 Trying database: {db_path}")
            
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create user table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(120) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'student',
                    subscription_start DATETIME,
                    subscription_end DATETIME,
                    device_id VARCHAR(100),
                    is_active BOOLEAN DEFAULT 1,
                    is_locked BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    last_login DATETIME,
                    last_activity DATETIME
                )
            ''')
            
            print(f"✅ Connected to database: {db_path}")
            db_found = True
            
            # Check existing admin users
            cursor.execute("SELECT username, role, is_active FROM user WHERE role = 'admin';")
            existing_admins = cursor.fetchall()
            
            print(f"📋 Existing admin accounts: {len(existing_admins)}")
            for admin in existing_admins:
                print(f"   - {admin[0]} (role: {admin[1]}, active: {admin[2]})")
            
            # Delete existing admin accounts to avoid conflicts
            cursor.execute("DELETE FROM user WHERE username = 'admin';")
            print("🗑️  Removed existing admin account")
            
            # Create fresh admin accounts
            admin_password_hash = hash_password('admin123')
            super_password_hash = hash_password('super123')
            current_time = datetime.now(timezone.utc).isoformat()
            
            # Insert admin account
            cursor.execute("""
                INSERT INTO user (username, password_hash, role, is_active, is_locked, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', admin_password_hash, 'admin', 1, 0, current_time))
            
            # Convert any existing superuser accounts to admin
            cursor.execute("UPDATE user SET role = 'admin' WHERE role = 'superuser';")
            print("🔄 Converted any existing superuser accounts to admin")
            
            conn.commit()
            print("💾 Admin accounts created successfully!")
            
            # Verify accounts were created
            cursor.execute("SELECT username, role, is_active FROM user WHERE role = 'admin';")
            new_admins = cursor.fetchall()
            
            print(f"\n✅ Verified {len(new_admins)} admin accounts:")
            for admin in new_admins:
                print(f"   - {admin[0]} (role: {admin[1]}, active: {admin[2]})")
            
            # Show all users for debugging
            cursor.execute("SELECT COUNT(*) FROM user;")
            total_users = cursor.fetchone()[0]
            print(f"\n📊 Total users in database: {total_users}")
            
            conn.close()
            
            print(f"\n🎉 SUCCESS! Admin accounts fixed in: {db_path}")
            print("\n🔑 Login Credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Only admin role available - superuser role has been eliminated")
            print("\n🌐 Login URL: /admin-login")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ SQLite error with {db_path}: {e}")
            continue
        except Exception as e:
            print(f"❌ General error with {db_path}: {e}")
            continue
    
    if not db_found:
        print("❌ Could not find or create SQLite database")
        print("💡 Render Environment Info:")
        print(f"   - Current directory: {os.getcwd()}")
        print(f"   - Directory contents: {os.listdir('.')}")
        if os.path.exists('instance'):
            print(f"   - Instance directory: {os.listdir('instance')}")
        return False
    
    return True

def show_render_env():
    """Show Render environment information"""
    print("🔍 Render Environment:")
    print(f"   - Working Directory: {os.getcwd()}")
    print(f"   - Python Version: {sys.version}")
    print(f"   - RENDER: {os.environ.get('RENDER', 'Not set')}")
    print(f"   - FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
    
    # Show directory structure
    if os.path.exists('.'):
        print(f"   - App directory contents:")
        for item in os.listdir('.'):
            print(f"     - {item}")
    
    if os.path.exists('instance'):
        print(f"   - Instance directory contents:")
        for item in os.listdir('instance'):
            print(f"     - {item}")

if __name__ == "__main__":
    show_render_env()
    print()
    
    success = create_admin_accounts_render()
    
    if success:
        print("\n🎉 Render admin fix completed successfully!")
        print("💡 Try logging in now with the credentials above.")
    else:
        print("\n❌ Failed to fix admin accounts on Render")
        print("💡 Next steps:")
        print("   1. Redeploy your service on Render")
        print("   2. Check Render logs for errors")
        print("   3. Ensure SQLite file has write permissions")
