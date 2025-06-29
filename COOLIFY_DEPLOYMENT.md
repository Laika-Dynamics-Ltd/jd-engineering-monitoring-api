# 🚀 Coolify Deployment - JD Engineering Tablet Monitoring API

## URGENT: Deploy Before 10:30AM Testing Session

### Option 1: Coolify Web UI Deployment (Recommended)

1. **Login to Coolify**
   - Access your Coolify instance
   - Go to Projects → Create New Project

2. **Create New Service**
   - Click "New Service"
   - Select "Docker Compose"
   - Name: `jd-tablet-monitoring-api`

3. **Configuration**
   ```yaml
   # Copy this entire docker-compose.yml content:
   version: '3.8'
   
   services:
     tablet-monitoring-api:
       image: python:3.11-slim
       container_name: jd-tablet-monitoring-api
       restart: unless-stopped
       ports:
         - "8000:8000"
       environment:
         - PORT=8000
         - PYTHONUNBUFFERED=1
         - PYTHONDONTWRITEBYTECODE=1
       working_dir: /app
       command: >
         sh -c "
         apt-get update && apt-get install -y curl git &&
         git clone https://github.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api.git . &&
         pip install -r requirements_simple.txt &&
         uvicorn main_simple:app --host 0.0.0.0 --port 8000
         "
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 60s
   ```

4. **Domain Configuration**
   - Domain: `tablet-monitoring.laikadynamics.com`
   - Port: `8000`
   - Enable SSL: Yes

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build

### Option 2: Direct Server Deployment (Backup)

If Coolify has issues, SSH to your server:

```bash
# SSH to your Coolify server
ssh your-server

# Clone and run directly
git clone https://github.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api.git
cd jd-engineering-monitoring-api
python3 -m pip install -r requirements_simple.txt
python3 -m uvicorn main_simple:app --host 0.0.0.0 --port 8000 &
```

### Testing After Deployment

1. **Health Check**
   ```bash
   curl https://tablet-monitoring.laikadynamics.com/health
   ```

2. **Tablet Metrics Test**
   ```bash
   curl -X POST https://tablet-monitoring.laikadynamics.com/tablet-metrics \
     -H "Authorization: Bearer ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681" \
     -H "Content-Type: application/json" \
     -d '{"device_id": "test_tablet", "location": "test_location"}'
   ```

### Update Tablet Script

Once deployed, update the bulletproof script on tablets:

```python
# In tablet_client_bulletproof.py, change:
API_URL = "https://tablet-monitoring.laikadynamics.com/tablet-metrics"
```

### 🚨 If All Else Fails - Emergency Local Solution

Run on your development machine:
```bash
python3 -m uvicorn main_simple:app --host 0.0.0.0 --port 8000 &

# Then use ngrok for temporary public access:
ngrok http 8000

# Update tablet script with ngrok URL
```

## ⏰ TIMELINE FOR 10:30AM SESSION

- **Now - 10:15am**: Deploy to Coolify
- **10:15 - 10:25am**: Test API endpoints
- **10:25am**: Update tablet script with new URL
- **10:30am**: Ready for Brad's TeamViewer testing

## 📱 After API is Working

Your tablet will show:
```
✅ SUCCESS - Battery:85% | WiFi:online | MYOB:False | Scanner:False | Success:1/1
```

Instead of the 502 errors you're seeing now.

**Priority**: Get this deployed in the next 15 minutes for your testing session! 