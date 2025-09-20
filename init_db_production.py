#!/usr/bin/env python3
"""
Production Database Initialization Script
Run this once to set up the database in production
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app and database
from app import app, db, User, hash_password

def init_production_db():
    """Initialize database for production"""
    print("🔄 Initializing production database...")
    
    with app.app_context():
        try:
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Create superuser if doesn't exist
            if not User.query.filter_by(role='superuser').first():
                superuser = User(
                    username='superuser',
                    password_hash=hash_password('super123'),
                    role='superuser',
                    is_active=True
                )
                db.session.add(superuser)
                print("✅ Created superuser account")
            else:
                print("ℹ️  Superuser already exists")
            
            # Create admin if doesn't exist
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password_hash=hash_password('admin123'),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin)
                print("✅ Created admin account")
            else:
                print("ℹ️  Admin already exists")
            
            # Create demo student accounts with active subscriptions
            demo_students = [
                {'username': 'student1', 'password': 'student123'},
                {'username': 'student2', 'password': 'student123'},
                {'username': 'student3', 'password': 'student123'}
            ]
            
            for student_data in demo_students:
                if not User.query.filter_by(username=student_data['username']).first():
                    student = User(
                        username=student_data['username'],
                        password_hash=hash_password(student_data['password']),
                        role='student',
                        is_active=True,
                        subscription_start=datetime.now(timezone.utc),
                        subscription_end=datetime.now(timezone.utc) + timedelta(days=30)
                    )
                    db.session.add(student)
                    print(f"✅ Created demo student: {student_data['username']}")
                else:
                    print(f"ℹ️  Student {student_data['username']} already exists")
            
            # Commit all changes
            db.session.commit()
            print("💾 All changes committed to database")
            
            # Verify database setup
            print("\n📋 Database Summary:")
            print(f"   - Superusers: {User.query.filter_by(role='superuser').count()}")
            print(f"   - Admins: {User.query.filter_by(role='admin').count()}")
            print(f"   - Students: {User.query.filter_by(role='student').count()}")
            print(f"   - Total Users: {User.query.count()}")
            
            print("\n🎉 Database initialization completed successfully!")
            print("\n🔑 Default Login Credentials:")
            print("   Admin: admin / admin123")
            print("   Superuser: superuser / super123")
            print("   Demo Students: student1, student2, student3 / student123")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            db.session.rollback()
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    success = init_production_db()
    sys.exit(0 if success else 1)
