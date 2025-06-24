# Railway Production Deployment Guide
## J&D McLennan Engineering Dashboard - Enterprise Grade

This guide provides complete setup steps for deploying the production-grade J&D McLennan Engineering Tablet Monitoring Dashboard to Railway with full enterprise features.

---

## 🚀 Railway Production Deployment Overview

Railway deployment includes:
- **Production-grade FastAPI application**
- **PostgreSQL database with connection pooling**
- **Redis caching layer**
- **WebSocket real-time monitoring**
- **Enterprise security & monitoring**
- **Automated deployments**

---

## 📋 Pre-Deployment Checklist

### 1. Railway Account Setup
- [ ] Railway account created at [railway.app](https://railway.app)
- [ ] Railway CLI installed
- [ ] GitHub repository connected
- [ ] Production branch created

### 2. Production Files Verification
Ensure these production files exist:
- [ ] `main_production.py` - Production FastAPI app
- [ ] `production_config.py` - Enterprise configuration
- [ ] `static/dashboard_production.html` - Real-time dashboard
- [ ] `Dockerfile.production` - Production container
- [ ] `railway.json` - Railway configuration
- [ ] `requirements.txt` - Updated dependencies

---

## ⚙️ Step 1: Railway Configuration

### Create Railway Configuration File

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  },
  "deploy": {
    "startCommand": "gunicorn main_production:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --log-level info",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Update Production Dockerfile for Railway

Update `Dockerfile.production`:

```dockerfile
# Multi-stage production Dockerfile for Railway deployment
FROM python:3.11-slim as base

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies including gunicorn
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn[standard]

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Railway port (dynamic)
EXPOSE $PORT

# Production startup command for Railway
CMD gunicorn main_production:app --worker-class uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --log-level info
```

---

## 🗄️ Step 2: Database Setup

### Railway PostgreSQL Service

1. **Add PostgreSQL Service**:
   ```bash
   # In Railway dashboard
   # 1. Click "New Project"
   # 2. Add "PostgreSQL" service
   # 3. Note the connection details
   ```

2. **Database Initialization Script**:

Create `scripts/railway_init_db.sql`:

```sql
-- J&D McLennan Engineering Database Schema for Railway
-- Production-grade table creation with optimizations

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Device registry table with Railway optimizations
CREATE TABLE IF NOT EXISTS device_registry (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(100),
    location VARCHAR(100),
    android_version VARCHAR(50),
    app_version VARCHAR(50),
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    total_sessions INTEGER DEFAULT 0,
    total_timeouts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Device metrics with partitioning-ready structure
CREATE TABLE IF NOT EXISTS device_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    battery_temperature FLOAT,
    memory_available BIGINT CHECK (memory_available >= 0),
    memory_total BIGINT CHECK (memory_total >= 0),
    storage_available BIGINT CHECK (storage_available >= 0),
    cpu_usage FLOAT CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Network metrics table
CREATE TABLE IF NOT EXISTS network_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    wifi_signal_strength INTEGER CHECK (wifi_signal_strength >= -100 AND wifi_signal_strength <= 0),
    wifi_ssid VARCHAR(100),
    connectivity_status VARCHAR(20) NOT NULL CHECK (connectivity_status IN ('online', 'offline', 'limited', 'unknown')),
    network_type VARCHAR(50),
    ip_address INET,
    dns_response_time FLOAT CHECK (dns_response_time >= 0),
    data_usage_mb FLOAT CHECK (data_usage_mb >= 0),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- App metrics table
CREATE TABLE IF NOT EXISTS app_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    screen_state VARCHAR(20) NOT NULL CHECK (screen_state IN ('active', 'locked', 'dimmed', 'off')),
    app_foreground VARCHAR(200),
    app_memory_usage BIGINT CHECK (app_memory_usage >= 0),
    screen_timeout_setting INTEGER CHECK (screen_timeout_setting >= 0),
    last_user_interaction TIMESTAMPTZ,
    notification_count INTEGER CHECK (notification_count >= 0),
    app_crashes INTEGER CHECK (app_crashes >= 0),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session events table
CREATE TABLE IF NOT EXISTS session_events (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('login', 'logout', 'timeout', 'error', 'reconnect', 'session_start', 'session_end')),
    session_id VARCHAR(100),
    duration INTEGER CHECK (duration >= 0),
    error_message TEXT,
    user_id VARCHAR(100),
    app_version VARCHAR(50),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes for Railway
CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id_timestamp ON device_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_network_metrics_device_id_timestamp ON network_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_app_metrics_device_id_timestamp ON app_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_session_events_device_id_timestamp ON session_events(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_device_registry_active ON device_registry(is_active, last_seen DESC);

-- Insert sample data for testing
INSERT INTO device_registry (device_id, device_name, location, android_version, app_version) VALUES
('tablet-001', 'Production Tablet 1', 'Warehouse A', '11.0', '2.1.0'),
('tablet-002', 'Production Tablet 2', 'Warehouse B', '11.0', '2.1.0'),
('tablet-003', 'Production Tablet 3', 'Office', '12.0', '2.1.0')
ON CONFLICT (device_id) DO NOTHING;

-- Performance monitoring view
CREATE OR REPLACE VIEW device_health_summary AS
SELECT 
    dr.device_id,
    dr.device_name,
    dr.location,
    dr.is_active,
    dr.last_seen,
    COALESCE(dm.battery_level, 80) as battery_level,
    COALESCE(nm.connectivity_status, 'online') as connectivity_status,
    COALESCE(am.screen_state, 'active') as screen_state
FROM device_registry dr
LEFT JOIN LATERAL (
    SELECT battery_level 
    FROM device_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) dm ON true
LEFT JOIN LATERAL (
    SELECT connectivity_status 
    FROM network_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) nm ON true
LEFT JOIN LATERAL (
    SELECT screen_state 
    FROM app_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) am ON true;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO CURRENT_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO CURRENT_USER;
```

---

## 🔧 Step 3: Environment Variables Setup

### Railway Environment Configuration

In Railway Dashboard → Variables, set these environment variables:

```bash
# Application Configuration
ENVIRONMENT=production
PORT=8000

# Database Configuration (Railway provides DATABASE_URL automatically)
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
DB_TIMEOUT=30

# Redis Configuration (if adding Redis service)
REDIS_URL=${{Redis.REDIS_URL}}
CACHE_TTL=300

# Security Configuration
SECRET_KEY=your_secure_secret_key_minimum_32_characters_here
API_TOKEN=your_secure_api_token_for_production_here
JWT_SECRET=your_jwt_secret_key_for_production_here

# Application Settings
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},localhost,127.0.0.1
API_RATE_LIMIT=100
METRICS_ENABLED=true

# Performance Settings
GUNICORN_WORKERS=4
GUNICORN_WORKER_CONNECTIONS=1000
GUNICORN_MAX_REQUESTS=1000

# Logging
LOG_LEVEL=info
DEBUG=false
```

### Generate Secure Keys

Run locally to generate secure keys:

```bash
# Generate secure keys (run locally)
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('API_TOKEN=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

---

## 🚀 Step 4: Deployment Process

### 1. Initialize Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project in your directory
cd jd-engineering-monitoring-api
railway init

# Link to existing project (if created via dashboard)
railway link
```

### 2. Deploy to Railway

```bash
# Deploy the application
railway up

# Monitor deployment
railway logs

# Check deployment status
railway status
```

### 3. Database Setup

```bash
# Connect to Railway PostgreSQL
railway connect Postgres

# Run initialization script
\i scripts/railway_init_db.sql

# Verify tables created
\dt

# Check sample data
SELECT * FROM device_registry;

# Exit
\q
```

### 4. Verify Deployment

```bash
# Get your Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health

# Test dashboard
curl https://your-app.railway.app/dashboard

# Test API endpoint
curl https://your-app.railway.app/devices
```

---

## 🔧 Step 5: Production Optimizations

### 1. Add Redis Service (Optional)

In Railway Dashboard:
1. Add new **Redis** service to your project
2. Railway will provide `REDIS_URL` automatically
3. Update environment variables to use Redis

### 2. Custom Domain Setup

```bash
# Add custom domain in Railway Dashboard
# 1. Go to Settings → Domains
# 2. Add your domain: dashboard.jd-mcllennan.com
# 3. Configure DNS records as shown
# 4. Railway provides automatic SSL
```

### 3. Monitoring Setup

Create `railway-monitoring.py` for Railway-specific monitoring:

```python
#!/usr/bin/env python3
"""
Railway Production Monitoring Script
Monitors the deployed application health and performance
"""

import requests
import time
import json
import os
from datetime import datetime

# Configuration
RAILWAY_URL = os.getenv("RAILWAY_URL", "https://your-app.railway.app")
HEALTH_ENDPOINT = f"{RAILWAY_URL}/health"
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Optional Slack notifications

def check_application_health():
    """Check application health on Railway"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check Passed: {health_data.get('status', 'unknown')}")
            return True, health_data
        else:
            print(f"❌ Health Check Failed: HTTP {response.status_code}")
            return False, {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False, {"error": str(e)}

def send_alert(message):
    """Send alert notification"""
    if WEBHOOK_URL:
        try:
            payload = {"text": f"🚨 Railway Alert: {message}"}
            requests.post(WEBHOOK_URL, json=payload, timeout=10)
        except Exception as e:
            print(f"Failed to send alert: {e}")

def main():
    """Main monitoring loop"""
    print("🔍 Starting Railway Production Monitoring")
    
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        timestamp = datetime.now().isoformat()
        healthy, data = check_application_health()
        
        if healthy:
            consecutive_failures = 0
            print(f"[{timestamp}] System healthy")
        else:
            consecutive_failures += 1
            print(f"[{timestamp}] System unhealthy ({consecutive_failures}/{max_failures})")
            
            if consecutive_failures >= max_failures:
                send_alert(f"Application health check failed {consecutive_failures} times")
                consecutive_failures = 0  # Reset after alert
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
```

---

## 📊 Step 6: Monitoring & Maintenance

### 1. Railway Dashboard Monitoring

Monitor these metrics in Railway Dashboard:
- **CPU Usage**: Should stay < 70%
- **Memory Usage**: Should stay < 80%
- **Request Volume**: Track API usage
- **Response Times**: Keep < 1 second
- **Error Rates**: Keep < 1%

### 2. Application Logs

```bash
# View real-time logs
railway logs --follow

# View specific service logs
railway logs --service Postgres

# Filter logs by level
railway logs --filter "ERROR"
```

### 3. Database Maintenance

```bash
# Connect to production database
railway connect Postgres

# Check database size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Monitor active connections
SELECT count(*) as active_connections FROM pg_stat_activity;

# Check query performance
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

---

## 🔒 Step 7: Security & Compliance

### 1. Environment Security

```bash
# Review environment variables
railway variables

# Rotate secrets regularly
railway variables set SECRET_KEY=new_secret_key_here
railway variables set API_TOKEN=new_api_token_here
```

### 2. Access Control

```bash
# Add team members with proper roles
railway invite user@company.com --role viewer

# Review project permissions
railway team list
```

### 3. SSL Configuration

Railway automatically provides:
- ✅ **SSL/TLS certificates** via Let's Encrypt
- ✅ **HTTP to HTTPS redirects**
- ✅ **Security headers**
- ✅ **DDoS protection**

---

## 🚨 Step 8: Troubleshooting

### Common Railway Issues

#### 1. Deployment Failures

```bash
# Check build logs
railway logs --deployment

# Verify Dockerfile
railway run docker build -f Dockerfile.production .

# Check environment variables
railway variables
```

#### 2. Database Connection Issues

```bash
# Test database connection
railway connect Postgres

# Check connection string
railway variables get DATABASE_URL

# Verify database initialization
railway run python3 -c "import asyncpg; print('PostgreSQL driver available')"
```

#### 3. Memory/Performance Issues

```bash
# Check resource usage in Railway Dashboard
# Upgrade plan if needed

# Optimize application
railway variables set GUNICORN_WORKERS=2  # Reduce if memory limited
```

#### 4. SSL/Domain Issues

```bash
# Check domain configuration in Railway Dashboard
# Verify DNS records
# Wait for SSL certificate provisioning (can take up to 24 hours)
```

---

## ✅ Step 9: Deployment Verification

### 1. Health Check Validation

```bash
# Test health endpoint
curl https://your-app.railway.app/health | jq

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-06-25T...",
  "environment": "production",
  "version": "2.0.0-production",
  "components": {
    "database": {
      "status": "healthy",
      "is_connected": true
    },
    "cache": {
      "status": "not_configured"
    },
    "websocket": {
      "status": "healthy",
      "active_connections": 0
    }
  }
}
```

### 2. Dashboard Verification

```bash
# Test dashboard access
curl https://your-app.railway.app/dashboard

# Test API endpoints
curl https://your-app.railway.app/devices \
  -H "Authorization: Bearer your_api_token"

# Test WebSocket (use browser console)
# const ws = new WebSocket('wss://your-app.railway.app/ws');
```

### 3. Performance Testing

```bash
# Install testing tools
pip install locust

# Create load test file
cat > railway_load_test.py << 'EOF'
from locust import HttpUser, task, between

class DashboardUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.headers = {"Authorization": "Bearer your_api_token"}
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/dashboard")
    
    @task(2)
    def check_health(self):
        self.client.get("/health")
    
    @task(1)
    def get_devices(self):
        self.client.get("/devices", headers=self.headers)
EOF

# Run load test
locust -f railway_load_test.py --host=https://your-app.railway.app
```

---

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Railway account setup complete
- [ ] Production files uploaded to repository
- [ ] Environment variables configured
- [ ] Database schema initialized
- [ ] Security keys generated and set
- [ ] Railway project created and linked

### Deployment
- [ ] Application deployed successfully
- [ ] Database connected and populated
- [ ] Health checks passing
- [ ] Dashboard accessible
- [ ] API endpoints responding
- [ ] WebSocket connections working

### Post-Deployment
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Monitoring alerts setup
- [ ] Performance testing completed
- [ ] Load testing passed
- [ ] Team access configured
- [ ] Backup procedures documented

### Ongoing Maintenance
- [ ] Daily health monitoring
- [ ] Weekly performance reviews
- [ ] Monthly security updates
- [ ] Quarterly load testing
- [ ] Log analysis and cleanup

---

## 📞 Support & Resources

### Railway Resources
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Community support
- **Railway Status**: [status.railway.app](https://status.railway.app)

### Application Support
- **Health Monitoring**: `https://your-app.railway.app/health`
- **Application Logs**: `railway logs --follow`
- **Database Access**: `railway connect Postgres`

### Emergency Procedures
1. **Application Down**: Check Railway status, review logs
2. **Database Issues**: Verify connection, check Railway dashboard
3. **Performance Issues**: Review metrics, scale resources if needed
4. **Security Concerns**: Rotate secrets, review access logs

---

**🏆 Railway Deployment Complete!**

Your J&D McLennan Engineering Dashboard is now deployed to Railway with enterprise-grade features:

✅ **Production-Ready**: Multi-worker Gunicorn with Uvicorn  
✅ **Database**: PostgreSQL with connection pooling  
✅ **Security**: JWT authentication, security headers  
✅ **Monitoring**: Health checks, performance metrics  
✅ **Real-time**: WebSocket support for live updates  
✅ **Scaling**: Auto-scaling ready with Railway  

**Live URL**: `https://your-app.railway.app/dashboard`

---

*Last Updated: 2024-06-25 | Version: 2.0.0-production* 