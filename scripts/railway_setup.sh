#!/bin/bash
# Railway Production Deployment Setup Script
# J&D McLennan Engineering Dashboard

set -e

echo "🚀 J&D McLennan Engineering - Railway Production Setup"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Railway CLI is installed
check_railway_cli() {
    log_info "Checking Railway CLI installation..."
    
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI not found. Installing..."
        npm install -g @railway/cli
        log_success "Railway CLI installed"
    else
        log_success "Railway CLI found"
    fi
}

# Generate secure keys
generate_secure_keys() {
    log_info "Generating secure keys for production..."
    
    echo ""
    echo "🔐 COPY THESE SECURE KEYS TO RAILWAY ENVIRONMENT VARIABLES:"
    echo "============================================================"
    
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    API_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    echo "SECRET_KEY=$SECRET_KEY"
    echo "API_TOKEN=$API_TOKEN"
    echo "JWT_SECRET=$JWT_SECRET"
    echo ""
    
    # Save to file for reference
    cat > .railway_keys.txt << EOF
# Railway Environment Variables - KEEP SECURE!
# Generated on $(date)

SECRET_KEY=$SECRET_KEY
API_TOKEN=$API_TOKEN
JWT_SECRET=$JWT_SECRET

# Additional required variables:
ENVIRONMENT=production
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
CACHE_TTL=300
API_RATE_LIMIT=100
METRICS_ENABLED=true
GUNICORN_WORKERS=4
LOG_LEVEL=info
DEBUG=false
EOF
    
    log_success "Keys saved to .railway_keys.txt (keep secure!)"
}

# Initialize Railway project
init_railway_project() {
    log_info "Initializing Railway project..."
    
    if [ ! -f ".railway/project.json" ]; then
        log_info "No existing Railway project found. Run 'railway init' manually."
        log_warning "Then run 'railway link' if connecting to existing project."
    else
        log_success "Railway project already initialized"
    fi
}

# Verify production files
verify_production_files() {
    log_info "Verifying production files..."
    
    required_files=(
        "main_production.py"
        "production_config.py"
        "Dockerfile.production"
        "railway.json"
        "requirements.txt"
        "static/dashboard_production.html"
        "scripts/healthcheck.sh"
    )
    
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        log_success "All production files present"
    else
        log_error "Missing production files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

# Deploy to Railway
deploy_to_railway() {
    log_info "Deploying to Railway..."
    
    log_info "Running 'railway up'..."
    railway up
    
    log_success "Deployment initiated"
    log_info "Monitor deployment with: railway logs"
}

# Post-deployment verification
verify_deployment() {
    log_info "Getting deployment URL..."
    
    RAILWAY_URL=$(railway domain 2>/dev/null || echo "")
    
    if [ -n "$RAILWAY_URL" ]; then
        log_success "Application deployed to: $RAILWAY_URL"
        
        log_info "Testing health endpoint..."
        if curl -f "$RAILWAY_URL/health" > /dev/null 2>&1; then
            log_success "Health check passed"
        else
            log_warning "Health check failed - application may still be starting"
        fi
        
        echo ""
        echo "🎯 DEPLOYMENT COMPLETE!"
        echo "======================="
        echo "Dashboard URL: $RAILWAY_URL/dashboard"
        echo "Health Check: $RAILWAY_URL/health"
        echo "API Docs: $RAILWAY_URL/docs"
        echo ""
        
    else
        log_warning "Could not determine Railway URL. Check Railway dashboard."
    fi
}

# Main setup process
main() {
    echo ""
    log_info "Starting Railway production setup..."
    echo ""
    
    # Step 1: Check Railway CLI
    check_railway_cli
    echo ""
    
    # Step 2: Generate secure keys
    generate_secure_keys
    echo ""
    
    # Step 3: Verify production files
    verify_production_files
    echo ""
    
    # Step 4: Initialize Railway project
    init_railway_project
    echo ""
    
    # Ask for confirmation before deployment
    echo "⚠️  IMPORTANT: Before deploying, ensure you have:"
    echo "   1. Set environment variables in Railway Dashboard"
    echo "   2. Added PostgreSQL service to your Railway project"
    echo "   3. Configured your custom domain (if applicable)"
    echo ""
    
    read -p "Ready to deploy to Railway? [y/N]: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Step 5: Deploy
        deploy_to_railway
        echo ""
        
        # Step 6: Verify deployment
        verify_deployment
        
        log_success "Railway setup complete!"
        
        echo ""
        echo "📋 NEXT STEPS:"
        echo "=============="
        echo "1. Monitor logs: railway logs --follow"
        echo "2. Set up database: railway connect Postgres"
        echo "3. Run database init: \i scripts/railway_init_db.sql"
        echo "4. Configure custom domain in Railway Dashboard"
        echo "5. Set up monitoring alerts"
        echo ""
        
    else
        log_info "Deployment cancelled. Run this script again when ready."
        echo ""
        echo "📋 TO DEPLOY MANUALLY:"
        echo "======================"
        echo "1. Set environment variables in Railway Dashboard"
        echo "2. Add PostgreSQL service"
        echo "3. Run: railway up"
        echo "4. Monitor: railway logs"
        echo ""
    fi
}

# Run main function
main "$@" 