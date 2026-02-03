#!/usr/bin/env python3
import sqlite3

DB_PATH = 'instance/dictation_app.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check if email column exists
    cursor.execute("PRAGMA table_info(admission_request)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'email' not in columns:
        print("📝 Adding email column to admission_request table...")
        cursor.execute("ALTER TABLE admission_request ADD COLUMN email VARCHAR(120)")
        conn.commit()
        print("✅ Email column added successfully!")
    else:
        print("✅ Email column already exists!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
conn.close()