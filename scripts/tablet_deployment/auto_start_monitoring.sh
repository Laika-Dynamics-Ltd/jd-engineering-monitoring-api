#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# JD ENGINEERING TABLET MONITOR - AUTO-START SCRIPT
# This script ensures the monitoring runs 24/7 automatically
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/tablet_client_bulletproof.py"
LOG_FILE="$SCRIPT_DIR/monitor.log"
PID_FILE="$SCRIPT_DIR/monitor.pid"
MAX_RESTARTS=5
RESTART_DELAY=10

echo "🚀 JD Engineering Tablet Monitor - Auto-Start System"
echo "============================================================"
echo "Script Dir: $SCRIPT_DIR"
echo "Monitor Script: $MONITOR_SCRIPT"
echo "Log File: $LOG_FILE"
echo "============================================================"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if monitor is running
is_monitor_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        else
            rm -f "$PID_FILE"  # Clean up stale PID file
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to start the monitor
start_monitor() {
    log_message "🚀 Starting tablet monitor..."
    
    # Kill any existing instances
    pkill -f "tablet_client_bulletproof.py" 2>/dev/null || true
    sleep 2
    
    # Start in background and save PID
    cd "$SCRIPT_DIR"
    nohup python3 "$MONITOR_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    # Verify it started
    sleep 5
    if is_monitor_running; then
        log_message "✅ Monitor started successfully (PID: $pid)"
        return 0
    else
        log_message "❌ Failed to start monitor"
        return 1
    fi
}

# Function to stop the monitor
stop_monitor() {
    if is_monitor_running; then
        local pid=$(cat "$PID_FILE")
        log_message "🛑 Stopping monitor (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 3
        kill -9 "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
        log_message "✅ Monitor stopped"
    else
        log_message "ℹ️  Monitor was not running"
    fi
}

# Function to restart the monitor
restart_monitor() {
    log_message "🔄 Restarting monitor..."
    stop_monitor
    sleep 2
    start_monitor
}

# Function to keep monitor alive (watchdog)
keep_alive() {
    local restart_count=0
    
    log_message "👁️  Starting watchdog mode..."
    
    while true; do
        if is_monitor_running; then
            log_message "✅ Monitor is running healthy"
            restart_count=0  # Reset counter on success
        else
            log_message "⚠️  Monitor not running, attempting restart ($((restart_count + 1))/$MAX_RESTARTS)"
            
            if [ $restart_count -lt $MAX_RESTARTS ]; then
                start_monitor
                restart_count=$((restart_count + 1))
                
                if ! is_monitor_running; then
                    log_message "❌ Restart failed. Waiting $RESTART_DELAY seconds..."
                    sleep $RESTART_DELAY
                fi
            else
                log_message "🚨 Max restarts reached. Manual intervention required."
                log_message "🚨 Check logs and restart manually: $0 start"
                break
            fi
        fi
        
        # Check every 60 seconds
        sleep 60
    done
}

# Main command handling
case "${1:-start}" in
    "start")
        log_message "📱 Auto-start command received"
        if is_monitor_running; then
            log_message "ℹ️  Monitor already running"
        else
            start_monitor
        fi
        ;;
    
    "stop")
        log_message "🛑 Stop command received"
        stop_monitor
        ;;
    
    "restart")
        log_message "🔄 Restart command received"
        restart_monitor
        ;;
    
    "status")
        if is_monitor_running; then
            local pid=$(cat "$PID_FILE")
            log_message "✅ Monitor is running (PID: $pid)"
            echo "✅ RUNNING"
        else
            log_message "❌ Monitor is not running"
            echo "❌ STOPPED"
        fi
        ;;
    
    "watchdog"|"keep-alive")
        keep_alive
        ;;
    
    "logs")
        echo "📋 Recent logs:"
        tail -50 "$LOG_FILE" 2>/dev/null || echo "No logs found"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|watchdog|logs}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the monitoring service"
        echo "  stop      - Stop the monitoring service"  
        echo "  restart   - Restart the monitoring service"
        echo "  status    - Check if service is running"
        echo "  watchdog  - Keep service alive (auto-restart)"
        echo "  logs      - Show recent log entries"
        exit 1
        ;;
esac 