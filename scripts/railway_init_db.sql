-- J&D McLennan Engineering Database Schema for Railway
-- Production-grade table creation with optimizations
-- Execute this after connecting to Railway PostgreSQL: railway connect Postgres

\echo 'Initializing J&D McLennan Engineering Production Database...'

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

\echo 'Extensions created...'

-- Device registry table with Railway optimizations
CREATE TABLE IF NOT EXISTS device_registry (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(100),
    location VARCHAR(100),
    android_version VARCHAR(50),
    app_version VARCHAR(50),
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    total_sessions INTEGER DEFAULT 0,
    total_timeouts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

\echo 'Device registry table created...'

-- Device metrics with partitioning-ready structure
CREATE TABLE IF NOT EXISTS device_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
    battery_temperature FLOAT,
    memory_available BIGINT CHECK (memory_available >= 0),
    memory_total BIGINT CHECK (memory_total >= 0),
    storage_available BIGINT CHECK (storage_available >= 0),
    cpu_usage FLOAT CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

\echo 'Device metrics table created...'

-- Network metrics table
CREATE TABLE IF NOT EXISTS network_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    wifi_signal_strength INTEGER CHECK (wifi_signal_strength >= -100 AND wifi_signal_strength <= 0),
    wifi_ssid VARCHAR(100),
    connectivity_status VARCHAR(20) NOT NULL CHECK (connectivity_status IN ('online', 'offline', 'limited', 'unknown')),
    network_type VARCHAR(50),
    ip_address INET,
    dns_response_time FLOAT CHECK (dns_response_time >= 0),
    data_usage_mb FLOAT CHECK (data_usage_mb >= 0),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

\echo 'Network metrics table created...'

-- App metrics table
CREATE TABLE IF NOT EXISTS app_metrics (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    screen_state VARCHAR(20) NOT NULL CHECK (screen_state IN ('active', 'locked', 'dimmed', 'off')),
    app_foreground VARCHAR(200),
    app_memory_usage BIGINT CHECK (app_memory_usage >= 0),
    screen_timeout_setting INTEGER CHECK (screen_timeout_setting >= 0),
    last_user_interaction TIMESTAMPTZ,
    notification_count INTEGER CHECK (notification_count >= 0),
    app_crashes INTEGER CHECK (app_crashes >= 0),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

\echo 'App metrics table created...'

-- Session events table
CREATE TABLE IF NOT EXISTS session_events (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL REFERENCES device_registry(device_id),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('login', 'logout', 'timeout', 'error', 'reconnect', 'session_start', 'session_end')),
    session_id VARCHAR(100),
    duration INTEGER CHECK (duration >= 0),
    error_message TEXT,
    user_id VARCHAR(100),
    app_version VARCHAR(50),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

\echo 'Session events table created...'

-- Performance indexes for Railway
CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id_timestamp ON device_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_network_metrics_device_id_timestamp ON network_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_app_metrics_device_id_timestamp ON app_metrics(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_session_events_device_id_timestamp ON session_events(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_device_registry_active ON device_registry(is_active, last_seen DESC);

\echo 'Performance indexes created...'

-- Insert sample data for testing
INSERT INTO device_registry (device_id, device_name, location, android_version, app_version) VALUES
('tablet-001', 'Production Tablet 1', 'Warehouse A', '11.0', '2.1.0'),
('tablet-002', 'Production Tablet 2', 'Warehouse B', '11.0', '2.1.0'),
('tablet-003', 'Production Tablet 3', 'Office', '12.0', '2.1.0')
ON CONFLICT (device_id) DO NOTHING;

\echo 'Sample data inserted...'

-- Insert sample device metrics
INSERT INTO device_metrics (device_id, battery_level, memory_available, memory_total, cpu_usage) VALUES
('tablet-001', 85, 2048000000, 4096000000, 12.5),
('tablet-002', 72, 1536000000, 4096000000, 8.3),
('tablet-003', 91, 3072000000, 8192000000, 15.2)
ON CONFLICT DO NOTHING;

\echo 'Sample device metrics inserted...'

-- Insert sample network metrics
INSERT INTO network_metrics (device_id, wifi_signal_strength, wifi_ssid, connectivity_status, network_type) VALUES
('tablet-001', -45, 'JD_McLennan_Warehouse', 'online', 'wifi'),
('tablet-002', -52, 'JD_McLennan_Warehouse', 'online', 'wifi'),
('tablet-003', -38, 'JD_McLennan_Office', 'online', 'wifi')
ON CONFLICT DO NOTHING;

\echo 'Sample network metrics inserted...'

-- Performance monitoring view
CREATE OR REPLACE VIEW device_health_summary AS
SELECT 
    dr.device_id,
    dr.device_name,
    dr.location,
    dr.is_active,
    dr.last_seen,
    COALESCE(dm.battery_level, 80) as battery_level,
    COALESCE(nm.connectivity_status, 'online') as connectivity_status,
    COALESCE(am.screen_state, 'active') as screen_state
FROM device_registry dr
LEFT JOIN LATERAL (
    SELECT battery_level 
    FROM device_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) dm ON true
LEFT JOIN LATERAL (
    SELECT connectivity_status 
    FROM network_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) nm ON true
LEFT JOIN LATERAL (
    SELECT screen_state 
    FROM app_metrics 
    WHERE device_id = dr.device_id 
    ORDER BY timestamp DESC 
    LIMIT 1
) am ON true;

\echo 'Performance monitoring view created...'

-- Business intelligence view for Railway
CREATE OR REPLACE VIEW business_intelligence_summary AS
SELECT 
    COUNT(*) as total_devices,
    COUNT(*) FILTER (WHERE is_active = true) as active_devices,
    COUNT(*) FILTER (WHERE last_seen > NOW() - INTERVAL '1 hour') as devices_online_last_hour,
    ROUND(AVG(COALESCE(
        (SELECT battery_level FROM device_metrics dm WHERE dm.device_id = dr.device_id ORDER BY timestamp DESC LIMIT 1), 
        80
    )), 2) as avg_battery_level,
    SUM(total_sessions) as total_sessions_all_time,
    SUM(total_timeouts) as total_timeouts_all_time,
    CASE 
        WHEN SUM(total_sessions) > 0 
        THEN ROUND((SUM(total_timeouts)::FLOAT / SUM(total_sessions)) * 100, 2)
        ELSE 0 
    END as timeout_rate_percent
FROM device_registry dr;

\echo 'Business intelligence view created...'

-- Create update trigger for device registry
CREATE OR REPLACE FUNCTION update_device_last_seen()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE device_registry 
    SET last_seen = NOW(), updated_at = NOW()
    WHERE device_id = NEW.device_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_device_last_seen
    AFTER INSERT ON device_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_device_last_seen();

\echo 'Database triggers created...'

-- Grant permissions (Railway handles this automatically but included for completeness)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO CURRENT_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO CURRENT_USER;

\echo 'Permissions granted...'

-- Display summary
\echo ''
\echo '===================================================='
\echo 'J&D McLennan Engineering Database Initialization Complete!'
\echo '===================================================='
\echo ''

-- Show table summary
\echo 'Tables created:'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo 'Sample data verification:'
SELECT * FROM device_health_summary;

\echo ''
\echo 'Business intelligence summary:'
SELECT * FROM business_intelligence_summary;

\echo ''
\echo '✅ Database ready for production use!'
\echo 'Next steps:'
\echo '1. Deploy application to Railway'
\echo '2. Test health endpoint: https://your-app.railway.app/health'
\echo '3. Access dashboard: https://your-app.railway.app/dashboard'
\echo '' 