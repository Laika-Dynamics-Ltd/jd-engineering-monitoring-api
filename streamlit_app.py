import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import time
import os

# Page configuration
st.set_page_config(
    page_title="JD Engineering Tablet Monitor",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .online-status {
        color: #28a745;
        font-weight: bold;
    }
    .offline-status {
        color: #dc3545;
        font-weight: bold;
    }
    .recent-status {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://jd-engineering-monitoring-api-production.up.railway.app")
API_TOKEN = os.getenv("API_TOKEN", "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681")

# For Railway deployment, use internal URL
if os.getenv("RAILWAY_ENVIRONMENT"):
    API_BASE_URL = "http://localhost:8000"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Helper functions
def fetch_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_status_color(status):
    """Get color based on device status"""
    colors = {
        "online": "#28a745",
        "recent": "#ffc107", 
        "offline": "#dc3545"
    }
    return colors.get(status, "#6c757d")

def format_time_ago(timestamp):
    """Format timestamp as time ago"""
    if not timestamp:
        return "Never"
    
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
            
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s ago"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}m ago"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() / 3600)}h ago"
        else:
            return f"{int(diff.total_seconds() / 86400)}d ago"
    except:
        return "Unknown"

# Sidebar
with st.sidebar:
    st.title("🎛️ Control Panel")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 30)
    
    # Time range selector
    st.subheader("📊 Analytics Time Range")
    time_range = st.selectbox(
        "Select time range",
        options=[1, 6, 12, 24, 48, 168],
        format_func=lambda x: f"Last {x} hours" if x < 168 else "Last week",
        index=3
    )
    
    # Manual refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    # API Status
    st.subheader("🔌 API Status")
    health = fetch_data("/health")
    if health:
        st.success("✅ API Connected")
        st.caption(f"Environment: {health.get('environment', 'unknown')}")
    else:
        st.error("❌ API Disconnected")

# Main content
st.title("📱 JD Engineering Tablet Monitoring Dashboard")
st.markdown("Real-time monitoring of tablet devices in engineering environments")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📱 Device Details", "📈 Analytics", "🔍 Session Issues"])

with tab1:
    # Fetch devices data
    devices = fetch_data("/devices")
    
    if devices:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_devices = len(devices)
        online_devices = len([d for d in devices if d.get('status') == 'online'])
        recent_devices = len([d for d in devices if d.get('status') == 'recent'])
        offline_devices = len([d for d in devices if d.get('status') == 'offline'])
        
        with col1:
            st.metric("Total Devices", total_devices, delta=None)
        with col2:
            st.metric("Online", online_devices, delta=None, delta_color="normal")
        with col3:
            st.metric("Recent", recent_devices, delta=None, delta_color="normal")
        with col4:
            st.metric("Offline", offline_devices, delta=None, delta_color="inverse")
        
        # Device status chart
        st.subheader("🟢 Device Status Distribution")
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # Pie chart
            status_counts = pd.DataFrame([
                {"Status": "Online", "Count": online_devices, "Color": "#28a745"},
                {"Status": "Recent", "Count": recent_devices, "Color": "#ffc107"},
                {"Status": "Offline", "Count": offline_devices, "Color": "#dc3545"}
            ])
            
            fig_pie = px.pie(
                status_counts, 
                values='Count', 
                names='Status',
                color='Status',
                color_discrete_map={'Online': '#28a745', 'Recent': '#ffc107', 'Offline': '#dc3545'}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Device table
            st.subheader("📋 Device List")
            
            # Prepare data for table
            device_data = []
            for device in devices:
                status_html = f"<span class='{device['status']}-status'>{device['status'].upper()}</span>"
                device_data.append({
                    "Device ID": device['device_id'],
                    "Name": device.get('device_name', 'Unknown'),
                    "Location": device.get('location', 'Unknown'),
                    "Status": status_html,
                    "Last Seen": format_time_ago(device.get('last_seen')),
                    "Sessions": device.get('total_sessions', 0),
                    "Timeouts": device.get('total_timeouts', 0)
                })
            
            df = pd.DataFrame(device_data)
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.subheader("📱 Device Metrics Dashboard")
    
    # Device selector
    devices = fetch_data("/devices")
    if devices:
        device_ids = [d['device_id'] for d in devices]
        selected_device = st.selectbox("Select Device", device_ids)
        
        if selected_device:
            # Fetch device metrics
            metrics = fetch_data(f"/devices/{selected_device}/metrics?hours={time_range}")
            
            if metrics:
                # Device info
                device_info = next((d for d in devices if d['device_id'] == selected_device), {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Device:** {device_info.get('device_name', selected_device)}")
                with col2:
                    st.info(f"**Location:** {device_info.get('location', 'Unknown')}")
                with col3:
                    status = device_info.get('status', 'unknown')
                    st.info(f"**Status:** {status.upper()}")
                
                # Metrics charts
                if metrics.get('device_metrics'):
                    st.subheader("🔋 Device Performance")
                    
                    # Battery level chart
                    battery_data = pd.DataFrame(metrics['device_metrics'])
                    if 'battery_level' in battery_data.columns:
                        fig_battery = px.line(
                            battery_data, 
                            x='timestamp', 
                            y='battery_level',
                            title='Battery Level Over Time',
                            labels={'battery_level': 'Battery %', 'timestamp': 'Time'}
                        )
                        fig_battery.update_layout(yaxis_range=[0, 100])
                        st.plotly_chart(fig_battery, use_container_width=True)
                    
                    # CPU usage chart
                    if 'cpu_usage' in battery_data.columns:
                        fig_cpu = px.line(
                            battery_data,
                            x='timestamp',
                            y='cpu_usage',
                            title='CPU Usage Over Time',
                            labels={'cpu_usage': 'CPU %', 'timestamp': 'Time'}
                        )
                        fig_cpu.update_layout(yaxis_range=[0, 100])
                        st.plotly_chart(fig_cpu, use_container_width=True)
                
                # Network metrics
                if metrics.get('network_metrics'):
                    st.subheader("📡 Network Status")
                    
                    network_data = pd.DataFrame(metrics['network_metrics'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # WiFi signal strength
                        if 'wifi_signal_strength' in network_data.columns:
                            fig_wifi = px.line(
                                network_data,
                                x='timestamp',
                                y='wifi_signal_strength',
                                title='WiFi Signal Strength',
                                labels={'wifi_signal_strength': 'Signal (dBm)', 'timestamp': 'Time'}
                            )
                            st.plotly_chart(fig_wifi, use_container_width=True)
                    
                    with col2:
                        # Connectivity status
                        if 'connectivity_status' in network_data.columns:
                            status_counts = network_data['connectivity_status'].value_counts()
                            fig_conn = px.pie(
                                values=status_counts.values,
                                names=status_counts.index,
                                title='Connectivity Status Distribution'
                            )
                            st.plotly_chart(fig_conn, use_container_width=True)

with tab3:
    st.subheader("📈 Session Analytics")
    
    # Fetch session analytics
    analytics = fetch_data(f"/analytics/session-issues?hours={time_range}")
    
    if analytics and analytics.get('session_analysis'):
        session_df = pd.DataFrame(analytics['session_analysis'])
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_timeouts = session_df['timeout_count'].sum() if 'timeout_count' in session_df else 0
        total_logins = session_df['login_count'].sum() if 'login_count' in session_df else 0
        total_errors = session_df['error_count'].sum() if 'error_count' in session_df else 0
        avg_duration = session_df['avg_session_duration'].mean() if 'avg_session_duration' in session_df else 0
        
        with col1:
            st.metric("Total Timeouts", int(total_timeouts))
        with col2:
            st.metric("Total Logins", int(total_logins))
        with col3:
            st.metric("Total Errors", int(total_errors))
        with col4:
            st.metric("Avg Session (min)", f"{int(avg_duration/60)}" if avg_duration else "0")
        
        # Timeout analysis by device
        if not session_df.empty:
            st.subheader("⏱️ Timeout Analysis by Device")
            
            fig_timeouts = px.bar(
                session_df.sort_values('timeout_count', ascending=True).tail(10),
                x='timeout_count',
                y='device_id',
                orientation='h',
                title='Top 10 Devices by Timeout Count',
                labels={'timeout_count': 'Number of Timeouts', 'device_id': 'Device'}
            )
            st.plotly_chart(fig_timeouts, use_container_width=True)
            
            # Session success rate
            st.subheader("✅ Session Success Rate")
            
            session_df['success_rate'] = (session_df['logout_count'] / 
                                         (session_df['login_count'] + 0.0001) * 100).round(2)
            
            fig_success = px.scatter(
                session_df,
                x='login_count',
                y='success_rate',
                size='timeout_count',
                hover_data=['device_name', 'location'],
                title='Session Success Rate vs Login Count',
                labels={'success_rate': 'Success Rate (%)', 'login_count': 'Number of Logins'}
            )
            st.plotly_chart(fig_success, use_container_width=True)

with tab4:
    st.subheader("🔍 Session Issues Deep Dive")
    
    # Fetch detailed analytics
    analytics = fetch_data(f"/analytics/session-issues?hours={time_range}")
    
    if analytics:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Problem devices table
            st.subheader("⚠️ Devices with Issues")
            
            if analytics.get('session_analysis'):
                session_df = pd.DataFrame(analytics['session_analysis'])
                
                # Filter devices with issues
                problem_devices = session_df[
                    (session_df['timeout_count'] > 0) | 
                    (session_df['error_count'] > 0)
                ].sort_values('timeout_count', ascending=False)
                
                if not problem_devices.empty:
                    st.dataframe(
                        problem_devices[['device_id', 'device_name', 'location', 
                                       'timeout_count', 'error_count', 'last_activity']],
                        use_container_width=True
                    )
                else:
                    st.success("✅ No devices with issues!")
        
        with col2:
            # Network correlation
            st.subheader("📡 Network Correlation")
            
            if analytics.get('network_correlation'):
                network_df = pd.DataFrame(analytics['network_correlation'])
                
                if not network_df.empty:
                    # Average metrics
                    avg_offline = network_df['offline_count'].mean()
                    avg_signal = network_df['avg_signal_strength'].mean()
                    
                    st.metric("Avg Offline Events", f"{avg_offline:.1f}")
                    st.metric("Avg Signal Strength", f"{avg_signal:.1f} dBm")
                    
                    # Correlation hint
                    if avg_signal < -70:
                        st.warning("⚠️ Poor WiFi signal detected")
                    if avg_offline > 5:
                        st.warning("⚠️ Frequent disconnections detected")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.caption("🚀 JD Engineering Tablet Monitoring System | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 