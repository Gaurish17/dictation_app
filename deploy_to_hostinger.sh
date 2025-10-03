#!/bin/bash

# Deploy Flask Dictation App to Hostinger VPS (SQLite version)
# Run this script from your local machine to deploy the app

set -e  # Exit on any error

# Configuration - UPDATE THESE VALUES
VPS_IP="your_vps_ip_here"          # Your VPS IP address
VPS_USER="root"                     # Your VPS username (usually root)
DOMAIN="yourdomain.com"             # Your domain name
APP_DIR="/var/www/dictation-app"    # Application directory on VPS

echo "🚀 Deploying Flask Dictation App to Hostinger VPS (SQLite)"
echo "🎯 Target: $VPS_USER@$VPS_IP"
echo "🌐 Domain: $DOMAIN"

# Function to run commands on VPS
run_remote() {
    ssh $VPS_USER@$VPS_IP "$1"
}

# Function to copy files to VPS
copy_files() {
    echo "📤 Uploading application files..."
    
    # Create deployment package (excluding unnecessary files)
    echo "📦 Creating deployment package..."
    tar -czf dictation-app.tar.gz \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='logs' \
        --exclude='*.db' \
        --exclude='node_modules' \
        --exclude='uploads' \
        .
    
    # Upload to VPS
    scp dictation-app.tar.gz $VPS_USER@$VPS_IP:/tmp/
    
    # Extract on VPS
    run_remote "cd $APP_DIR && tar -xzf /tmp/dictation-app.tar.gz && chown -R appuser:www-data $APP_DIR"
    
    # Clean up
    rm dictation-app.tar.gz
    run_remote "rm /tmp/dictation-app.tar.gz"
    
    echo "✅ Files uploaded successfully"
}

# Function to set up Python environment
setup_python() {
    echo "🐍 Setting up Python environment..."
    
    run_remote "cd $APP_DIR && sudo -u appuser python3 -m venv venv"
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/pip install --upgrade pip"
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/pip install -r requirements.txt"
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/pip install gunicorn"
    
    echo "✅ Python environment ready"
}

# Function to create production environment file
create_env() {
    echo "🔧 Creating production environment configuration..."
    
    # Generate a secure secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    
    cat > /tmp/production.env << EOF
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY

# SQLite Database (simple deployment)
DATABASE_URL=sqlite:///$APP_DIR/production.db

# File paths
UPLOAD_FOLDER=$APP_DIR/uploads
TYPING_PASSAGES_FOLDER=$APP_DIR/typing_passages

# File upload settings
MAX_CONTENT_LENGTH=52428800

# Admin contact
ADMIN_EMAIL=admin@$DOMAIN
ADMIN_PHONE=+917756094286

# Email settings (optional - update if you have SMTP)
MAIL_USERNAME=noreply@$DOMAIN
MAIL_PASSWORD=your_email_password

# Security settings
SESSION_COOKIE_SECURE=True
WTF_CSRF_ENABLED=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=$APP_DIR/logs/app.log
EOF
    
    scp /tmp/production.env $VPS_USER@$VPS_IP:$APP_DIR/.env
    run_remote "chown appuser:www-data $APP_DIR/.env && chmod 600 $APP_DIR/.env"
    rm /tmp/production.env
    
    echo "✅ Environment configuration created"
}

# Function to initialize database
init_database() {
    echo "🗃️ Initializing SQLite database..."
    
    # Create database and initialize tables
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/python -c 'from app import app, db; app.app_context().push(); db.create_all(); print(\"Database initialized\")'"
    
    # Run migrations if they exist
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/python migrate_db.py" || echo "No migrate_db.py found"
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/python migrate_db_content_type.py" || echo "No migrate_db_content_type.py found"
    
    # Create admin account
    run_remote "cd $APP_DIR && sudo -u appuser ./venv/bin/python -c 'from app import app; app.run(debug=False, host=\"0.0.0.0\", port=5000)' &"
    sleep 2
    run_remote "pkill -f python" || true
    
    echo "✅ Database initialized successfully"
}

# Function to set up Gunicorn service
setup_gunicorn() {
    echo "⚙️ Setting up Gunicorn service..."
    
    cat > /tmp/dictation-app.service << EOF
[Unit]
Description=Dictation App Gunicorn daemon
After=network.target

[Service]
User=appuser
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/dictation-app.sock -m 007 wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=10
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    scp /tmp/dictation-app.service $VPS_USER@$VPS_IP:/tmp/
    run_remote "mv /tmp/dictation-app.service /etc/systemd/system/"
    run_remote "systemctl daemon-reload"
    run_remote "systemctl enable dictation-app"
    run_remote "systemctl start dictation-app"
    run_remote "systemctl status dictation-app --no-pager -l"
    rm /tmp/dictation-app.service
    
    echo "✅ Gunicorn service configured and started"
}

# Function to configure Nginx
setup_nginx() {
    echo "🌐 Setting up Nginx..."
    
    cat > /tmp/dictation-app.nginx << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # File upload size limit
    client_max_body_size 50M;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/dictation-app.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Serve uploaded files directly
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~* \.(py|pyc|pyo|db)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF
    
    scp /tmp/dictation-app.nginx $VPS_USER@$VPS_IP:/tmp/
    run_remote "mv /tmp/dictation-app.nginx /etc/nginx/sites-available/dictation-app"
    run_remote "ln -sf /etc/nginx/sites-available/dictation-app /etc/nginx/sites-enabled/"
    run_remote "rm -f /etc/nginx/sites-enabled/default"
    run_remote "nginx -t"
    run_remote "systemctl reload nginx"
    rm /tmp/dictation-app.nginx
    
    echo "✅ Nginx configured successfully"
}

# Function to set up SSL certificate
setup_ssl() {
    echo "🔒 Setting up SSL certificate..."
    
    echo "Setting up SSL with Let's Encrypt..."
    run_remote "certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect"
    
    echo "✅ SSL certificate configured"
}

# Function to create backup script
setup_backup() {
    echo "💾 Setting up backup script..."
    
    cat > /tmp/backup.sh << EOF
#!/bin/bash
# Backup script for Dictation App
BACKUP_DIR="$APP_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup database
cp $APP_DIR/production.db \$BACKUP_DIR/database_\$DATE.db

# Backup uploads
tar -czf \$BACKUP_DIR/uploads_\$DATE.tar.gz -C $APP_DIR uploads/

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.db" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF
    
    scp /tmp/backup.sh $VPS_USER@$VPS_IP:$APP_DIR/
    run_remote "chmod +x $APP_DIR/backup.sh && chown appuser:www-data $APP_DIR/backup.sh"
    
    # Set up daily backup cron job
    run_remote "echo '0 2 * * * /var/www/dictation-app/backup.sh' | crontab -u appuser -"
    
    rm /tmp/backup.sh
    echo "✅ Backup system configured"
}

# Main deployment function
main() {
    echo "Starting deployment..."
    
    copy_files
    setup_python
    create_env
    init_database
    setup_gunicorn
    setup_nginx
    setup_ssl
    setup_backup
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit https://$DOMAIN to access your app"
    echo "2. Admin login: https://$DOMAIN/admin-login"
    echo "3. Default admin credentials: admin / admin123"
    echo "4. ⚠️  IMPORTANT: Change admin password immediately!"
    echo ""
    echo "📊 Useful commands:"
    echo "- Check app status: systemctl status dictation-app"
    echo "- View app logs: journalctl -u dictation-app -f"
    echo "- Restart app: systemctl restart dictation-app"
    echo "- Check nginx: systemctl status nginx"
    echo ""
    echo "📁 App location: $APP_DIR"
    echo "🗄️  Database: $APP_DIR/production.db"
    echo "💾 Backups: $APP_DIR/backups/"
}

# Check if required variables are set
if [[ "$VPS_IP" == "your_vps_ip_here" ]] || [[ "$DOMAIN" == "yourdomain.com" ]]; then
    echo "❌ Please update the configuration variables at the top of this script:"
    echo "   - VPS_IP: Your VPS IP address"
    echo "   - DOMAIN: Your domain name"
    exit 1
fi

# Run deployment
main