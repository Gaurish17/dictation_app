#!/usr/bin/env python3
"""
Database migration script to add attempt_number column to DictationAttempt table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add attempt_number column to existing database"""
    
    db_path = os.path.join('instance', 'dictation_app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(dictation_attempt)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'attempt_number' in columns:
            print("attempt_number column already exists in dictation_attempt table")
            conn.close()
            return True
        
        print("Adding attempt_number column to dictation_attempt table...")
        
        # Add the new column with default value 1
        cursor.execute("""
            ALTER TABLE dictation_attempt 
            ADD COLUMN attempt_number INTEGER DEFAULT 1
        """)
        
        print("Updating existing records with proper attempt numbers...")
        
        # Get all existing attempts grouped by user_id and audio_id
        cursor.execute("""
            SELECT id, user_id, audio_id, submitted_at 
            FROM dictation_attempt 
            ORDER BY user_id, audio_id, submitted_at
        """)
        
        attempts = cursor.fetchall()
        
        # Group attempts by user_id and audio_id
        attempt_groups = {}
        for attempt_id, user_id, audio_id, submitted_at in attempts:
            key = (user_id, audio_id)
            if key not in attempt_groups:
                attempt_groups[key] = []
            attempt_groups[key].append((attempt_id, submitted_at))
        
        # Update attempt numbers
        updates = 0
        for (user_id, audio_id), group_attempts in attempt_groups.items():
            # Sort by submitted_at to get chronological order
            group_attempts.sort(key=lambda x: x[1] if x[1] else '1970-01-01')
            
            for index, (attempt_id, _) in enumerate(group_attempts):
                attempt_number = index + 1
                cursor.execute("""
                    UPDATE dictation_attempt 
                    SET attempt_number = ? 
                    WHERE id = ?
                """, (attempt_number, attempt_id))
                updates += 1
        
        conn.commit()
        print(f"Migration completed successfully! Updated {updates} records.")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM dictation_attempt WHERE attempt_number IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"Verified: {count} records have attempt_number values")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Adding attempt_number to DictationAttempt")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The database is now ready with attempt tracking functionality.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
    
    print("=" * 60)