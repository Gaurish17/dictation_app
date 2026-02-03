#!/usr/bin/env python3
"""
Database migration script to add device registration columns to User table.
This implements the single registered device login system.
"""

import os
import sys
from datetime import datetime, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import config

# Initialize Flask app for database context
app = Flask(__name__)

# Configure app based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize database
db = SQLAlchemy(app)

def migrate_device_registration():
    """Add device registration columns to User table"""
    print("🔄 Starting device registration migration...")
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('user')]
            
            columns_to_add = []
            
            # Define new columns for device registration
            new_columns = {
                'registered_device_id': 'VARCHAR(64)',  # SHA-256 hash of device fingerprint
                'first_login_date': 'DATETIME',         # When device was first registered
                'last_login_date': 'DATETIME',          # Last successful login
                'device_reset_count': 'INTEGER DEFAULT 0'  # Number of times admin reset device
            }
            
            # Check which columns need to be added
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    columns_to_add.append((column_name, column_type))
            
            if not columns_to_add:
                print("✅ All device registration columns already exist")
                return True
            
            # Add missing columns
            for column_name, column_type in columns_to_add:
                try:
                    alter_sql = f"ALTER TABLE user ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(alter_sql))
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"ℹ️  Column {column_name} already exists, skipping...")
                    else:
                        print(f"❌ Error adding column {column_name}: {e}")
                        raise
            
            # Commit the changes
            db.session.commit()
            print("✅ Device registration migration completed successfully")
            
            # Show final table structure
            print("\n📋 Updated User table columns:")
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('user')
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            required_columns = [
                'registered_device_id',
                'first_login_date', 
                'last_login_date',
                'device_reset_count'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns present")
                return True
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False

if __name__ == "__main__":
    print("=== Device Registration Migration ===")
    
    # Run migration
    if migrate_device_registration():
        if verify_migration():
            print("\n🎉 Device registration system migration completed successfully!")
            print("\nNext steps:")
            print("1. Update app.py with device binding logic")
            print("2. Add admin device reset functionality")
            print("3. Deploy to production")
        else:
            print("\n❌ Migration verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)