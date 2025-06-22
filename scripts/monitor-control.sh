#!/data/data/com.termux/files/usr/bin/bash

# Tablet Monitoring Service Control Script
# Usage: ./monitor-control.sh {start|stop|status|restart|logs}

SCRIPT_NAME="tablet_client.py"
PID_FILE="monitor.pid"
LOG_FILE="monitoring.log"

case "$1" in
  start)
    if [ -f $PID_FILE ]; then
      PID=$(cat $PID_FILE)
      if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Monitoring is already running (PID: $PID)"
        exit 1
      else
        echo "🧹 Cleaning up stale PID file..."
        rm $PID_FILE
      fi
    fi
    
    echo "🚀 Starting tablet monitoring..."
    python $SCRIPT_NAME > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    
    # Wait a moment to check if it started successfully
    sleep 2
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
      echo "✅ Monitoring started successfully (PID: $PID)"
      echo "📝 Logs: tail -f $LOG_FILE"
    else
      echo "❌ Failed to start monitoring"
      rm -f $PID_FILE
      exit 1
    fi
    ;;
    
  stop)
    if [ -f $PID_FILE ]; then
      PID=$(cat $PID_FILE)
      if ps -p $PID > /dev/null 2>&1; then
        echo "⏹️  Stopping monitoring (PID: $PID)..."
        kill $PID 2>/dev/null
        
        # Wait for process to stop
        for i in {1..10}; do
          if ! ps -p $PID > /dev/null 2>&1; then
            break
          fi
          sleep 1
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
          echo "🔨 Force stopping process..."
          kill -9 $PID 2>/dev/null
        fi
        
        rm $PID_FILE
        echo "✅ Monitoring stopped"
      else
        echo "⚠️  Process not running (cleaning up PID file)"
        rm $PID_FILE
      fi
    else
      echo "❌ No monitoring process found (no PID file)"
    fi
    ;;
    
  status)
    if [ -f $PID_FILE ]; then
      PID=$(cat $PID_FILE)
      if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Monitoring is running (PID: $PID)"
        
        # Show some process info
        ps -p $PID -o pid,ppid,etime,cmd 2>/dev/null
        
        # Show recent log entries
        echo ""
        echo "📊 Recent activity:"
        tail -5 $LOG_FILE 2>/dev/null || echo "No log data available"
        
        # Show log file size
        if [ -f $LOG_FILE ]; then
          SIZE=$(du -h $LOG_FILE | cut -f1)
          echo "📝 Log file size: $SIZE"
        fi
      else
        echo "❌ Monitoring is not running (stale PID file found)"
        echo "🧹 Cleaning up..."
        rm $PID_FILE
      fi
    else
      echo "❌ Monitoring is not running"
    fi
    ;;
    
  restart)
    echo "🔄 Restarting monitoring service..."
    $0 stop
    sleep 3
    $0 start
    ;;
    
  logs)
    if [ -f $LOG_FILE ]; then
      echo "📝 Following monitoring logs (Ctrl+C to exit):"
      echo "----------------------------------------"
      tail -f $LOG_FILE
    else
      echo "❌ Log file not found: $LOG_FILE"
      echo "💡 Start monitoring first: $0 start"
    fi
    ;;
    
  info)
    echo "📊 Tablet Monitoring Service Information"
    echo "========================================"
    echo "Script: $SCRIPT_NAME"
    echo "PID File: $PID_FILE"
    echo "Log File: $LOG_FILE"
    echo ""
    
    # Check if script exists
    if [ -f $SCRIPT_NAME ]; then
      echo "✅ Monitoring script found"
    else
      echo "❌ Monitoring script missing: $SCRIPT_NAME"
    fi
    
    # Check status
    $0 status
    
    # Show system info
    echo ""
    echo "🔋 System Information:"
    echo "Battery: $(termux-battery-status 2>/dev/null | grep percentage | cut -d':' -f2 | tr -d ' ,')"
    echo "WiFi: $(termux-wifi-connectioninfo 2>/dev/null | grep ssid | cut -d':' -f2 | tr -d ' ,"')"
    echo "Storage: $(df -h . | tail -1 | awk '{print $4" available"}')"
    ;;
    
  clean)
    echo "🧹 Cleaning up monitoring files..."
    
    # Stop if running
    if [ -f $PID_FILE ]; then
      echo "⏹️  Stopping monitoring first..."
      $0 stop
    fi
    
    # Archive old logs
    if [ -f $LOG_FILE ]; then
      mv $LOG_FILE "${LOG_FILE}.$(date +%Y%m%d_%H%M%S)"
      echo "📦 Archived log file"
    fi
    
    # Clean up any stale files
    rm -f $PID_FILE
    echo "✅ Cleanup complete"
    ;;
    
  *)
    echo "🚀 Tablet Monitoring Service Controller"
    echo "======================================"
    echo ""
    echo "Usage: $0 {start|stop|status|restart|logs|info|clean}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the monitoring service"
    echo "  stop     - Stop the monitoring service"
    echo "  status   - Show service status and recent activity"
    echo "  restart  - Restart the monitoring service"
    echo "  logs     - Follow real-time logs (Ctrl+C to exit)"
    echo "  info     - Show detailed system and service information"
    echo "  clean    - Stop service and clean up old files"
    echo ""
    echo "Examples:"
    echo "  $0 start           # Start monitoring"
    echo "  $0 status          # Check if running"
    echo "  $0 logs            # Watch live output"
    echo "  $0 restart         # Restart service"
    echo ""
    exit 1
    ;;
esac 