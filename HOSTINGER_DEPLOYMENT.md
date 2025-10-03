# 🚀 Hostinger Deployment Guide for Flask Dictation App

This guide provides step-by-step instructions to deploy the Flask dictation app on Hostinger hosting.

## 📋 Prerequisites

1. **Hostinger Account** with Python hosting support
2. **Domain** configured with Hostinger
3. **SSH Access** to your hosting account
4. **MySQL Database** (optional, can use SQLite)

## 🔧 Pre-Deployment Setup

### 1. Prepare Environment Variables

1. Copy `.env.production` to `.env` and update with your values:

```bash
cp .env.production .env
```

2. **Critical values to update in `.env`:**

```env
# Generate a secure secret key (64 characters)
SECRET_KEY=your-super-secure-random-64-character-secret-key-here

# Database (Choose one option)
# Option 1: MySQL (Recommended for production)
DATABASE_URL=mysql+pymysql://username:password@hostname:3306/database_name

# Option 2: SQLite (Simple deployment)
DATABASE_URL=sqlite:///production.db

# Update paths for your Hostinger account
UPLOAD_FOLDER=/home/yourusername/public_html/uploads
TYPING_PASSAGES_FOLDER=/home/yourusername/public_html/typing_passages

# Admin contact
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PHONE=+919324165619

# Email settings (optional)
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=your-email-password
```

### 2. Generate Secure Secret Key

```python
# Run this Python script to generate a secure secret key
import secrets
print(secrets.token_urlsafe(64))
```

## 📤 File Upload to Hostinger

### Method 1: Using cPanel File Manager

1. **Zip the project files:**
```bash
zip -r dictation_app.zip . -x "venv/*" "__pycache__/*" "*.pyc" ".git/*"
```

2. **Upload via cPanel:**
   - Login to Hostinger cPanel
   - Go to File Manager
   - Navigate to `public_html`
   - Upload `dictation_app.zip`
   - Extract the zip file

### Method 2: Using SSH/SFTP

```bash
# Upload files via SCP
scp -r . username@yourserver.com:/home/username/public_html/

# Or use SFTP client like FileZilla
```

## 🛠 Server Setup

### 1. SSH into your Hostinger server

```bash
ssh username@yourserver.com
cd /home/username/public_html
```

### 2. Set up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Correct Permissions

```bash
# Set directory permissions
chmod 755 /home/username/public_html
chmod -R 755 templates/
chmod -R 755 static/ (if exists)

# Create and set permissions for upload directories
mkdir -p uploads typing_passages logs
chmod 755 uploads typing_passages logs

# Set executable permissions for Python files
chmod +x wsgi.py
chmod +x app.py
```

### 4. Database Setup

#### Option A: MySQL Database (Recommended)

1. **Create MySQL database in cPanel:**
   - Go to MySQL Databases
   - Create database: `username_dictation`
   - Create user and assign to database
   - Note down credentials

2. **Update DATABASE_URL in `.env`:**
```env
DATABASE_URL=mysql+pymysql://username_dbuser:password@localhost:3306/username_dictation
```

#### Option B: SQLite (Simple)

```bash
# SQLite will be created automatically
# Ensure database directory is writable
chmod 755 /home/username/public_html
```

### 5. Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database and create admin account
python wsgi.py
```

## 🌐 Web Server Configuration

### 1. Create .htaccess file

```bash
cat > .htaccess << 'EOF'
RewriteEngine On

# Handle Python application
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]

# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>

# Hide sensitive files
<Files ".env*">
    Order Allow,Deny
    Deny from all
</Files>

<Files "*.py">
    Order Allow,Deny
    Deny from all
</Files>

<Files "wsgi.py">
    Order Allow,Deny
    Allow from all
</Files>
EOF
```

### 2. Test the Application

```bash
# Test WSGI application
source venv/bin/activate
python wsgi.py

# Check if it runs without errors
# Press Ctrl+C after testing
```

## 🔐 Security Configuration

### 1. Secure File Permissions

```bash
# Protect sensitive files
chmod 600 .env .env.production
chmod 600 *.log

# Ensure Python files are not directly accessible
find . -name "*.py" -not -name "wsgi.py" -exec chmod 640 {} \;
```

### 2. Create robots.txt

```bash
cat > robots.txt << 'EOF'
User-agent: *
Disallow: /admin/
Disallow: /uploads/
Disallow: /logs/
Disallow: *.py
Disallow: *.log
EOF
```

## 📊 Database Management

### Initial Admin Account

The system will automatically create an admin account:
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ IMPORTANT:** Change this password immediately after first login!

### Manual Database Operations

```bash
# Backup database (MySQL)
mysqldump -u username -p database_name > backup.sql

# Backup database (SQLite)
cp production.db production_backup.db

# Run migrations
source venv/bin/activate
python migrate_db.py
python migrate_db_content_type.py
```

## 🚀 Going Live

### 1. Final Checks

```bash
# Check all files are in place
ls -la

# Test database connection
source venv/bin/activate
python -c "from app import db; print('Database OK')"

# Check permissions
ls -la uploads/ typing_passages/
```

### 2. Monitor Logs

```bash
# Check application logs
tail -f logs/app.log

# Check web server logs
tail -f /home/username/logs/error.log
```

### 3. Access Your Application

- **URL:** `https://yourdomain.com`
- **Admin Panel:** `https://yourdomain.com/admin-login`

## 🔄 Maintenance

### Regular Tasks

```bash
# Update application
git pull origin main  # if using git
source venv/bin/activate
pip install -r requirements.txt

# Backup database weekly
mysqldump -u username -p database_name > backup_$(date +%Y%m%d).sql

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete
```

### Monitoring

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Monitor active connections
netstat -an | grep :80 | wc -l
```

## 🆘 Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   ```bash
   # Check error logs
   tail -f /home/username/logs/error.log
   
   # Check file permissions
   ls -la wsgi.py
   ```

2. **Database Connection Error**
   ```bash
   # Test database connection
   python -c "import pymysql; print('PyMySQL OK')"
   
   # Check database credentials in .env
   cat .env | grep DATABASE_URL
   ```

3. **File Upload Issues**
   ```bash
   # Check upload directory permissions
   ls -la uploads/
   chmod 755 uploads/
   ```

4. **Python Path Issues**
   ```bash
   # Check virtual environment
   which python
   pip list
   ```

### Getting Help

1. **Check Hostinger Documentation**
2. **Contact Hostinger Support**
3. **Check application logs:** `logs/app.log`
4. **Review error logs:** `/home/username/logs/error.log`

## ✅ Success Checklist

- [ ] Environment variables configured
- [ ] Database created and initialized
- [ ] File permissions set correctly
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] WSGI application runs without errors
- [ ] .htaccess file created
- [ ] Security headers configured
- [ ] Admin account accessible
- [ ] Upload directories functional
- [ ] SSL certificate active

---

**🎉 Congratulations!** Your Flask dictation app should now be live on Hostinger!

Remember to:
- Change default admin password
- Regularly backup your database
- Monitor application logs
- Update dependencies periodically
- Test all functionality after deployment
