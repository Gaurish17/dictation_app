#!/usr/bin/env python3
import sqlite3
import hashlib

DB_PATH = 'instance/dictation_app.db'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Stenographix@03102025'

def hash_password_sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

password_hash = hash_password_sha256(ADMIN_PASSWORD)
print(f"🔐 New SHA256 hash: {password_hash}")

cursor.execute("UPDATE user SET password_hash = ? WHERE username = ? AND role = 'admin'", 
               (password_hash, ADMIN_USERNAME))

conn.commit()
print(f"✅ Admin password updated successfully!")
print(f"   Username: {ADMIN_USERNAME}")
print(f"   Password: {ADMIN_PASSWORD}")
print(f"   Rows updated: {cursor.rowcount}")
conn.close()