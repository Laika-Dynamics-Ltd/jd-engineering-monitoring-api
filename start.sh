#!/bin/bash

# Start script for Railway deployment with nginx
echo "🚀 Starting JD Engineering Monitoring Services..."

# Get the PORT from Railway or default to 8080
PORT=${PORT:-8080}

echo "📡 Configuring services to run on port $PORT..."

# Update nginx config with Railway's PORT
sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/nginx.conf

# Start supervisord which will manage all services
echo "🎛️ Starting supervisor to manage all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 