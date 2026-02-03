#!/bin/bash

# Cleanup script to remove unnecessary files from local and production

echo "=========================================="
echo "🧹 PROJECT CLEANUP SCRIPT"
echo "=========================================="
echo ""

# Files to keep (essential)
KEEP_FILES=(
    "app.py"
    "config.py"
    "wsgi.py"
    "requirements.txt"
    "improved_text_comparison.py"
    "lcs_text_comparison.py"
    ".env.example"
    ".gitignore"
    "README.md"
    "database_schema.sql"
)

# Files to remove (old/unnecessary)
REMOVE_FILES=(
    "deploy_to_hostinger.sh"
    "hostinger_vps_setup.sh"
    "deploy_back_button_updates.sh"
    "deploy_admission_feature.sh"
    "dictation-app.tar.gz"
    "HOSTINGER_DEPLOYMENT.md"
    "HOSTINGER_VPS_DEPLOYMENT.md"
    "PRODUCTION_READY.md"
    "production_env_file.env"
    "nginx_stenographix_config"
    "nginx_stenographix_ssl_config"
    "render.yaml"
    "Dockerfile"
    "Procfile"
    "deploy.py"
    "git-setup.sh"
    "backup_and_migration.py"
    "PRODUCTION_DATABASE_SETUP.md"
    "Makefile"
    "lcs_comparison_demo.py"
    "fix_admin_login.py"
    "deployment_guide.md"
)

# Migration scripts (one-time use, can be removed after successful migration)
MIGRATION_FILES=(
    "migrate_db.py"
    "migrate_db_content_type.py"
    "migrate_db_attempt_number.py"
    "migrate_db_typing_attempt_number.py"
    "migrate_device_registration.py"
    "migrate_trusted_devices.py"
    "migrate_admission_requests.py"
    "migrate_trusted_devices_production.py"
)

echo "📋 Step 1: Cleaning up LOCAL unnecessary files..."
echo ""

# Remove unnecessary files locally
for file in "${REMOVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   Removing: $file"
        rm "$file"
    fi
done

echo ""
echo "📋 Step 2: Moving migration scripts to archive folder..."
mkdir -p migrations_archive
for file in "${MIGRATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   Archiving: $file"
        mv "$file" migrations_archive/
    fi
done

echo ""
echo "📋 Step 3: Cleaning up PRODUCTION server..."
echo ""

SERVER="root@72.60.202.28"
PASSWORD="Stenographix@03102025"

# Clean up production server
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" << 'REMOTE_EOF'
cd /var/www/stenographix

echo "🧹 Cleaning production server..."

# Remove unnecessary deployment scripts
rm -f deploy_to_hostinger.sh
rm -f hostinger_vps_setup.sh
rm -f deploy_back_button_updates.sh
rm -f deploy_admission_feature.sh
rm -f dictation-app.tar.gz
rm -f HOSTINGER_DEPLOYMENT.md
rm -f HOSTINGER_VPS_DEPLOYMENT.md
rm -f nginx_stenographix_config
rm -f nginx_stenographix_ssl_config
rm -f render.yaml
rm -f Dockerfile
rm -f Procfile
rm -f deploy.py
rm -f lcs_comparison_demo.py

# Move migration scripts to archive
mkdir -p migrations_archive
mv migrate_*.py migrations_archive/ 2>/dev/null || true
mv fix_admin_login.py migrations_archive/ 2>/dev/null || true

# Remove old deployment scripts
rm -f deploy_all_features.sh

echo "✅ Production server cleaned"
echo ""
echo "📁 Essential files kept:"
ls -lh *.py | grep -E "(app|config|wsgi|improved|lcs_text)" || true

REMOTE_EOF

echo ""
echo "=========================================="
echo "✅ CLEANUP COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "   ✓ Removed old deployment scripts"
echo "   ✓ Archived migration scripts locally"
echo "   ✓ Cleaned production server"
echo ""
echo "📁 Essential files retained:"
echo "   ✓ app.py (main application)"
echo "   ✓ config.py (configuration)"
echo "   ✓ wsgi.py (WSGI entry point)"
echo "   ✓ requirements.txt (dependencies)"
echo "   ✓ improved_text_comparison.py (LCS logic)"
echo "   ✓ lcs_text_comparison.py (text comparison)"
echo "   ✓ templates/ (all HTML templates)"
echo "   ✓ uploads/ (audio files)"
echo "   ✓ typing_passages/ (typing content)"
echo "   ✓ app.db (database)"
echo ""
echo "📦 Archived:"
echo "   ✓ Migration scripts moved to migrations_archive/"
echo ""