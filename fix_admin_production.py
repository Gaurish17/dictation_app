#!/usr/bin/env python3
"""
Script to reset admin credentials in production database
"""
import sqlite3
from werkzeug.security import generate_password_hash

# Production database path
DB_PATH = 'dictation_app.db'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Stenographix@03102025'

def reset_admin_password():
    """Reset admin password in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate password hash
        password_hash = generate_password_hash(ADMIN_PASSWORD)
        
        # Check if admin exists
        cursor.execute("SELECT id FROM admin_users WHERE username = ?", (ADMIN_USERNAME,))
        admin = cursor.fetchone()
        
        if admin:
            # Update existing admin
            cursor.execute("""
                UPDATE admin_users 
                SET password_hash = ?
                WHERE username = ?
            """, (password_hash, ADMIN_USERNAME))
            print(f"✅ Admin password updated for username: {ADMIN_USERNAME}")
        else:
            # Create new admin
            cursor.execute("""
                INSERT INTO admin_users (username, password_hash, email, is_super_admin, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (ADMIN_USERNAME, password_hash, 'admin@localhost', 1))
            print(f"✅ Admin user created: {ADMIN_USERNAME}")
        
        conn.commit()
        conn.close()
        print(f"✅ Admin credentials set successfully!")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Password: {ADMIN_PASSWORD}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    reset_admin_password()