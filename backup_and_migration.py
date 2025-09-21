#!/usr/bin/env python3
"""
Backup and Migration Tools for Dictation App
Handles SQLite backups, data export/import, and database migration
"""

import sqlite3
import json
import csv
import os
import shutil
from datetime import datetime
import zipfile

class DatabaseBackupManager:
    def __init__(self, db_path='instance/dictation_app.db'):
        self.db_path = db_path
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self):
        """Create a complete backup of database and files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"full_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        print(f"🔄 Creating full backup: {backup_name}")
        
        # Create backup directory
        os.makedirs(backup_path, exist_ok=True)
        
        # 1. Backup SQLite database
        if os.path.exists(self.db_path):
            db_backup = os.path.join(backup_path, 'dictation_app.db')
            shutil.copy2(self.db_path, db_backup)
            print("   ✅ Database backed up")
        
        # 2. Backup uploaded files
        for folder in ['uploads', 'typing_passages']:
            if os.path.exists(folder):
                folder_backup = os.path.join(backup_path, folder)
                shutil.copytree(folder, folder_backup)
                print(f"   ✅ {folder}/ backed up")
        
        # 3. Create zip archive
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove uncompressed backup
        shutil.rmtree(backup_path)
        
        print(f"✅ Full backup created: {zip_path}")
        return zip_path
    
    def export_data_json(self):
        """Export all data to JSON format"""
        if not os.path.exists(self.db_path):
            print("❌ Database not found")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = os.path.join(self.backup_dir, f"data_export_{timestamp}.json")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        data = {}
        
        # Export all tables
        tables = ['user', 'audio_file', 'typing_passage', 'dictation_attempt', 'typing_attempt']
        
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data[table] = [dict(row) for row in rows]
                print(f"   ✅ Exported {len(rows)} records from {table}")
            except sqlite3.OperationalError:
                print(f"   ⚠️  Table {table} not found")
        
        conn.close()
        
        # Save to JSON
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Data exported to: {export_file}")
        return export_file
    
    def export_data_csv(self):
        """Export data to CSV files"""
        if not os.path.exists(self.db_path):
            print("❌ Database not found")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_dir = os.path.join(self.backup_dir, f"csv_export_{timestamp}")
        os.makedirs(csv_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        tables = ['user', 'audio_file', 'typing_passage', 'dictation_attempt', 'typing_attempt']
        
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if rows:
                    csv_file = os.path.join(csv_dir, f"{table}.csv")
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()
                        for row in rows:
                            writer.writerow(dict(row))
                    print(f"   ✅ Exported {len(rows)} records to {table}.csv")
            except sqlite3.OperationalError:
                print(f"   ⚠️  Table {table} not found")
        
        conn.close()
        print(f"✅ CSV export completed: {csv_dir}")
        return csv_dir
    
    def import_data_json(self, json_file):
        """Import data from JSON export"""
        if not os.path.exists(json_file):
            print(f"❌ JSON file not found: {json_file}")
            return False
        
        print(f"🔄 Importing data from: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        
        # Import data table by table
        for table, rows in data.items():
            if not rows:
                continue
            
            try:
                # Get column names
                columns = list(rows[0].keys())
                placeholders = ','.join(['?' for _ in columns])
                
                # Insert data
                query = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                
                for row in rows:
                    values = [row[col] for col in columns]
                    conn.execute(query, values)
                
                conn.commit()
                print(f"   ✅ Imported {len(rows)} records to {table}")
                
            except sqlite3.Error as e:
                print(f"   ❌ Error importing {table}: {e}")
        
        conn.close()
        print("✅ Data import completed")
        return True
    
    def restore_full_backup(self, backup_zip):
        """Restore from a full backup zip file"""
        if not os.path.exists(backup_zip):
            print(f"❌ Backup file not found: {backup_zip}")
            return False
        
        print(f"🔄 Restoring from backup: {backup_zip}")
        
        # Extract backup
        temp_dir = "temp_restore"
        with zipfile.ZipFile(backup_zip, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Restore database
        db_backup = os.path.join(temp_dir, 'dictation_app.db')
        if os.path.exists(db_backup):
            os.makedirs('instance', exist_ok=True)
            shutil.copy2(db_backup, self.db_path)
            print("   ✅ Database restored")
        
        # Restore files
        for folder in ['uploads', 'typing_passages']:
            folder_backup = os.path.join(temp_dir, folder)
            if os.path.exists(folder_backup):
                if os.path.exists(folder):
                    shutil.rmtree(folder)
                shutil.copytree(folder_backup, folder)
                print(f"   ✅ {folder}/ restored")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("✅ Restore completed")
        return True
    
    def list_backups(self):
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            print("❌ No backups directory found")
            return []
        
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip') and 'backup' in file:
                file_path = os.path.join(self.backup_dir, file)
                size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                backups.append((file, f"{size:.1f} MB"))
        
        if backups:
            print("📁 Available backups:")
            for backup, size in backups:
                print(f"   - {backup} ({size})")
        else:
            print("📁 No backups found")
        
        return backups

def main():
    """Main menu for backup operations"""
    manager = DatabaseBackupManager()
    
    print("🗄️  Database Backup & Migration Tool")
    print("=" * 50)
    
    while True:
        print("\n📋 Options:")
        print("1. Create full backup (database + files)")
        print("2. Export data to JSON")
        print("3. Export data to CSV")
        print("4. Import data from JSON")
        print("5. Restore from full backup")
        print("6. List available backups")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            backup_file = manager.create_full_backup()
            print(f"✅ Backup saved: {backup_file}")
            
        elif choice == '2':
            export_file = manager.export_data_json()
            if export_file:
                print(f"✅ JSON export saved: {export_file}")
                
        elif choice == '3':
            export_dir = manager.export_data_csv()
            if export_dir:
                print(f"✅ CSV export saved: {export_dir}")
                
        elif choice == '4':
            json_file = input("Enter JSON file path: ").strip()
            manager.import_data_json(json_file)
            
        elif choice == '5':
            backup_file = input("Enter backup zip file path: ").strip()
            manager.restore_full_backup(backup_file)
            
        elif choice == '6':
            manager.list_backups()
            
        elif choice == '7':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
