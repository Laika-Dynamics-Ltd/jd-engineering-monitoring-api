#!/bin/bash
# Production Health Check Script for J&D McLennan Engineering Dashboard
# Performs comprehensive health validation

set -e

# Configuration
HEALTH_URL="http://localhost:8000/health"
TIMEOUT=10
MAX_RETRIES=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local expected_status="$2"
    local timeout="$3"
    
    log "Checking HTTP endpoint: $url"
    
    response=$(curl -s -w "%{http_code}" -o /tmp/health_response.json --connect-timeout "$timeout" "$url" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "HTTP endpoint responding correctly (Status: $response)"
        return 0
    else
        log_error "HTTP endpoint check failed (Status: $response, Expected: $expected_status)"
        return 1
    fi
}

# Function to validate health response structure
validate_health_response() {
    log "Validating health response structure..."
    
    if [ ! -f "/tmp/health_response.json" ]; then
        log_error "Health response file not found"
        return 1
    fi
    
    # Check if response contains required fields
    if grep -q '"status"' /tmp/health_response.json && \
       grep -q '"timestamp"' /tmp/health_response.json && \
       grep -q '"components"' /tmp/health_response.json; then
        log_success "Health response structure is valid"
        
        # Check if status is healthy or degraded
        status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' /tmp/health_response.json | cut -d'"' -f4)
        if [ "$status" = "healthy" ] || [ "$status" = "degraded" ]; then
            log_success "System status: $status"
            return 0
        else
            log_error "System status is unhealthy: $status"
            return 1
        fi
    else
        log_error "Health response structure is invalid"
        return 1
    fi
}

# Function to check WebSocket connectivity
check_websocket() {
    log "Checking WebSocket connectivity..."
    
    # Try to establish WebSocket connection (basic check)
    if command -v nc >/dev/null 2>&1; then
        if nc -z localhost 8000; then
            log_success "WebSocket port is accessible"
            return 0
        else
            log_warning "WebSocket port check failed"
            return 1
        fi
    else
        log_warning "netcat not available, skipping WebSocket check"
        return 0
    fi
}

# Function to check memory usage
check_memory_usage() {
    log "Checking memory usage..."
    
    if command -v free >/dev/null 2>&1; then
        memory_usage=$(free | grep Mem | awk '{printf("%.1f", ($3/$2) * 100.0)}')
        memory_threshold=85.0
        
        if (( $(echo "$memory_usage < $memory_threshold" | bc -l) )); then
            log_success "Memory usage is acceptable: ${memory_usage}%"
            return 0
        else
            log_warning "High memory usage detected: ${memory_usage}%"
            return 0  # Warning only, not a failure
        fi
    else
        log_warning "Memory check tools not available"
        return 0
    fi
}

# Function to check disk space
check_disk_space() {
    log "Checking disk space..."
    
    disk_usage=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
    disk_threshold=90
    
    if [ "$disk_usage" -lt "$disk_threshold" ]; then
        log_success "Disk usage is acceptable: ${disk_usage}%"
        return 0
    else
        log_warning "High disk usage detected: ${disk_usage}%"
        return 0  # Warning only, not a failure
    fi
}

# Main health check function
main_health_check() {
    log "=== J&D McLennan Engineering Dashboard Health Check ==="
    log "Starting comprehensive health validation..."
    
    local exit_code=0
    
    # HTTP endpoint check
    if ! check_http_endpoint "$HEALTH_URL" "200" "$TIMEOUT"; then
        exit_code=1
    fi
    
    # Validate health response structure
    if ! validate_health_response; then
        exit_code=1
    fi
    
    # WebSocket connectivity check
    if ! check_websocket; then
        log_warning "WebSocket check failed, but continuing..."
    fi
    
    # System resource checks
    check_memory_usage
    check_disk_space
    
    # Cleanup
    rm -f /tmp/health_response.json
    
    if [ $exit_code -eq 0 ]; then
        log_success "=== All critical health checks passed ==="
    else
        log_error "=== Health check failed ==="
    fi
    
    return $exit_code
}

# Retry logic
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if main_health_check; then
        exit 0
    fi
    
    retry_count=$((retry_count + 1))
    if [ $retry_count -lt $MAX_RETRIES ]; then
        log "Health check failed, retrying ($retry_count/$MAX_RETRIES)..."
        sleep 2
    fi
done

log_error "Health check failed after $MAX_RETRIES attempts"
exit 1 