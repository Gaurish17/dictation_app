"""
Migration script to add email column to admission_request table
Run this to update existing database with the new email field
"""

import sqlite3
from datetime import datetime

def migrate_database(db_path='instance/app.db'):
    """Add email column to admission_request table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if email column already exists
        cursor.execute("PRAGMA table_info(admission_request)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Adding 'email' column to admission_request table...")
            
            # Add email column (nullable initially for existing records)
            cursor.execute('''
                ALTER TABLE admission_request 
                ADD COLUMN email VARCHAR(120)
            ''')
            
            # Update existing records with a placeholder email
            cursor.execute('''
                UPDATE admission_request 
                SET email = contact_number || '@placeholder.com'
                WHERE email IS NULL
            ''')
            
            conn.commit()
            print("✅ Successfully added 'email' column to admission_request table")
            print("✅ Updated existing records with placeholder emails")
        else:
            print("ℹ️  'email' column already exists in admission_request table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("Database Migration: Add Email to Admission Requests")
    print("="*60)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📝 Note: Existing admission requests have placeholder emails")
        print("   Format: contact_number@placeholder.com")
    else:
        print("\n❌ Migration failed!")
    
    print("="*60)