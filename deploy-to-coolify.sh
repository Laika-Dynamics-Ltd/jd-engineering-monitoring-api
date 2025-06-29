#!/bin/bash

# JD Engineering Tablet Monitoring API - Coolify Deployment Script

echo "🚀 Deploying JD Engineering Tablet Monitoring API to Coolify"
echo "============================================================"

# Configuration
COOLIFY_HOST=${COOLIFY_HOST:-"your-coolify-server.com"}
PROJECT_NAME="jd-tablet-monitoring"
SERVICE_NAME="tablet-monitoring-api"

echo "📦 Building Docker image..."
docker build -f Dockerfile.simple -t $SERVICE_NAME:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful"
else
    echo "❌ Docker build failed"
    exit 1
fi

echo "🧪 Testing Docker image locally..."
docker run --rm -d --name test-$SERVICE_NAME -p 8001:8000 $SERVICE_NAME:latest

sleep 5

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Local test successful"
    docker stop test-$SERVICE_NAME
else
    echo "❌ Local test failed"
    docker stop test-$SERVICE_NAME
    exit 1
fi

echo "📋 Docker Compose Configuration:"
echo "================================"
cat docker-compose.yml

echo ""
echo "🔧 Next Steps for Coolify Deployment:"
echo "1. Copy the docker-compose.yml to your Coolify instance"
echo "2. Create a new service in Coolify using the compose file"
echo "3. Set domain: tablet-monitoring.laikadynamics.com"
echo "4. Deploy the service"
echo ""
echo "✅ Ready for Coolify deployment!"

# Test locally first
echo "🧪 Testing API endpoints locally:"
echo "Health: curl http://localhost:8001/health"
echo "Docs: http://localhost:8001/docs" 