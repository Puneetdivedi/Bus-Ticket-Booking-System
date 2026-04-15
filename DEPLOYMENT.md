# Deployment Guide

This guide covers deploying the Bus Ticket Booking System to production.

## Prerequisites

- Docker and Docker Compose installed
- Reverse proxy (Nginx, Apache) for SSL/TLS
- Database server (PostgreSQL recommended)
- CI/CD pipeline (GitHub Actions, GitLab CI, etc.)

## Architecture Overview

```
Internet
    │
    ▼
┌─────────────────┐
│   Nginx/Apache  │  (Reverse Proxy, SSL/TLS)
│  (Port 80/443)  │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐  ┌────────┐
│Frontend│  │Backend │
│ :3000  │  │ :8000  │
└────────┘  └────┬───┘
                 │
                 ▼
            ┌──────────┐
            │PostgreSQL│
            │ :5432    │
            └──────────┘
```

## Deployment Steps

### 1. Prepare Infrastructure

#### Option A: Docker Compose on VPS

```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone https://github.com/Puneetdivedi/Bus-Ticket-Booking-System.git
cd Bus-Ticket-Booking-System

# Create production environment file
cat > .env.production << EOF
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://bus_user:secure_password@db:5432/bus_booking
LOG_LEVEL=WARNING
API_KEY_ENABLED=true
API_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Create docker-compose override for production
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DATABASE_URL=postgresql://bus_user:pass@db:5432/bus_booking
      - LOG_LEVEL=WARNING
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
EOF
```

#### Option B: Kubernetes Deployment

See `k8s-deployment.yaml` for Kubernetes manifests.

### 2. Build and Deploy

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f backend frontend
```

### 3. Configure Nginx (Reverse Proxy)

Create `/etc/nginx/sites-available/bus-booking`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;

        # Rate limiting
        limit_req zone=api burst=100 nodelay;
    }

    # WebSocket support (if needed)
    location /ws/ {
        proxy_pass http://backend/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/bus-booking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Setup SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 5. Database Setup (PostgreSQL)

```bash
# Connect to database server
psql -U postgres

# Create database and user
CREATE DATABASE bus_booking;
CREATE USER bus_user WITH PASSWORD 'secure_password';
ALTER ROLE bus_user SET client_encoding TO 'utf8';
ALTER ROLE bus_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bus_user SET default_transaction_deferrable TO on;
ALTER ROLE bus_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bus_booking TO bus_user;
\q

# Backup database
pg_dump -U bus_user -d bus_booking > backup.sql
```

### 6. Configure Monitoring & Logging

#### Application Monitoring

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bus-booking-api'
    static_configs:
      - targets: ['localhost:8000']
```

#### Log Aggregation (Optional)

Setup ELK Stack (Elasticsearch, Logstash, Kibana):
```bash
docker run -d --name elasticsearch \
  -e "discovery.type=single-node" \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0

docker run -d --name kibana \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/kibana/kibana:8.0.0
```

### 7. Backup Strategy

#### Automated Daily Backups

Create `/home/ubuntu/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups/bus-booking"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
docker exec bus-booking-db pg_dump -U bus_user bus_booking | \
  gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup application data
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /app/database /app/uploads

# Keep only last 30 days of backups
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh  # Daily at 2 AM
```

### 8. Health Monitoring

Create health check script:
```bash
#!/bin/bash

API_URL="https://yourdomain.com/api/health"
EMAIL="admin@yourdomain.com"

RESPONSE=$(curl -s -w "%{http_code}" $API_URL)
HTTP_CODE=${RESPONSE: -3}

if [ "$HTTP_CODE" != "200" ]; then
    echo "Service down! HTTP Code: $HTTP_CODE" | mail -s "Alert: Bus Booking API" $EMAIL
fi
```

Add to crontab (every 5 minutes):
```bash
*/5 * * * * /path/to/health_check.sh
```

### 9. Auto-Scaling (Optional)

For Kubernetes:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bus-booking-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bus-booking-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Push to registry
        env:
          REGISTRY: ${{ secrets.REGISTRY }}
        run: |
          docker tag bus-booking-api:latest $REGISTRY/bus-booking-api:latest
          docker tag bus-booking-web:latest $REGISTRY/bus-booking-web:latest
          docker push $REGISTRY/bus-booking-api:latest
          docker push $REGISTRY/bus-booking-web:latest
      
      - name: Deploy to server
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          mkdir -p ~/.ssh
          echo "$DEPLOY_KEY" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh -i ~/.ssh/id_ed25519 user@server.com 'cd /app && git pull && docker-compose pull && docker-compose up -d'
```

## Performance Tuning

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_booking_travel_date ON bookings(travel_date);
CREATE INDEX idx_booking_seat_travel_date ON booking_seats(travel_date, seat_number);
CREATE INDEX idx_booking_mobile ON bookings(mobile_number);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM bookings WHERE travel_date = '2024-12-25';
```

### Application Optimization

- Enable gzip compression in Nginx
- Use CDN for static files
- Implement database connection pooling
- Cache frequently accessed data

## Security Hardening

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Fail2ban Installation

```bash
sudo apt-get install fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Troubleshooting Production Issues

### Services Down

```bash
# Check docker status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Full restart
docker-compose down
docker-compose up -d
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec bus-booking-db psql -U bus_user -d bus_booking -c "SELECT 1"

# Check database size
docker exec bus-booking-db psql -U bus_user -d bus_booking -c "SELECT pg_size_pretty(pg_database_size('bus_booking'))"
```

### Performance Issues

```bash
# Check container resources
docker stats

# View slow queries
docker exec bus-booking-db psql -U bus_user -d bus_booking -c "SHOW log_min_duration_statement"

# Enable slow query logging
docker exec bus-booking-db psql -U bus_user -d bus_booking -c "SET log_min_duration_statement = 1000"
```

## Rollback Procedure

```bash
# Tag current version
git tag production-$(date +%Y%m%d)

# Revert to previous version
docker-compose down
git checkout main~1
docker-compose up -d

# Or restore from backup
psql -U bus_user bus_booking < backup.sql
```

## Disaster Recovery

### Complete System Backup

```bash
# Full backup including Docker volumes
docker-compose exec -T db pg_dump -U bus_user bus_booking | gzip > full_backup.sql.gz

# Restore
gunzip < full_backup.sql.gz | docker-compose exec -T db psql -U bus_user bus_booking
```

---

For support or issues, please open a GitHub issue or contact the development team.
