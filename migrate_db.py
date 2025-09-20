"""
Database migration script to add reference_text column to audio_file table
"""
import sqlite3
import os

def migrate_database():
    db_path = 'instance/dictation_app.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database with updated schema...")
        # If database doesn't exist, just run the app to create it
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if reference_text column exists
        cursor.execute("PRAGMA table_info(audio_file)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'reference_text' not in columns:
            print("Adding reference_text column to audio_file table...")
            cursor.execute("ALTER TABLE audio_file ADD COLUMN reference_text TEXT")
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("reference_text column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()