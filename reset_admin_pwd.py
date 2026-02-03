#!/usr/bin/env python3
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'instance/dictation_app.db'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Stenographix@03102025'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

password_hash = generate_password_hash(ADMIN_PASSWORD)
cursor.execute("UPDATE user SET password_hash = ? WHERE username = ? AND role = 'admin'",
               (password_hash, ADMIN_USERNAME))

conn.commit()
print(f"✅ Admin password reset successfully!")
print(f"   Username: {ADMIN_USERNAME}")
print(f"   Password: {ADMIN_PASSWORD}")
print(f"   Rows updated: {cursor.rowcount}")
conn.close()