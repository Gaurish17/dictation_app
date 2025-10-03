# 🚀 Complete Hostinger VPS Deployment Guide

## Step-by-Step Deployment of Flask Dictation App

This guide will walk you through deploying your Flask dictation app on a Hostinger VPS using SQLite (simpler than MySQL).

---

## 🏁 Prerequisites

1. **Hostinger VPS** - Any plan (Premium or Business recommended)
2. **Domain name** - Registered and pointing to your VPS
3. **Local machine** with SSH access
4. **Basic Linux knowledge** (commands will be provided)

---

## 📋 Step 1: Purchase and Set Up VPS

### 1.1 Purchase Hostinger VPS
- Go to Hostinger and purchase a VPS plan
- Choose Ubuntu 20.04 or 22.04 LTS
- Note down your VPS IP address and root credentials

### 1.2 Connect to Your VPS
```bash
# From your local terminal
ssh root@YOUR_VPS_IP

# When prompted, enter your VPS root password
```

### 1.3 Run Initial Setup
```bash
# Upload the setup script to your VPS
scp hostinger_vps_setup.sh root@YOUR_VPS_IP:/tmp/

# Connect to VPS and run setup
ssh root@YOUR_VPS_IP
chmod +x /tmp/hostinger_vps_setup.sh
/tmp/hostinger_vps_setup.sh
```

---

## 🌐 Step 2: Configure Domain and DNS

### 2.1 Point Domain to VPS
In your domain registrar (or Hostinger domain panel):

1. **Add A Record:**
   - Name: `@` (for yourdomain.com)
   - Value: `YOUR_VPS_IP`
   - TTL: `300` (5 minutes)

2. **Add CNAME Record:**
   - Name: `www`
   - Value: `yourdomain.com`
   - TTL: `300`

### 2.2 Verify DNS Propagation
```bash
# Check if DNS is working (wait 5-30 minutes after setting DNS)
nslookup yourdomain.com
ping yourdomain.com
```

---

## 📤 Step 3: Deploy Your Application

### 3.1 Prepare Deployment Script
On your **local machine** where your Flask app code is:

1. **Update deployment script:**
   ```bash
   # Edit the configuration in deploy_to_hostinger.sh
   VPS_IP="YOUR_ACTUAL_VPS_IP"          # e.g., 192.168.1.100
   DOMAIN="yourdomain.com"              # e.g., stenographix.com
   ```

2. **Make script executable:**
   ```bash
   chmod +x deploy_to_hostinger.sh
   chmod +x hostinger_vps_setup.sh
   ```

### 3.2 Run Deployment
```bash
# From your local machine, run the deployment
./deploy_to_hostinger.sh
```

The script will automatically:
- ✅ Upload your app files
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Create SQLite database
- ✅ Configure Gunicorn (Python app server)
- ✅ Configure Nginx (web server)
- ✅ Set up SSL certificate (HTTPS)
- ✅ Create backup system

---

## 🔐 Step 4: Post-Deployment Security

### 4.1 Change Default Admin Password
1. Visit: `https://yourdomain.com/admin-login`
2. Login with: `admin` / `admin123`
3. **IMMEDIATELY change this password!**

### 4.2 Create Your First Student Account
1. In admin panel → Users → Create User
2. Set username, password, and subscription period

---

## 🎯 Step 5: Test Your Application

### 5.1 Test Admin Functions
- ✅ Admin login works
- ✅ Create student account
- ✅ Upload audio files
- ✅ Create typing passages
- ✅ View reports

### 5.2 Test Student Functions
- ✅ Student login works
- ✅ Dictation practice
- ✅ Typing practice
- ✅ Results display correctly

---

## 📊 Step 6: Monitor and Maintain

### 6.1 Check Application Status
```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Check if app is running
systemctl status dictation-app
systemctl status nginx

# View application logs
journalctl -u dictation-app -f
```

### 6.2 Check Files and Database
```bash
# Navigate to app directory
cd /var/www/dictation-app

# Check if database exists
ls -la production.db

# Check uploads directory
ls -la uploads/

# Check logs
tail -f logs/app.log
```

---

## 🆘 Troubleshooting Common Issues

### Issue 1: 500 Internal Server Error
**Solution:**
```bash
# Check application logs
journalctl -u dictation-app -f

# Restart the application
systemctl restart dictation-app

# Check Nginx logs
tail -f /var/log/nginx/error.log
```

### Issue 2: Database Errors
**Solution:**
```bash
cd /var/www/dictation-app

# Reinitialize database
sudo -u appuser ./venv/bin/python -c "from app import db; db.create_all()"

# Run migrations
sudo -u appuser ./venv/bin/python migrate_db.py
```

### Issue 3: File Upload Not Working
**Solution:**
```bash
# Check upload directory permissions
ls -la /var/www/dictation-app/uploads/
chmod 755 /var/www/dictation-app/uploads/
chown -R appuser:www-data /var/www/dictation-app/uploads/
```

### Issue 4: SSL Certificate Issues
**Solution:**
```bash
# Renew SSL certificate
certbot renew

# Test SSL
certbot certificates
```

---

## 🔄 Backup and Updates

### Manual Backup
```bash
# Run backup manually
/var/www/dictation-app/backup.sh
```

### Update Application
```bash
# If you make changes to your code
cd /var/www/dictation-app

# Upload new files (from local machine)
scp -r . root@YOUR_VPS_IP:/var/www/dictation-app/

# Restart application
systemctl restart dictation-app
```

---

## 📞 Support and Resources

### Important File Locations
- **Application:** `/var/www/dictation-app/`
- **Database:** `/var/www/dictation-app/production.db`
- **Uploads:** `/var/www/dictation-app/uploads/`
- **Logs:** `/var/www/dictation-app/logs/`
- **Backups:** `/var/www/dictation-app/backups/`

### Useful Commands
```bash
# Restart services
systemctl restart dictation-app
systemctl restart nginx

# Check status
systemctl status dictation-app
systemctl status nginx

# View logs
journalctl -u dictation-app -f
tail -f /var/log/nginx/access.log

# Monitor resources
htop
df -h
```

### Performance Monitoring
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check active connections
netstat -an | grep :80 | wc -l
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] VPS is accessible via SSH
- [ ] Domain points to VPS IP
- [ ] HTTPS works (SSL certificate)
- [ ] Admin login works at `/admin-login`
- [ ] Student accounts can be created
- [ ] File uploads work (audio/text files)
- [ ] Dictation practice functions
- [ ] Typing practice functions
- [ ] Database is saving data
- [ ] Backups are configured

---

## 🎉 Congratulations!

Your Flask Dictation App is now live on Hostinger VPS!

- **Website:** `https://yourdomain.com`
- **Admin Panel:** `https://yourdomain.com/admin-login`
- **Default Admin:** username: `admin`, password: `admin123` (CHANGE THIS!)

**Remember to:**
1. Change default admin password immediately
2. Set up regular backups
3. Monitor application performance
4. Keep system updated

---

## 💡 Pro Tips

1. **Use strong passwords** for all accounts
2. **Regular backups** are automated but test them
3. **Monitor disk space** - uploads can grow large
4. **Update system** monthly: `apt update && apt upgrade`
5. **Monitor logs** for any issues
6. **Test functionality** regularly

Your dictation app is now production-ready on Hostinger VPS! 🚀