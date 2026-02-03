#!/usr/bin/env python3
import sqlite3
from werkzeug.security import check_password_hash

DB_PATH = 'instance/dictation_app.db'
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'Stenographix@03102025'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT username, password_hash FROM user WHERE username = ? AND role = 'admin'", (TEST_USERNAME,))
result = cursor.fetchone()

if result:
    username, stored_hash = result
    print(f"✅ Found admin user: {username}")
    print(f"📝 Stored hash: {stored_hash[:50]}...")
    print(f"🔐 Testing password: {TEST_PASSWORD}")
    
    if check_password_hash(stored_hash, TEST_PASSWORD):
        print("✅ ✅ ✅ PASSWORD MATCHES! Login should work!")
    else:
        print("❌ PASSWORD DOES NOT MATCH!")
        print("Let me try some common passwords...")
        
        for pwd in ['admin', 'Admin123', 'Stenographix', 'password']:
            if check_password_hash(stored_hash, pwd):
                print(f"✅ FOUND IT! The password is: {pwd}")
                break
else:
    print("❌ No admin user found!")

conn.close()