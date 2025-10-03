#!/bin/bash

# Simplified Hostinger VPS Setup Script for Flask Dictation App (SQLite)
# Run this script on your fresh VPS to set up the environment

echo "🚀 Starting Hostinger VPS Setup for Flask Dictation App (SQLite)"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required software (no MySQL needed - using SQLite)
echo "🛠️ Installing required software..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y nginx supervisor git curl wget unzip
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y sqlite3

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx

# Start and enable services
sudo systemctl start nginx
sudo systemctl enable nginx

# Create application user (recommended security practice)
sudo adduser --disabled-password --gecos "" appuser
sudo usermod -aG www-data appuser

# Create application directory
sudo mkdir -p /var/www/dictation-app
sudo chown appuser:www-data /var/www/dictation-app
sudo chmod 755 /var/www/dictation-app

# Create required directories
sudo mkdir -p /var/www/dictation-app/{uploads,typing_passages,logs}
sudo chown -R appuser:www-data /var/www/dictation-app
sudo chmod -R 755 /var/www/dictation-app

# Set up firewall
echo "🔥 Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ VPS setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your application files"
echo "2. Set up domain DNS (point A record to this VPS IP)"
echo "3. Run the deployment script"
echo "4. Configure SSL certificate"
echo ""
echo "🌐 Your VPS IP: $(curl -s ifconfig.me)"