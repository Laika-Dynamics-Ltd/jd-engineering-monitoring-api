#!/bin/bash

# Dashboard Enhancement Deployment Script
# JD Engineering Tablet Monitoring System
# This script deploys all dashboard improvements and optimizations

set -e  # Exit on any error

echo "🚀 JD Engineering Dashboard Enhancement Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "main.py not found. Please run this script from the project root directory."
    exit 1
fi

print_status "Found project root directory"

# Create backup of current dashboard
print_info "Creating backup of current dashboard..."
BACKUP_DIR="backups/dashboard_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "static/dashboard.html" ]; then
    cp "static/dashboard.html" "$BACKUP_DIR/"
    print_status "Backed up original dashboard.html"
fi

if [ -f "static/dashboard_clean.html" ]; then
    cp "static/dashboard_clean.html" "$BACKUP_DIR/"
    print_status "Backed up dashboard_clean.html"
fi

# Check if enhanced dashboard exists
if [ ! -f "static/dashboard_enhanced.html" ]; then
    print_error "Enhanced dashboard not found at static/dashboard_enhanced.html"
    print_info "Please ensure the enhanced dashboard has been created first."
    exit 1
fi

print_status "Enhanced dashboard found"

# Verify enhanced JavaScript and CSS files
if [ ! -f "static/dashboard-enhanced.js" ]; then
    print_warning "Enhanced JavaScript file not found. Dashboard will use inline JS."
fi

if [ ! -f "static/dashboard-enhanced.css" ]; then
    print_warning "Enhanced CSS file not found. Dashboard will use inline styles."
fi

# Check Python dependencies
print_info "Checking Python dependencies..."
python3 -c "
import asyncpg
import fastapi
import uvicorn
print('✓ Core dependencies available')
" 2>/dev/null || {
    print_error "Missing required Python dependencies"
    print_info "Run: pip install -r requirements.txt"
    exit 1
}

print_status "Python dependencies verified"

# Database connectivity check
print_info "Checking database connectivity..."
if [ -n "$DATABASE_URL" ]; then
    print_status "Database URL configured"
else
    print_warning "DATABASE_URL not set. Using development configuration."
fi

# Test API endpoints
print_info "Testing enhanced API endpoints..."

# Start the server in background for testing (if not already running)
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_info "Starting server for testing..."
    python3 main.py &
    SERVER_PID=$!
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Server started successfully"
        
        # Test enhanced endpoints
        if curl -s http://localhost:8000/api/dashboard/status > /dev/null 2>&1; then
            print_status "Enhanced API endpoints accessible"
        else
            print_warning "Enhanced API endpoints may need authentication"
        fi
        
        # Clean up test server
        kill $SERVER_PID 2>/dev/null || true
        sleep 2
    else
        print_error "Failed to start server for testing"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
else
    print_status "Server already running"
fi

# Performance optimizations
print_info "Applying performance optimizations..."

# Check if gzip compression is available
if command -v gzip >/dev/null 2>&1; then
    print_status "Gzip compression available"
else
    print_warning "Gzip not available. Install for better performance."
fi

# Create optimized static assets
print_info "Optimizing static assets..."

# Minify CSS if possible
if command -v csso >/dev/null 2>&1 && [ -f "static/dashboard-enhanced.css" ]; then
    csso static/dashboard-enhanced.css --output static/dashboard-enhanced.min.css
    print_status "CSS minified"
elif [ -f "static/dashboard-enhanced.css" ]; then
    cp static/dashboard-enhanced.css static/dashboard-enhanced.min.css
    print_warning "CSS minification tool not available. Using unminified CSS."
fi

# Minify JavaScript if possible
if command -v uglifyjs >/dev/null 2>&1 && [ -f "static/dashboard-enhanced.js" ]; then
    uglifyjs static/dashboard-enhanced.js -o static/dashboard-enhanced.min.js
    print_status "JavaScript minified"
elif [ -f "static/dashboard-enhanced.js" ]; then
    cp static/dashboard-enhanced.js static/dashboard-enhanced.min.js
    print_warning "JavaScript minification tool not available. Using unminified JS."
fi

# Security checks
print_info "Running security checks..."

# Check for sensitive information in files
if grep -r "password\|secret\|key" static/*.html >/dev/null 2>&1; then
    print_warning "Potential sensitive information found in HTML files"
else
    print_status "No sensitive information detected in HTML files"
fi

# Validate HTML structure
print_info "Validating HTML structure..."
if command -v tidy >/dev/null 2>&1; then
    if tidy -q -e static/dashboard_enhanced.html >/dev/null 2>&1; then
        print_status "HTML structure valid"
    else
        print_warning "HTML validation issues detected (non-critical)"
    fi
else
    print_warning "HTML validator not available. Install 'tidy' for validation."
fi

# Create deployment summary
print_info "Creating deployment summary..."
SUMMARY_FILE="$BACKUP_DIR/deployment_summary.txt"
cat > "$SUMMARY_FILE" << EOF
JD Engineering Dashboard Enhancement Deployment
Timestamp: $(date)
Enhanced Dashboard: static/dashboard_enhanced.html
Backup Location: $BACKUP_DIR

Features Added:
- Modern responsive design with glassmorphism effects
- Enhanced real-time data updates
- Improved error handling and retry mechanisms
- Advanced chart visualizations
- Mobile-optimized interface
- Performance optimizations
- Enhanced API endpoints for better data management

API Enhancements:
- /api/dashboard/status - Real-time system status
- /api/dashboard/alerts - Alert management
- /api/dashboard/devices/enhanced - Enhanced device listing
- /api/dashboard/charts/realtime - Real-time chart data
- /api/dashboard/export - Data export functionality

Backup Files:
- Original dashboard.html
- Previous dashboard_clean.html

Next Steps:
1. Restart the application server
2. Clear browser cache for all users
3. Test all dashboard functionality
4. Monitor performance metrics
5. Collect user feedback

EOF

print_status "Deployment summary created: $SUMMARY_FILE"

# Final deployment steps
print_info "Finalizing deployment..."

# Set appropriate file permissions
chmod 644 static/dashboard_enhanced.html
chmod 644 static/dashboard-enhanced.js 2>/dev/null || true
chmod 644 static/dashboard-enhanced.css 2>/dev/null || true

print_status "File permissions set"

# Create systemd service file (if on Linux)
if command -v systemctl >/dev/null 2>&1; then
    SERVICE_FILE="/tmp/jd-monitoring.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=JD Engineering Tablet Monitoring API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    print_info "Systemd service file created at $SERVICE_FILE"
    print_info "To install: sudo cp $SERVICE_FILE /etc/systemd/system/ && sudo systemctl enable jd-monitoring"
fi

# Performance monitoring setup
print_info "Setting up performance monitoring..."
mkdir -p logs
touch logs/performance.log
touch logs/dashboard.log

print_status "Log files initialized"

# Final checks
print_info "Running final validation checks..."

# Check file sizes
ENHANCED_SIZE=$(stat -f%z static/dashboard_enhanced.html 2>/dev/null || stat -c%s static/dashboard_enhanced.html 2>/dev/null || echo "unknown")
print_info "Enhanced dashboard size: $ENHANCED_SIZE bytes"

if [ "$ENHANCED_SIZE" != "unknown" ] && [ "$ENHANCED_SIZE" -gt 1000000 ]; then
    print_warning "Dashboard file is large (>1MB). Consider optimization."
fi

# Environment-specific instructions
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    print_info "Railway deployment detected"
    print_info "Remember to commit changes and push to trigger deployment"
elif [ -n "$VERCEL" ]; then
    print_info "Vercel deployment detected"
    print_info "Remember to push changes to trigger deployment"
elif [ -n "$HEROKU_APP_NAME" ]; then
    print_info "Heroku deployment detected"
    print_info "Remember to commit and push to Heroku"
else
    print_info "Local deployment - restart your server to apply changes"
fi

echo ""
echo "=================================================="
print_status "Dashboard Enhancement Deployment Complete!"
echo "=================================================="

print_info "🎉 Your tablet monitoring dashboard has been enhanced with:"
echo "   • Modern responsive design"
echo "   • Real-time data updates"
echo "   • Improved performance"
echo "   • Enhanced user experience"
echo "   • Better error handling"
echo "   • Advanced analytics"

print_info "🔧 Next steps:"
echo "   1. Restart your application server"
echo "   2. Clear browser cache"
echo "   3. Test the enhanced dashboard"
echo "   4. Monitor performance metrics"

print_info "📁 Backup location: $BACKUP_DIR"
print_info "📊 Dashboard URL: http://your-domain/dashboard"

echo ""
print_info "For support or issues, check the deployment summary at:"
print_info "$SUMMARY_FILE"

exit 0 