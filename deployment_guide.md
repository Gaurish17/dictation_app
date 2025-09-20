# Deployment Guide for Dictation & Typing Practice App

## Application Overview
- **Framework**: Flask with SQLAlchemy
- **Database**: SQLite (needs migration to PostgreSQL/MySQL for production)
- **Features**: User management, subscription tracking, audio/text content management
- **File Storage**: Audio files and typing passages

## Hosting Platform Options

### 1. **Hostinger (Recommended for beginners)**
- **VPS Hosting**: €3.99-€8.99/month
- **Business Hosting**: €2.99/month (limited Python support)
- **Cloud Hosting**: €9.99/month (better for Flask apps)

### 2. **Alternative Platforms**
- **DigitalOcean**: $6-$24/month (App Platform or Droplets)
- **Heroku**: $7-$25/month (good Flask support)
- **PythonAnywhere**: $5-$20/month (Python-focused)
- **Railway**: $5-$20/month (modern deployment)

## Step-by-Step Deployment Plan

### Phase 1: Pre-Deployment Preparation

#### 1.1 Environment Configuration
```bash
# Create production configuration
export FLASK_ENV=production
export SECRET_KEY="your-super-secure-secret-key-here"
export DATABASE_URL="postgresql://username:password@host:port/database"
```

#### 1.2 Database Migration
- Current: SQLite (local file)
- Production: PostgreSQL or MySQL
- Migration script needed for data transfer

#### 1.3 File Storage Setup
- Audio files in `/uploads` folder
- Typing passages in `/typing_passages` folder
- Consider cloud storage (AWS S3, Cloudinary) for scalability

### Phase 2: Platform-Specific Setup

#### Option A: Hostinger VPS Deployment

**Requirements:**
- Ubuntu 20.04/22.04 VPS
- Python 3.8+ with pip
- PostgreSQL or MySQL
- Nginx (reverse proxy)
- Gunicorn (WSGI server)

**Steps:**
1. Purchase Hostinger VPS
2. Set up domain DNS
3. Install dependencies
4. Configure database
5. Deploy application
6. Set up SSL certificate

#### Option B: DigitalOcean App Platform

**Advantages:**
- Managed hosting
- Auto-scaling
- Built-in database options
- SSL included

**Steps:**
1. Create DigitalOcean account
2. Connect GitHub repository
3. Configure build settings
4. Set up managed database
5. Configure domain

### Phase 3: Required Code Changes

#### 3.1 Database Configuration Update
```python
import os
from urllib.parse import urlparse

# Production database configuration
if os.environ.get('DATABASE_URL'):
    url = urlparse(os.environ.get('DATABASE_URL'))
    SQLALCHEMY_DATABASE_URI = f"postgresql://{url.username}:{url.password}@{url.hostname}:{url.port}{url.path}"
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dictation_app.db'
```

#### 3.2 File Storage Configuration
```python
import os

# Configure upload folders for production
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
TYPING_PASSAGES_FOLDER = os.environ.get('TYPING_PASSAGES_FOLDER', 'typing_passages')

# For cloud storage (optional)
# AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
```

#### 3.3 Security Updates
```python
# Update secret key
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-change-in-production')

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### Phase 4: Production Files Needed

#### 4.1 requirements.txt (Enhanced)
```
Flask==2.3.3
Werkzeug==2.3.7
Flask-SQLAlchemy==3.0.5
python-dateutil==2.8.2
openpyxl==3.1.2
reportlab==4.0.4
psycopg2-binary==2.9.7  # For PostgreSQL
gunicorn==21.2.0        # WSGI server
python-dotenv==1.0.0    # Environment variables
```

#### 4.2 Procfile (for Heroku/Railway)
```
web: gunicorn app:app
```

#### 4.3 Dockerfile (for containerized deployment)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

#### 4.4 .env file (environment variables)
```
SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database
FLASK_ENV=production
UPLOAD_FOLDER=/app/uploads
TYPING_PASSAGES_FOLDER=/app/typing_passages
```

### Phase 5: Domain Setup

#### 5.1 Domain Purchase Options
- **Hostinger**: €0.99-€12.99/year
- **Namecheap**: $8-$15/year
- **GoDaddy**: $12-$20/year
- **Google Domains**: $12-$20/year

#### 5.2 DNS Configuration
```
A Record: @ -> Your server IP
CNAME: www -> your-domain.com
```

#### 5.3 SSL Certificate
- Free: Let's Encrypt (automatic with most platforms)
- Paid: SSL certificates from domain providers

### Phase 6: Deployment Checklist

- [ ] Choose hosting platform
- [ ] Purchase domain
- [ ] Set up database (PostgreSQL/MySQL)
- [ ] Update application configuration
- [ ] Deploy application code
- [ ] Configure DNS records
- [ ] Set up SSL certificate
- [ ] Test all functionality
- [ ] Set up backups
- [ ] Monitor application

## Cost Estimation (Monthly)

### Budget Option (~$10-15/month)
- Hostinger VPS Basic: €3.99
- Domain: €1/month
- Database: Included
- SSL: Free

### Professional Option (~$25-35/month)
- DigitalOcean App Platform: $12
- Managed Database: $15
- Domain: $1/month
- SSL: Included

### Premium Option (~$50-70/month)
- DigitalOcean Droplet: $24
- Managed Database: $15
- Cloud Storage: $5
- Domain: $1/month
- Backup: $5

## Next Steps

1. **Choose your preferred hosting option**
2. **I'll help you implement the specific deployment**
3. **Set up production configuration files**
4. **Deploy and test the application**

Would you like me to proceed with a specific hosting platform setup?
