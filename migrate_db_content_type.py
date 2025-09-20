#!/usr/bin/env python3

import sqlite3
import os

# Database path
DB_PATH = 'instance/dictation_app.db'

def migrate_database():
    """Add content_type column to audio_file table"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if content_type column already exists
        cursor.execute("PRAGMA table_info(audio_file)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'content_type' in columns:
            print("content_type column already exists in audio_file table")
            conn.close()
            return True
        
        print("Adding content_type column to audio_file table...")
        
        # Add the content_type column with default value 'both'
        cursor.execute("ALTER TABLE audio_file ADD COLUMN content_type VARCHAR(20) DEFAULT 'both'")
        
        # Update existing records to have 'both' as content_type
        cursor.execute("UPDATE audio_file SET content_type = 'both' WHERE content_type IS NULL")
        
        # Commit changes
        conn.commit()
        
        print("Migration completed successfully!")
        print("All existing audio files are now set to 'both' (exam and practice)")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM audio_file WHERE content_type = 'both'")
        count = cursor.fetchone()[0]
        print(f"Updated {count} audio files with content_type = 'both'")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    print("Starting database migration...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")