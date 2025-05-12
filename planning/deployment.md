# Deployment Guide

## Overview
This document outlines the deployment process for the ICMP Backend service. It covers various deployment scenarios, including development, staging, and production environments.

## Prerequisites

## System Requirements
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis 6 or higher
- Nginx (for production)
- Gunicorn (for production)

## Required Software
1. **Python Packages**
   ```bash
   pip install -r requirements.txt
   ```

2. **System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y python3-dev postgresql postgresql-contrib redis-server nginx

   # CentOS/RHEL
   sudo yum update
   sudo yum install -y python3-devel postgresql postgresql-server redis nginx
   ```

## Development Deployment

## 1. Clone Repository
```bash
git clone https://github.com/your-org/icmp-backend.git
cd icmp-backend
```

## 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your development settings
```

## 5. Initialize Database
```bash
python scripts/init_db.py
```

## 6. Run Development Server
```bash
flask run
```

### Production Deployment

## 1. Server Preparation

### Update System
```bash
sudo apt-get update
sudo apt-get upgrade
```

### Install Dependencies
```bash
sudo apt-get install -y python3-dev postgresql postgresql-contrib redis-server nginx
```

### Configure Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 2. Database Setup

### Install PostgreSQL
```bash
sudo apt-get install -y postgresql postgresql-contrib
```

### Configure PostgreSQL
```bash
sudo -u postgres psql
postgres=# CREATE DATABASE icmp_db;
postgres=# CREATE USER icmp_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE icmp_db TO icmp_user;
postgres=# \q
```

### Initialize Database
```bash
python scripts/init_db.py
```

## 3. Redis Setup

### Install Redis
```bash
sudo apt-get install -y redis-server
```

### Configure Redis
```bash
sudo nano /etc/redis/redis.conf
# Set password and other security options
```

### Start Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 4. Application Deployment

### Create Application Directory
```bash
sudo mkdir -p /var/www/icmp-backend
sudo chown -R $USER:$USER /var/www/icmp-backend
```

### Clone Repository
```bash
cd /var/www/icmp-backend
git clone https://github.com/your-org/icmp-backend.git .
```

### Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment
```bash
cp .env.example .env
# Edit .env with production settings
```

### Set Up Gunicorn
```bash
sudo nano /etc/systemd/system/icmp-backend.service
```

Add the following content:
```ini
[Unit]
Description=ICMP Backend Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/icmp-backend
Environment="PATH=/var/www/icmp-backend/venv/bin"
ExecStart=/var/www/icmp-backend/venv/bin/gunicorn --workers 3 --bind unix:icmp-backend.sock -m 007 app:create_app()

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start icmp-backend
sudo systemctl enable icmp-backend
```

## 5. Nginx Configuration

### Install Nginx
```bash
sudo apt-get install -y nginx
```

### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/icmp-backend
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/icmp-backend/icmp-backend.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/icmp-backend /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL Configuration

### Install Certbot
```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### Monitoring Setup

## 1. Logging Configuration

### Application Logs
```bash
sudo mkdir -p /var/log/icmp-backend
sudo chown -R www-data:www-data /var/log/icmp-backend
```

Update the logging configuration in `.env`:
```
LOG_FILE=/var/log/icmp-backend/app.log
```

### Nginx Logs
```bash
sudo nano /etc/nginx/sites-available/icmp-backend
```

Add logging configuration:
```nginx
server {
    # ... existing configuration ...

    access_log /var/log/nginx/icmp-backend-access.log;
    error_log /var/log/nginx/icmp-backend-error.log;
}
```

## 2. Monitoring Tools

### Install Prometheus
```bash
sudo apt-get install -y prometheus
```

### Install Grafana
```bash
sudo apt-get install -y grafana
```

### Configure Prometheus
```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add the following configuration:
```yaml
scrape_configs:
  - job_name: 'icmp-backend'
    static_configs:
      - targets: ['localhost:8000']
```

### Start Services
```bash
sudo systemctl start prometheus
sudo systemctl enable prometheus
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

### Backup Strategy

## 1. Database Backups

### Create Backup Script
```bash
sudo nano /usr/local/bin/backup-icmp-db.sh
```

Add the following content:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/icmp-db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/icmp_db_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR
pg_dump -U icmp_user icmp_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "icmp_db_*.sql.gz" -mtime +7 -delete
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/backup-icmp-db.sh
```

### Set Up Cron Job
```bash
sudo crontab -e
```

Add the following line:
```
0 0 * * * /usr/local/bin/backup-icmp-db.sh
```

## 2. Application Backups

### Create Backup Script
```bash
sudo nano /usr/local/bin/backup-icmp-app.sh
```

Add the following content:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/icmp-app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/icmp_app_$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_FILE /var/www/icmp-backend

# Keep only last 7 days of backups
find $BACKUP_DIR -name "icmp_app_*.tar.gz" -mtime +7 -delete
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/backup-icmp-app.sh
```

### Set Up Cron Job
```bash
sudo crontab -e
```

Add the following line:
```
0 1 * * * /usr/local/bin/backup-icmp-app.sh
```

### Maintenance Procedures

## 1. Regular Maintenance

### Update Application
```bash
cd /var/www/icmp-backend
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart icmp-backend
```

### Update System
```bash
sudo apt-get update
sudo apt-get upgrade
```

### Check Logs
```bash
sudo tail -f /var/log/icmp-backend/app.log
sudo tail -f /var/log/nginx/icmp-backend-error.log
```

## 2. Emergency Procedures

### Restart Services
```bash
sudo systemctl restart icmp-backend
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis-server
```

### Check Service Status
```bash
sudo systemctl status icmp-backend
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### Database Recovery
```bash
# Restore from backup
gunzip -c /var/backups/icmp-db/icmp_db_20240311_000000.sql.gz | psql -U icmp_user icmp_db
```

### Troubleshooting

## 1. Common Issues

### Application Not Starting
```bash
# Check logs
sudo journalctl -u icmp-backend

# Check permissions
sudo chown -R www-data:www-data /var/www/icmp-backend
```

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U icmp_user -d icmp_db -h localhost
```

### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

## 2. Performance Issues

### Check Resource Usage
```bash
# CPU and Memory
top

# Disk Usage
df -h

# Network
netstat -tulpn
```

### Optimize Database
```bash
# Analyze tables
psql -U icmp_user -d icmp_db -c "ANALYZE;"

# Vacuum database
psql -U icmp_user -d icmp_db -c "VACUUM FULL;"
```

### Security Considerations

## 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
```

## 2. SSL/TLS Configuration
```bash
# Update SSL configuration
sudo nano /etc/nginx/sites-available/icmp-backend
```

Add security headers:
```nginx
server {
    # ... existing configuration ...

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

## 3. Regular Security Updates
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Scaling Considerations

## 1. Horizontal Scaling

### Load Balancer Configuration
```nginx
upstream icmp_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    # ... existing configuration ...

    location / {
        proxy_pass http://icmp_backend;
    }
}
```

## 2. Database Scaling

### Read Replicas
```bash
# Configure PostgreSQL replication
sudo nano /etc/postgresql/12/main/postgresql.conf
```

Add replication settings:
```ini
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
```

## 3. Caching Strategy

### Redis Configuration
```bash
# Configure Redis for caching
sudo nano /etc/redis/redis.conf
```

Add caching settings:
```ini
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Conclusion

This deployment guide provides a comprehensive overview of deploying and maintaining the ICMP Backend service. Regular updates and maintenance are essential for ensuring the service's reliability and security. Always test changes in a staging environment before applying them to production.

Last Updated: 2025-05-12
