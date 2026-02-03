#!/usr/bin/env python3
"""
Migration script to add admission_request table to the database.
This adds support for new user admission requests feature.
"""

import sys
import os
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def migrate_admission_requests():
    """Add admission_request table to database"""
    with app.app_context():
        try:
            print("🔄 Starting admission_request table migration...")
            
            # Check if table already exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'admission_request' in existing_tables:
                print("✅ admission_request table already exists!")
                return True
            
            # Create the admission_request table
            print("📝 Creating admission_request table...")
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS admission_request (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(200) NOT NULL,
                state VARCHAR(100) NOT NULL,
                district VARCHAR(100) NOT NULL,
                contact_number VARCHAR(20) NOT NULL,
                date_of_birth DATE NOT NULL,
                purpose TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed_at DATETIME,
                processed_by INTEGER,
                notes TEXT,
                FOREIGN KEY (processed_by) REFERENCES user (id)
            )
            """
            
            db.session.execute(text(create_table_sql))
            db.session.commit()
            
            print("✅ Successfully created admission_request table!")
            
            # Verify table was created
            inspector = db.inspect(db.engine)
            if 'admission_request' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('admission_request')]
                print(f"✅ Table verified with columns: {', '.join(columns)}")
                return True
            else:
                print("❌ Table creation verification failed!")
                return False
                
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Admission Request Table Migration")
    print("=" * 60)
    
    success = migrate_admission_requests()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Migration failed! Please check the errors above.")
        print("=" * 60)
        sys.exit(1)