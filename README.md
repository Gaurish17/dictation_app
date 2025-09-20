# Dictation & Typing Practice Application

A comprehensive Flask web application for dictation and typing practice with user management, subscription tracking, and performance analytics.

## Features

### Student Features
- 🎧 **Dictation Practice**: Audio-based typing exercises with accuracy tracking
- ⌨️ **Typing Practice**: Text-based typing speed and accuracy tests
- 📊 **Progress Tracking**: Personal performance statistics and improvement tracking
- 🏆 **Leaderboards**: Compare performance with other students
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

### Admin Features
- 👥 **User Management**: Create, edit, and manage student accounts
- 📅 **Subscription Management**: Track and extend user subscriptions
- 📁 **Content Management**: Upload audio files and typing passages
- 📈 **Analytics & Reports**: Detailed performance reports and data export
- 🔒 **Security Features**: Device restriction and session management

### Technical Features
- 🔐 **Secure Authentication**: Password hashing and session management
- 🗄️ **Database Management**: SQLite for development, PostgreSQL for production
- 📤 **Data Export**: Excel, PDF, and CSV export capabilities
- 🎯 **Text Comparison**: Advanced algorithm for accuracy calculation
- 🔧 **Configuration Management**: Environment-based settings

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd suyog_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

5. **Initialize database**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open browser to `http://localhost:5000`
   - Default admin: `admin` / `admin123`
   - Default superuser: `superuser` / `super123`
   - Demo students: `student1`, `student2`, `student3` / `student123`

## Deployment Options

### 🚀 Quick Deployment (Recommended)

#### Option 1: Railway (Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy using our script
python deploy.py railway
```

#### Option 2: Heroku
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Deploy using our script
python deploy.py heroku
```

#### Option 3: DigitalOcean App Platform
```bash
python deploy.py digitalocean
# Follow the generated instructions
```

### 🐳 Docker Deployment
```bash
# Setup Docker deployment
python deploy.py docker

# Run with Docker Compose
docker-compose up -d
```

### 🖥️ VPS Deployment (Ubuntu/CentOS)
```bash
# Generate VPS deployment files
python deploy.py vps

# Follow the generated setup instructions
```

## Hosting Platform Comparison

| Platform | Cost/Month | Ease of Setup | Scalability | Database | SSL | Domain |
|----------|------------|---------------|-------------|----------|-----|--------|
| **Railway** | $5-20 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Included | ✅ Free | ✅ Custom |
| **Heroku** | $7-25 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Add-on | ✅ Free | ✅ Custom |
| **DigitalOcean** | $12-35 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Managed | ✅ Free | ✅ Custom |
| **Hostinger VPS** | €4-15 | ⭐⭐ | ⭐⭐⭐ | ⚙️ Setup Required | ⚙️ Let's Encrypt | ✅ Purchase |

## Environment Variables

### Required
```bash
SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
```

### Optional
```bash
UPLOAD_FOLDER=/app/uploads
TYPING_PASSAGES_FOLDER=/app/typing_passages
```

## Database Configuration

### Development (SQLite)
- Automatic setup
- File-based storage
- No additional configuration needed

### Production (PostgreSQL)
```bash
# Heroku
heroku addons:create heroku-postgresql:hobby-dev

# Railway
# PostgreSQL automatically provisioned

# DigitalOcean
# Managed database available in app spec

# Manual setup
CREATE DATABASE dictation_app;
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE dictation_app TO app_user;
```

## File Storage

### Local Development
- Audio files: `uploads/` directory
- Typing passages: `typing_passages/` directory

### Production Options
1. **Local Storage** (default)
   - Files stored on server filesystem
   - Suitable for small to medium deployments

2. **Cloud Storage** (recommended for scale)
   - AWS S3, Google Cloud Storage, or similar
   - Better for multiple server instances
   - Automatic backups and CDN support

## Security Considerations

### Production Security Checklist
- [ ] Change default admin passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting (if needed)

### Built-in Security Features
- Password hashing with SHA256
- Session management
- Device restriction for students
- CSRF protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection headers

## Performance Optimization

### Database
- Regular database maintenance
- Index optimization for large datasets
- Connection pooling for high traffic

### File Storage
- Compress audio files
- Use CDN for static assets
- Implement caching strategies

### Application
- Use Gunicorn with multiple workers
- Enable gzip compression
- Monitor memory usage

## Backup Strategy

### Database Backups
```bash
# PostgreSQL backup
pg_dump DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backups (add to cron)
0 2 * * * pg_dump DATABASE_URL > /backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### File Backups
```bash
# Backup uploads and typing passages
tar -czf files_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/ typing_passages/
```

## Monitoring & Logging

### Application Logs
- Flask application logs
- Error tracking and alerts
- Performance monitoring

### Recommended Tools
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **LogRocket** for user session recording
- **UptimeRobot** for uptime monitoring

## API Documentation

### Admin API Endpoints
- `POST /api/export-data` - Export application data
- `POST /api/filter-dictation-leaderboard` - Filter dictation leaderboard
- `POST /api/filter-typing-leaderboard` - Filter typing leaderboard

### Authentication
All API endpoints require proper session authentication.

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check DATABASE_URL format
postgresql://username:password@hostname:port/database_name

# Verify database exists and user has permissions
```

#### File Upload Issues
```bash
# Check file permissions
chmod 755 uploads/ typing_passages/

# Verify file size limits
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
```

#### Performance Issues
```bash
# Monitor resource usage
htop
df -h

# Check application logs
tail -f app.log
```

### Support
For deployment assistance or technical support:
1. Check the deployment guide: `deployment_guide.md`
2. Review application logs
3. Verify environment configuration
4. Test database connectivity

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write tests for new features

## License

This project is proprietary software. All rights reserved.

## Version History

### v1.0.0 (Current)
- Initial release
- Basic dictation and typing practice
- User management system
- Admin dashboard and reports
- Export functionality

### Planned Features
- Mobile app development
- Advanced analytics
- Multi-language support
- Bulk user import
- Integration with external systems

---

## Quick Reference

### Default Login Credentials
- **Admin**: `admin` / `admin123`
- **Superuser**: `superuser` / `super123`
- **Demo Students**: `student1`, `student2`, `student3` / `student123`

### Important Commands
```bash
# Local development
python app.py

# Production deployment
python deploy.py <platform>

# Database backup
pg_dump DATABASE_URL > backup.sql

# View logs
tail -f app.log
```

### Support Contacts
- Technical Issues: [Your support email]
- Deployment Help: [Your deployment support]
- Feature Requests: [Your feature request email]
