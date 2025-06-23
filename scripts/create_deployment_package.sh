#!/bin/bash

# Create deployment package for tablet
echo "📦 Creating Tablet Deployment Package"
echo "======================================"

# Create deployment directory
DEPLOY_DIR="tablet_deployment"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy essential files
echo "📋 Copying essential files..."

# Main monitoring script
cp tablet_client_working.py "$DEPLOY_DIR/"
echo "✅ tablet_client_working.py"

# Startup script
cp start_monitoring_simple.sh "$DEPLOY_DIR/"
echo "✅ start_monitoring_simple.sh"

# Deployment guide
cp DEPLOY_TO_TABLET.md "$DEPLOY_DIR/"
echo "✅ DEPLOY_TO_TABLET.md"

# Create a simple README for the package
cat > "$DEPLOY_DIR/README.txt" << 'EOF'
JD Engineering Tablet Monitor - Deployment Package
==================================================

FILES INCLUDED:
- tablet_client_working.py    (Main monitoring script)
- start_monitoring_simple.sh  (Easy startup script)
- DEPLOY_TO_TABLET.md         (Deployment instructions)

QUICK START:
1. Copy these files to your Android tablet
2. Open Termux on the tablet
3. Navigate to where you copied the files
4. Run: chmod +x *.sh *.py
5. Run: ./start_monitoring_simple.sh

For detailed instructions, see DEPLOY_TO_TABLET.md

API Endpoint: https://jd-engineering-monitoring-api-production.up.railway.app
Dashboard: https://jd-engineering-monitoring-api-production.up.railway.app/dashboard
EOF

echo "✅ README.txt"

# Make scripts executable
chmod +x "$DEPLOY_DIR"/*.sh
chmod +x "$DEPLOY_DIR"/*.py

echo ""
echo "🎉 Deployment package created in: $DEPLOY_DIR/"
echo ""
echo "📱 To deploy to tablet:"
echo "1. Copy the entire '$DEPLOY_DIR' folder to your tablet"
echo "2. Follow the instructions in DEPLOY_TO_TABLET.md"
echo ""
echo "📁 Package contents:"
ls -la "$DEPLOY_DIR/" 