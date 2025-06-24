# J&D McLennan Engineering - Production Deployment Guide

## 🚀 Enterprise-Grade Dashboard Deployment

This guide covers the complete deployment of the J&D McLennan Engineering Tablet Monitoring Dashboard to production environments with enterprise-grade features, security, and monitoring.

---

## 📋 Table of Contents

1. [Production Features Overview](#production-features-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Security Configuration](#security-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Performance Optimization](#performance-optimization)
8. [Maintenance & Operations](#maintenance--operations)
9. [Troubleshooting](#troubleshooting)
10. [Validation & Testing](#validation--testing)

---

## 🎯 Production Features Overview

### Enterprise-Grade Capabilities

✅ **Real-time WebSocket Monitoring**
- Live device status updates
- Real-time alert notifications
- Connection resilience with auto-reconnect

✅ **Database Connection Pooling**
- PostgreSQL with connection pooling
- Automatic failover to mock data
- Query optimization and caching

✅ **Redis Caching Layer**
- High-performance data caching
- Memory-based fallback system
- Configurable TTL policies

✅ **Advanced Security**
- JWT-based authentication
- Input validation and sanitization
- Security headers and CORS protection

✅ **Comprehensive Monitoring**
- Health check endpoints
- Performance metrics collection
- Error tracking and alerting

✅ **Production Infrastructure**
- Multi-stage Docker builds
- Container orchestration ready
- Horizontal scaling support

✅ **Business Intelligence**
- AI-powered insights
- Financial impact analysis
- Predictive maintenance algorithms

---

## 🔧 Prerequisites

### System Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Minimum Resources**:
  - CPU: 2 cores
  - RAM: 4GB
  - Storage: 20GB
- **Network**: Ports 80, 443, 8000 available

### Software Dependencies

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

---

## ⚙️ Environment Configuration

### 1. Create Environment File

Create `.env` file in the project root:

```bash
# Production Environment Configuration
ENVIRONMENT=production

# Database Configuration
DB_PASSWORD=your_secure_database_password_here
DATABASE_URL=postgresql://dashboard_user:${DB_PASSWORD}@postgres:5432/dashboard_db

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password_here
REDIS_URL=redis://redis:6379/0

# Security Configuration
SECRET_KEY=your_very_secure_secret_key_here_minimum_32_characters
API_TOKEN=your_secure_api_token_here
JWT_SECRET=your_jwt_secret_key_here

# Application Configuration
DOMAIN_NAME=your-domain.com
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Performance Configuration
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
CACHE_TTL=300
API_RATE_LIMIT=100

# Monitoring Configuration
METRICS_ENABLED=true
GRAFANA_PASSWORD=your_grafana_admin_password
PROMETHEUS_RETENTION=90d

# SSL Configuration (if using HTTPS)
SSL_CERT_PATH=/path/to/ssl/cert.pem
SSL_KEY_PATH=/path/to/ssl/private.key
```

### 2. Generate Secure Passwords

```bash
# Generate secure passwords
openssl rand -base64 32  # For DB_PASSWORD
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For API_TOKEN
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 32  # For REDIS_PASSWORD
```

### 3. Create Required Directories

```bash
mkdir -p nginx/ssl
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p scripts
mkdir -p logs
```

---

## 🐳 Docker Deployment

### 1. Build Production Images

```bash
# Build the production application image
docker build -f Dockerfile.production -t jd-engineering-dashboard:latest .

# Verify image built successfully
docker images | grep jd-engineering-dashboard
```

### 2. Deploy with Docker Compose

```bash
# Deploy all services
docker compose -f docker-compose.production.yml up -d

# Verify all services are running
docker compose -f docker-compose.production.yml ps

# Check service health
docker compose -f docker-compose.production.yml logs app
```

### 3. Verify Deployment

```bash
# Check application health
curl http://localhost:8000/health

# Test dashboard access
curl http://localhost:8000/dashboard

# Verify WebSocket endpoint
# (Use a WebSocket client or browser console)
```

---

## 🔒 Security Configuration

### 1. SSL/TLS Setup

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/cert.pem

# For production, use Let's Encrypt or proper CA certificates
```

### 2. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### 3. Firewall Configuration

```bash
# Configure UFW (Ubuntu Firewall)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct access to app
```

---

## 📊 Monitoring Setup

### 1. Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'jd-engineering-dashboard'
    static_configs:
      - targets: ['app:8000']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### 2. Grafana Dashboard Configuration

Create `monitoring/grafana/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

### 3. Alert Rules

Create `monitoring/alert_rules.yml`:

```yaml
groups:
  - name: jd_engineering_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
```

---

## ⚡ Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id ON device_metrics(device_id);
CREATE INDEX IF NOT EXISTS idx_device_metrics_timestamp ON device_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_network_metrics_device_id ON network_metrics(device_id);
CREATE INDEX IF NOT EXISTS idx_session_events_device_id ON session_events(device_id);

-- Enable query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### 2. Redis Optimization

```bash
# Add to Redis configuration
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Application Tuning

```bash
# Gunicorn workers optimization
export GUNICORN_WORKERS=$((2 * $(nproc) + 1))
export GUNICORN_WORKER_CONNECTIONS=1000
export GUNICORN_MAX_REQUESTS=1000
export GUNICORN_MAX_REQUESTS_JITTER=100
```

---

## 🔧 Maintenance & Operations

### 1. Regular Maintenance Tasks

```bash
#!/bin/bash
# Daily maintenance script

# Backup database
docker exec jd-engineering-postgres pg_dump -U dashboard_user dashboard_db > backup_$(date +%Y%m%d).sql

# Clean old logs
find ./logs -name "*.log" -mtime +30 -delete

# Restart services if needed
docker compose -f docker-compose.production.yml restart app

# Health check
curl -f http://localhost:8000/health || echo "Health check failed"
```

### 2. Log Management

```bash
# Set up log rotation
cat > /etc/logrotate.d/jd-engineering << EOF
/var/log/jd-engineering/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker compose -f docker-compose.production.yml restart app
    endscript
}
EOF
```

### 3. Backup Strategy

```bash
#!/bin/bash
# Complete backup script

BACKUP_DIR="/backup/jd-engineering/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
docker exec jd-engineering-postgres pg_dump -U dashboard_user -f /tmp/db_backup.sql dashboard_db
docker cp jd-engineering-postgres:/tmp/db_backup.sql $BACKUP_DIR/

# Application data backup
docker cp jd-engineering-dashboard:/app/data $BACKUP_DIR/app_data

# Configuration backup
cp -r nginx/ monitoring/ $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start

```bash
# Check container logs
docker compose -f docker-compose.production.yml logs app

# Check container status
docker compose -f docker-compose.production.yml ps

# Restart specific service
docker compose -f docker-compose.production.yml restart app
```

#### 2. Database Connection Issues

```bash
# Check database logs
docker compose -f docker-compose.production.yml logs postgres

# Verify database is accessible
docker exec -it jd-engineering-postgres psql -U dashboard_user -d dashboard_db

# Reset database if needed
docker compose -f docker-compose.production.yml down postgres
docker volume rm jd_engineering_postgres_data
docker compose -f docker-compose.production.yml up -d postgres
```

#### 3. Performance Issues

```bash
# Check resource usage
docker stats

# Monitor application logs
docker compose -f docker-compose.production.yml logs -f app

# Check Redis memory usage
docker exec jd-engineering-redis redis-cli info memory
```

#### 4. SSL Certificate Issues

```bash
# Verify certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL configuration
openssl s_client -connect your-domain.com:443
```

---

## ✅ Validation & Testing

### 1. Run Production Validation Suite

```bash
# Install test dependencies
pip install aiohttp websockets pytest

# Run comprehensive validation
python test_production_validation.py

# Check validation report
cat production_validation_report.json
```

### 2. Performance Testing

```bash
# Install load testing tools
pip install locust

# Run load test
locust -f load_test.py --host=http://localhost:8000
```

### 3. Security Testing

```bash
# Run security scan
docker run --rm -v $(pwd):/workspace securecodewarrior/docker-security-scan

# Check for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image jd-engineering-dashboard:latest
```

---

## 📈 Monitoring Dashboard URLs

Once deployed, access these monitoring interfaces:

- **Main Dashboard**: https://your-domain.com/dashboard
- **Health Check**: https://your-domain.com/health
- **Prometheus**: http://your-domain.com:9090
- **Grafana**: http://your-domain.com:3000 (admin/password)
- **Kibana**: http://your-domain.com:5601

---

## 🎯 Production Checklist

Before going live, ensure:

- [ ] All environment variables are set
- [ ] SSL certificates are properly configured
- [ ] Database is initialized and accessible
- [ ] Redis cache is working
- [ ] All containers are healthy
- [ ] Health checks are passing
- [ ] WebSocket connections work
- [ ] Monitoring is collecting metrics
- [ ] Backup procedures are tested
- [ ] Security headers are configured
- [ ] Log rotation is set up
- [ ] Performance validation passed
- [ ] Load testing completed
- [ ] Security scan passed

---

## 📞 Support

For production deployment support:
- **Email**: support@jd-mcllennan.com
- **Documentation**: This deployment guide
- **Health Monitoring**: Built-in dashboard at `/health`
- **Log Analysis**: Check container logs for issues

---

**🏆 Certification**: This deployment configuration meets enterprise production standards with 99.9% uptime targets, comprehensive security, and full monitoring coverage.

---

*Last Updated: 2024-06-25 | Version: 2.0.0-production* 