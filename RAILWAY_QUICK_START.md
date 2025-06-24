# Railway Quick Start Guide
## J&D McLennan Engineering Dashboard - Production Deployment

**Deploy the enterprise-grade dashboard to Railway in 15 minutes!**

---

## 🚀 1. Prerequisites (5 minutes)

### Install Railway CLI
```bash
npm install -g @railway/cli
```

### Login to Railway
```bash
railway login
```

### Verify Production Files
Ensure these files exist in your project:
- ✅ `main_production.py`
- ✅ `production_config.py` 
- ✅ `Dockerfile.production`
- ✅ `railway.json`
- ✅ `requirements.txt`
- ✅ `static/dashboard_production.html`

---

## 🔐 2. Generate Security Keys (2 minutes)

```bash
# Generate secure keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('API_TOKEN=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

**Save these keys - you'll need them in step 4!**

---

## 🏗️ 3. Setup Railway Project (3 minutes)

### Option A: Create New Project
```bash
railway init
# Follow prompts to create new project
```

### Option B: Connect to Existing Project
```bash
railway link
# Select your existing project
```

### Add PostgreSQL Service
In Railway Dashboard:
1. Click **"Add Service"**
2. Select **"PostgreSQL"**
3. Wait for deployment

---

## ⚙️ 4. Configure Environment Variables (3 minutes)

In Railway Dashboard → **Variables**, add:

```bash
# Required Variables
ENVIRONMENT=production
SECRET_KEY=your_generated_secret_key_here
API_TOKEN=your_generated_api_token_here
JWT_SECRET=your_generated_jwt_secret_here

# Performance Settings
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
GUNICORN_WORKERS=4
CACHE_TTL=300
API_RATE_LIMIT=100
METRICS_ENABLED=true

# Logging
LOG_LEVEL=info
DEBUG=false
```

**Note**: Railway automatically provides `DATABASE_URL` and `PORT`

---

## 🚀 5. Deploy Application (2 minutes)

```bash
# Deploy to Railway
railway up

# Monitor deployment
railway logs
```

**Wait for "Deployment completed" message**

---

## 🗄️ 6. Initialize Database (3 minutes)

```bash
# Connect to PostgreSQL
railway connect Postgres

# Run initialization script
\i scripts/railway_init_db.sql

# Verify setup
SELECT * FROM device_registry;

# Exit
\q
```

---

## ✅ 7. Verify Deployment (2 minutes)

```bash
# Get your Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health

# Test dashboard (in browser)
# https://your-app.railway.app/dashboard
```

**Expected Health Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "components": {
    "database": {"status": "healthy"},
    "websocket": {"status": "healthy"}
  }
}
```

---

## 🎯 Quick Verification Checklist

After deployment, verify:

- [ ] **Health Check**: `https://your-app.railway.app/health` returns 200
- [ ] **Dashboard**: `https://your-app.railway.app/dashboard` loads J&D McLennan branding
- [ ] **Device Data**: Dashboard shows 3 sample tablets
- [ ] **Business Intelligence**: KPIs display ($125/week, 98% efficiency)
- [ ] **Real-time**: Connection indicator shows "Real-time Connected"
- [ ] **API Access**: `/devices` endpoint requires authentication

---

## 🔧 Common Issues & Quick Fixes

### Deployment Failed
```bash
railway logs --deployment
# Check for missing environment variables or Docker build issues
```

### Database Connection Error
```bash
# Verify PostgreSQL service is running
railway status
# Check if DATABASE_URL is automatically set
railway variables
```

### 404 on Dashboard
```bash
# Ensure main_production.py is being used
# Check railway.json configuration
```

### Performance Issues
```bash
# Monitor resource usage in Railway Dashboard
# Reduce GUNICORN_WORKERS if memory limited
railway variables set GUNICORN_WORKERS=2
```

---

## 📊 Monitoring & Maintenance

### View Logs
```bash
railway logs --follow
```

### Monitor Performance
- Check Railway Dashboard metrics
- CPU should stay < 70%
- Memory should stay < 80%

### Database Maintenance
```bash
railway connect Postgres
-- Check table sizes
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename)) 
FROM pg_tables WHERE schemaname = 'public';
```

---

## 🎉 Success! You're Live!

**Your J&D McLennan Engineering Dashboard is now live with:**

✅ **Enterprise Features**: Real-time monitoring, business intelligence  
✅ **Production Security**: JWT auth, encrypted connections  
✅ **High Performance**: Database pooling, caching, WebSockets  
✅ **Professional Branding**: J&D McLennan logo and red/white theme  
✅ **Railway Infrastructure**: Auto-scaling, SSL, monitoring  

### **Access Your Dashboard:**
- **Main Dashboard**: `https://your-app.railway.app/dashboard`
- **Health Monitoring**: `https://your-app.railway.app/health`
- **API Documentation**: `https://your-app.railway.app/docs`

### **Key Features Available:**
- 🔴 **Live Device Monitoring** (3 tablets)
- 💰 **Business Intelligence** ($6.5K annual projection, $15K ROI)
- ⚡ **Real-time Updates** via WebSocket
- 📊 **Performance Analytics** (98% efficiency score)
- 🔒 **Enterprise Security** (JWT authentication)

---

## 🆘 Need Help?

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Check Logs**: `railway logs`
- **Health Status**: Monitor `/health` endpoint
- **Database Access**: `railway connect Postgres`

---

**🎯 Deployment Time: ~15 minutes**  
**🏆 Result: Enterprise-grade production dashboard**

*Ready for immediate business use with full monitoring and analytics!* 