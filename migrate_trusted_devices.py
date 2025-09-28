#!/usr/bin/env python3
"""
Migration Script: Add TrustedDevice table for Single Device/IP Login Restriction
This script creates the TrustedDevice table if it doesn't exist.
"""

import os
import sys
from datetime import datetime, timezone

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, TrustedDevice, User

def migrate_trusted_devices():
    """Create TrustedDevice table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if TrustedDevice table exists by trying to query it
            try:
                TrustedDevice.query.limit(1).all()
                print("✅ TrustedDevice table already exists")
                return True
            except Exception:
                # Table doesn't exist, create it
                print("📋 Creating TrustedDevice table...")
                
                # Create all tables (this will only create missing ones)
                db.create_all()
                
                print("✅ TrustedDevice table created successfully")
                
                # Verify the table was created
                try:
                    count = TrustedDevice.query.count()
                    print(f"📊 TrustedDevice table verified: {count} records")
                    return True
                except Exception as e:
                    print(f"❌ Error verifying TrustedDevice table: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def show_table_info():
    """Show information about the TrustedDevice table"""
    with app.app_context():
        try:
            # Show table structure info
            print("\n📋 TrustedDevice Table Structure:")
            print("- id: Primary Key")
            print("- user_id: Foreign Key to User table")
            print("- device_fingerprint: Unique device identifier")
            print("- ip_address: Client IP address")
            print("- user_agent: Browser/device information")
            print("- first_login_at: When device was first registered")
            print("- last_used_at: Last time device was used")
            print("- is_active: Whether device is currently trusted")
            print("- locked_reason: Reason for deactivation")
            print("- created_at: Record creation timestamp")
            
            # Count existing records
            trusted_devices_count = TrustedDevice.query.count()
            print(f"\n📊 Current Statistics:")
            print(f"- Total TrustedDevice records: {trusted_devices_count}")
            
            if trusted_devices_count > 0:
                active_devices = TrustedDevice.query.filter_by(is_active=True).count()
                print(f"- Active trusted devices: {active_devices}")
                print(f"- Inactive trusted devices: {trusted_devices_count - active_devices}")
            
        except Exception as e:
            print(f"❌ Error showing table info: {e}")

if __name__ == '__main__':
    print("🚀 Starting TrustedDevice Migration...")
    print("=" * 50)
    
    if migrate_trusted_devices():
        show_table_info()
        print("=" * 50)
        print("✅ Migration completed successfully!")
        print("\n🔐 Single Device/IP Login Restriction is now active:")
        print("• Students can only login from one device/IP combination")
        print("• First login registers the trusted environment")
        print("• Different device/IP attempts will lock the account")
        print("• Only admins can unlock accounts and manage trusted devices")
    else:
        print("=" * 50)
        print("❌ Migration failed!")
        sys.exit(1)