#!/data/data/com.termux/files/usr/bin/bash
# JD Engineering Complete Tablet Manager v1.0
# Fully automated deployment, TeamViewer bypass, and background management

API_BASE_URL="https://jd-engineering-monitoring-api-production-5d93.up.railway.app"
GITHUB_RAW_URL="https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment"
LOG_FILE="jd_monitoring.log"
PID_FILE="jd_monitoring.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

show_banner() {
    clear
    echo "================================================================"
    echo "🚀 JD ENGINEERING COMPLETE TABLET MANAGER v1.0"
    echo "================================================================"
    echo "📱 Full deployment automation for monitoring tablets"
    echo "🔓 Android 15 TeamViewer bypass included"
    echo "⚙️  Background management and auto-start"
    echo "================================================================"
    echo ""
}

detect_tablet_type() {
    if [ -f "tablet_config.txt" ]; then
        TABLET_TYPE=$(cat tablet_config.txt)
        log "📋 Found existing config: $TABLET_TYPE"
        return 0
    fi
    
    echo "Which tablet type is this?"
    echo "1) Test Tablet (TeamViewer security testing)"
    echo "2) Electrical Department (Production MYOB)"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1) TABLET_TYPE="test" ;;
        2) TABLET_TYPE="electrical" ;;
        *) error "Invalid choice. Exiting."; exit 1 ;;
    esac
    
    echo "$TABLET_TYPE" > tablet_config.txt
    log "💾 Saved tablet type: $TABLET_TYPE"
}

install_dependencies() {
    log "📦 Installing required packages..."
    pkg update -y > /dev/null 2>&1
    pkg install python termux-api curl wget -y > /dev/null 2>&1
    pip install requests > /dev/null 2>&1
    log "✅ Dependencies installed"
}

download_monitoring_scripts() {
    log "📥 Downloading monitoring scripts..."
    
    if [ "$TABLET_TYPE" = "test" ]; then
        SCRIPT_NAME="test_tablet_client.py"
    else
        SCRIPT_NAME="electrical_tablet_client.py"
    fi
    
    if curl -L -s "$GITHUB_RAW_URL/$SCRIPT_NAME" -o "$SCRIPT_NAME"; then
        chmod +x "$SCRIPT_NAME"
        log "✅ Downloaded $SCRIPT_NAME"
    else
        error "❌ Failed to download $SCRIPT_NAME"
        return 1
    fi
}

setup_teamviewer_bypass() {
    log "🔓 Setting up TeamViewer bypass..."
    
    cat > "teamviewer_bypass.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
echo "🔓 Starting TeamViewer bypass..."

# Grant permissions
pm grant com.teamviewer.quicksupport.android android.permission.SYSTEM_ALERT_WINDOW 2>/dev/null
pm grant com.teamviewer.quicksupport.android android.permission.WRITE_SECURE_SETTINGS 2>/dev/null

# Enable accessibility
settings put secure accessibility_enabled 1 2>/dev/null
settings put secure enabled_accessibility_services com.teamviewer.quicksupport.android/.AccessibilityService 2>/dev/null

# Disable security
settings put global development_settings_enabled 1 2>/dev/null
settings put global stay_on_while_plugged_in 7 2>/dev/null

# Start TeamViewer
am start com.teamviewer.quicksupport.android/.MainActivity 2>/dev/null

# Open accessibility settings
sleep 2
am start -a android.settings.ACCESSIBILITY_SETTINGS 2>/dev/null

echo "✅ TeamViewer bypass applied!"
echo "📱 Please enable TeamViewer in Accessibility Settings"
EOF

    chmod +x teamviewer_bypass.sh
    log "✅ TeamViewer bypass script created"
    
    if [ "$TABLET_TYPE" = "test" ]; then
        log "🧪 Running TeamViewer bypass..."
        ./teamviewer_bypass.sh
    fi
}

setup_auto_start() {
    log "⚙️ Setting up auto-start..."
    
    cat > "jd_auto_start.sh" << EOF
#!/data/data/com.termux/files/usr/bin/bash
cd "\$(dirname "\$0")"

if [ -f "$PID_FILE" ]; then
    OLD_PID=\$(cat "$PID_FILE")
    if ps -p "\$OLD_PID" > /dev/null 2>&1; then
        echo "🔄 Already running (PID: \$OLD_PID)"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

echo "🚀 Starting monitoring..."
nohup python "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
echo "\$!" > "$PID_FILE"
echo "✅ Started (PID: \$!)"
EOF

    chmod +x jd_auto_start.sh
    
    # Boot auto-start
    mkdir -p ~/.termux/boot/
    echo "#!/data/data/com.termux/files/usr/bin/bash" > ~/.termux/boot/jd_monitoring.sh
    echo "sleep 30 && cd \"$PWD\" && ./jd_auto_start.sh" >> ~/.termux/boot/jd_monitoring.sh
    chmod +x ~/.termux/boot/jd_monitoring.sh
    
    log "✅ Auto-start configured"
}

start_monitoring() {
    log "🚀 Starting monitoring..."
    
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            log "⚠️ Already running (PID: $OLD_PID)"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    nohup python "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
    echo "$!" > "$PID_FILE"
    log "✅ Started (PID: $!)"
}

stop_monitoring() {
    log "🛑 Stopping monitoring..."
    
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            kill "$OLD_PID"
            sleep 2
            kill -9 "$OLD_PID" 2>/dev/null
            rm -f "$PID_FILE"
            log "✅ Stopped"
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    pkill -f "$SCRIPT_NAME" 2>/dev/null
}

show_status() {
    echo ""
    echo "📊 TABLET STATUS"
    echo "================"
    echo "📱 Type: ${TABLET_TYPE:-Unknown}"
    echo "⏰ Time: $(date '+%H:%M:%S')"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Monitoring: RUNNING (PID: $PID)"
        else
            echo "❌ Monitoring: STOPPED"
        fi
    else
        echo "❌ Monitoring: NOT RUNNING"
    fi
    
    if curl -s "$API_BASE_URL/health" > /dev/null; then
        echo "✅ API: ONLINE"
    else
        echo "❌ API: OFFLINE"
    fi
    echo ""
}

full_deployment() {
    log "🚀 Starting full deployment..."
    
    detect_tablet_type
    install_dependencies
    download_monitoring_scripts
    setup_teamviewer_bypass
    setup_auto_start
    start_monitoring
    
    echo ""
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "=========================="
    echo "📱 Tablet Type: $TABLET_TYPE"
    echo "🔄 Monitoring: Started"
    echo "📋 Log File: $LOG_FILE"
    echo ""
    echo "🎯 COMMANDS:"
    echo "   Status: ./complete_tablet_manager.sh status"
    echo "   Logs: tail -f $LOG_FILE"
    echo "   Dashboard: $API_BASE_URL/dashboard"
    echo ""
    if [ "$TABLET_TYPE" = "test" ]; then
        echo "🔓 TEAMVIEWER: Enable in Accessibility Settings"
    fi
    echo ""
}

show_menu() {
    echo "🎛️  MENU"
    echo "========"
    echo "1) 🚀 Quick Setup"
    echo "2) ▶️  Start"
    echo "3) ⏹️  Stop"
    echo "4) 🔄 Restart"
    echo "5) 📊 Status"
    echo "6) 📋 Logs"
    echo "7) 🔓 TeamViewer Bypass"
    echo "8) 🚪 Exit"
    read -p "Choice (1-8): " choice
}

main() {
    show_banner
    
    # Load config
    if [ -f "tablet_config.txt" ]; then
        TABLET_TYPE=$(cat tablet_config.txt)
        SCRIPT_NAME="${TABLET_TYPE}_tablet_client.py"
    fi
    
    # Command line args
    case "$1" in
        "deploy") full_deployment; exit 0 ;;
        "start") start_monitoring; exit 0 ;;
        "stop") stop_monitoring; exit 0 ;;
        "restart") stop_monitoring; sleep 2; start_monitoring; exit 0 ;;
        "status") show_status; exit 0 ;;
        "logs") tail -f "$LOG_FILE"; exit 0 ;;
        "bypass") ./teamviewer_bypass.sh 2>/dev/null || setup_teamviewer_bypass; exit 0 ;;
    esac
    
    # Show status if configured
    if [ -f "tablet_config.txt" ]; then
        show_status
    fi
    
    # Interactive menu
    while true; do
        show_menu
        case $choice in
            1) full_deployment ;;
            2) start_monitoring ;;
            3) stop_monitoring ;;
            4) stop_monitoring; sleep 2; start_monitoring ;;
            5) show_status ;;
            6) tail -n 20 "$LOG_FILE" 2>/dev/null || echo "No logs found" ;;
            7) ./teamviewer_bypass.sh 2>/dev/null || setup_teamviewer_bypass ;;
            8) log "👋 Exiting..."; exit 0 ;;
            *) error "Invalid choice" ;;
        esac
        echo ""
        read -p "Press Enter..."
    done
}

main "$@"
