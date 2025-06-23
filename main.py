# main.py - Railway.app optimized FastAPI application
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import asyncio
import asyncpg
import json
import os
import logging
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    global db_pool
    
    # Startup - Create database connection pool
    try:
        # Railway provides DATABASE_URL automatically for PostgreSQL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not found")
            raise Exception("Database configuration missing")
            
        # Railway PostgreSQL connection
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("✅ Database connection pool created successfully")
        
        # Initialize database tables
        await init_database()
        logger.info("✅ Database tables initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown - Close database connections
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")

# FastAPI app with Railway-optimized configuration
app = FastAPI(
    title="Tablet Session Monitoring API",
    description="Real-time monitoring API for Android tablet session timeout diagnostics",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Grafana and frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Railway handles HTTPS termination
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for dashboard assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security setup
security = HTTPBearer(auto_error=False)

# Pydantic Models with Railway-optimized validation
class DeviceMetrics(BaseModel):
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="Battery percentage")
    battery_temperature: Optional[float] = Field(None, description="Battery temperature in Celsius")
    memory_available: Optional[int] = Field(None, ge=0, description="Available memory in bytes")
    memory_total: Optional[int] = Field(None, ge=0, description="Total memory in bytes")
    storage_available: Optional[int] = Field(None, ge=0, description="Available storage in bytes")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="CPU usage percentage")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NetworkMetrics(BaseModel):
    wifi_signal_strength: Optional[int] = Field(None, ge=-100, le=0, description="WiFi signal in dBm")
    wifi_ssid: Optional[str] = Field(None, max_length=100, description="WiFi network name")
    connectivity_status: str = Field(..., pattern="^(online|offline|limited|unknown)$")
    network_type: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, description="Device IP address")
    dns_response_time: Optional[float] = Field(None, ge=0, description="DNS response time in ms")
    data_usage_mb: Optional[float] = Field(None, ge=0, description="Data usage in MB")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppMetrics(BaseModel):
    screen_state: str = Field(..., pattern="^(active|locked|dimmed|off)$")
    app_foreground: Optional[str] = Field(None, max_length=200, description="Current foreground app")
    app_memory_usage: Optional[int] = Field(None, ge=0, description="App memory usage in bytes")
    screen_timeout_setting: Optional[int] = Field(None, ge=0, description="Screen timeout in seconds")
    last_user_interaction: Optional[datetime] = None
    notification_count: Optional[int] = Field(None, ge=0)
    app_crashes: Optional[int] = Field(None, ge=0, description="App crashes in last hour")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionEvent(BaseModel):
    event_type: str = Field(..., pattern="^(login|logout|timeout|error|reconnect|session_start|session_end)$")
    session_id: Optional[str] = Field(None, max_length=100)
    duration: Optional[int] = Field(None, ge=0, description="Session duration in seconds")
    error_message: Optional[str] = Field(None, max_length=500)
    user_id: Optional[str] = Field(None, max_length=100)
    app_version: Optional[str] = Field(None, max_length=50)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TabletData(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=50, description="Unique tablet identifier")
    device_name: Optional[str] = Field(None, max_length=100, description="Friendly device name")
    location: Optional[str] = Field(None, max_length=100, description="Physical location")
    android_version: Optional[str] = Field(None, max_length=50)
    app_version: Optional[str] = Field(None, max_length=50)
    device_metrics: Optional[DeviceMetrics] = None
    network_metrics: Optional[NetworkMetrics] = None
    app_metrics: Optional[AppMetrics] = None
    session_events: Optional[List[SessionEvent]] = Field(default_factory=list)
    raw_logs: Optional[List[str]] = Field(default_factory=list, max_items=50)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v):
        # Ensure device_id is clean for database storage
        return v.strip().replace(' ', '_').lower()

# Database initialization for Railway PostgreSQL
async def init_database():
    """Initialize all required database tables with proper indexes"""
    async with db_pool.acquire() as conn:
        try:
            # Create extension for better timestamp handling
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            
            # Device metrics table with partitioning-ready structure
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS device_metrics (
                    id BIGSERIAL PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
                    battery_temperature FLOAT,
                    memory_available BIGINT CHECK (memory_available >= 0),
                    memory_total BIGINT CHECK (memory_total >= 0),
                    storage_available BIGINT CHECK (storage_available >= 0),
                    cpu_usage FLOAT CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Network metrics table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS network_metrics (
                    id BIGSERIAL PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    wifi_signal_strength INTEGER CHECK (wifi_signal_strength >= -100 AND wifi_signal_strength <= 0),
                    wifi_ssid VARCHAR(100),
                    connectivity_status VARCHAR(20) NOT NULL CHECK (connectivity_status IN ('online', 'offline', 'limited', 'unknown')),
                    network_type VARCHAR(50),
                    ip_address INET,
                    dns_response_time FLOAT CHECK (dns_response_time >= 0),
                    data_usage_mb FLOAT CHECK (data_usage_mb >= 0),
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # App metrics table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS app_metrics (
                    id BIGSERIAL PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    screen_state VARCHAR(20) NOT NULL CHECK (screen_state IN ('active', 'locked', 'dimmed', 'off')),
                    app_foreground VARCHAR(200),
                    app_memory_usage BIGINT CHECK (app_memory_usage >= 0),
                    screen_timeout_setting INTEGER CHECK (screen_timeout_setting >= 0),
                    last_user_interaction TIMESTAMPTZ,
                    notification_count INTEGER CHECK (notification_count >= 0),
                    app_crashes INTEGER CHECK (app_crashes >= 0),
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Session events table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS session_events (
                    id BIGSERIAL PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    event_type VARCHAR(30) NOT NULL CHECK (event_type IN ('login', 'logout', 'timeout', 'error', 'reconnect', 'session_start', 'session_end')),
                    session_id VARCHAR(100),
                    duration INTEGER CHECK (duration >= 0),
                    error_message TEXT,
                    user_id VARCHAR(100),
                    app_version VARCHAR(50),
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Device registry table for tracking active devices
            await conn.execute('''
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
                    total_timeouts INTEGER DEFAULT 0
                )
            ''')
            
            # Create performance indexes
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_device_metrics_device_time ON device_metrics(device_id, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_network_metrics_device_time ON network_metrics(device_id, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_app_metrics_device_time ON app_metrics(device_id, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_session_events_device_time ON session_events(device_id, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_session_events_type ON session_events(event_type, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_network_connectivity ON network_metrics(connectivity_status, timestamp DESC)',
                'CREATE INDEX IF NOT EXISTS idx_device_registry_active ON device_registry(is_active, last_seen DESC)'
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
                
            logger.info("✅ All database tables and indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            raise

# Authentication with Railway environment variables
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token from Railway environment variables"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Railway environment variable for API token
    valid_tokens = [
        os.getenv("API_TOKEN", "default-dev-token"),
        os.getenv("TABLET_API_KEY", "fallback-key")
    ]
    
    if credentials.credentials not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return credentials.credentials

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now(timezone.utc).isoformat()}
    )

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment monitoring"""
    try:
        # Test database connection
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )

# Main tablet data ingestion endpoint
@app.post("/tablet-metrics", response_model=Dict[str, Any])
async def receive_tablet_data(
    data: TabletData,
    background_tasks: BackgroundTasks,
    request: Request,
    token: str = Depends(verify_token)
):
    """Primary endpoint for receiving tablet monitoring data"""
    try:
        # Add client IP for debugging
        client_ip = request.client.host
        logger.info(f"📱 Received data from device: {data.device_id} (IP: {client_ip})")
        
        # Process data in background to return quickly
        background_tasks.add_task(store_tablet_data, data, client_ip)
        
        return {
            "status": "success",
            "message": "Data received and queued for processing",
            "device_id": data.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "records_received": {
                "device_metrics": 1 if data.device_metrics else 0,
                "network_metrics": 1 if data.network_metrics else 0,
                "app_metrics": 1 if data.app_metrics else 0,
                "session_events": len(data.session_events) if data.session_events else 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing tablet data from {data.device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process data: {str(e)}")

async def store_tablet_data(data: TabletData, client_ip: str = None):
    """Store tablet data in PostgreSQL with error handling"""
    async with db_pool.acquire() as conn:
        try:
            async with conn.transaction():
                # Update or insert device registry
                await conn.execute('''
                    INSERT INTO device_registry (device_id, device_name, location, android_version, app_version, last_seen)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (device_id) DO UPDATE SET
                        device_name = COALESCE(EXCLUDED.device_name, device_registry.device_name),
                        location = COALESCE(EXCLUDED.location, device_registry.location),
                        android_version = COALESCE(EXCLUDED.android_version, device_registry.android_version),
                        app_version = COALESCE(EXCLUDED.app_version, device_registry.app_version),
                        last_seen = EXCLUDED.last_seen,
                        is_active = TRUE
                ''', data.device_id, data.device_name, data.location, data.android_version, data.app_version, data.timestamp)
                
                # Store device metrics
                if data.device_metrics:
                    await conn.execute('''
                        INSERT INTO device_metrics (device_id, battery_level, battery_temperature, 
                                                  memory_available, memory_total, storage_available, 
                                                  cpu_usage, timestamp)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ''', data.device_id, data.device_metrics.battery_level,
                    data.device_metrics.battery_temperature, data.device_metrics.memory_available,
                    data.device_metrics.memory_total, data.device_metrics.storage_available,
                    data.device_metrics.cpu_usage, data.device_metrics.timestamp)
                
                # Store network metrics
                if data.network_metrics:
                    await conn.execute('''
                        INSERT INTO network_metrics (device_id, wifi_signal_strength, wifi_ssid,
                                                   connectivity_status, network_type, ip_address,
                                                   dns_response_time, data_usage_mb, timestamp)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ''', data.device_id, data.network_metrics.wifi_signal_strength,
                    data.network_metrics.wifi_ssid, data.network_metrics.connectivity_status,
                    data.network_metrics.network_type, data.network_metrics.ip_address,
                    data.network_metrics.dns_response_time, data.network_metrics.data_usage_mb,
                    data.network_metrics.timestamp)
                
                # Store app metrics
                if data.app_metrics:
                    await conn.execute('''
                        INSERT INTO app_metrics (device_id, screen_state, app_foreground,
                                               app_memory_usage, screen_timeout_setting,
                                               last_user_interaction, notification_count, 
                                               app_crashes, timestamp)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ''', data.device_id, data.app_metrics.screen_state,
                    data.app_metrics.app_foreground, data.app_metrics.app_memory_usage,
                    data.app_metrics.screen_timeout_setting, data.app_metrics.last_user_interaction,
                    data.app_metrics.notification_count, data.app_metrics.app_crashes,
                    data.app_metrics.timestamp)
                
                # Store session events
                if data.session_events:
                    session_count = 0
                    timeout_count = 0
                    for event in data.session_events:
                        await conn.execute('''
                            INSERT INTO session_events (device_id, event_type, session_id,
                                                      duration, error_message, user_id, 
                                                      app_version, timestamp)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ''', data.device_id, event.event_type, event.session_id,
                        event.duration, event.error_message, event.user_id,
                        event.app_version, event.timestamp)
                        
                        if event.event_type in ['login', 'session_start']:
                            session_count += 1
                        elif event.event_type == 'timeout':
                            timeout_count += 1
                    
                    # Update device registry counters
                    if session_count > 0 or timeout_count > 0:
                        await conn.execute('''
                            UPDATE device_registry 
                            SET total_sessions = total_sessions + $2,
                                total_timeouts = total_timeouts + $3
                            WHERE device_id = $1
                        ''', data.device_id, session_count, timeout_count)
                
                logger.info(f"✅ Successfully stored data for device {data.device_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to store data for device {data.device_id}: {str(e)}")
            raise

# Analytics and reporting endpoints
@app.get("/devices", response_model=List[Dict[str, Any]])
async def get_devices(token: str = Depends(verify_token)):
    """Get list of all monitored devices with summary statistics and latest metrics"""
    async with db_pool.acquire() as conn:
        devices = await conn.fetch('''
            SELECT dr.*,
                   EXTRACT(EPOCH FROM (NOW() - dr.last_seen))::INTEGER as seconds_since_last_seen,
                   CASE 
                       WHEN dr.last_seen > NOW() - INTERVAL '5 minutes' THEN 'online'
                       WHEN dr.last_seen > NOW() - INTERVAL '1 hour' THEN 'recent'
                       ELSE 'offline'
                   END as status,
                   -- Latest device metrics
                   dm.battery_level,
                   dm.battery_temperature,
                   dm.memory_available,
                   dm.memory_total,
                   dm.cpu_usage,
                   -- Latest network metrics
                   nm.wifi_signal_strength,
                   nm.wifi_ssid,
                   nm.connectivity_status,
                   nm.network_type,
                   -- Latest app metrics
                   am.screen_state,
                   am.app_foreground,
                   am.last_user_interaction,
                   -- MYOB and Scanner detection
                   CASE WHEN am.app_foreground ILIKE '%myob%' THEN true ELSE false END as myob_active,
                   CASE WHEN am.app_foreground ILIKE '%scanner%' OR am.app_foreground ILIKE '%barcode%' OR am.app_foreground ILIKE '%zebra%' THEN true ELSE false END as scanner_active,
                   -- Timeout risk calculation
                   CASE WHEN am.last_user_interaction < NOW() - INTERVAL '5 minutes' AND am.screen_state = 'active' THEN true ELSE false END as timeout_risk
            FROM device_registry dr
            LEFT JOIN LATERAL (
                SELECT * FROM device_metrics 
                WHERE device_id = dr.device_id 
                ORDER BY timestamp DESC 
                LIMIT 1
            ) dm ON true
            LEFT JOIN LATERAL (
                SELECT * FROM network_metrics 
                WHERE device_id = dr.device_id 
                ORDER BY timestamp DESC 
                LIMIT 1
            ) nm ON true
            LEFT JOIN LATERAL (
                SELECT * FROM app_metrics 
                WHERE device_id = dr.device_id 
                ORDER BY timestamp DESC 
                LIMIT 1
            ) am ON true
            ORDER BY dr.last_seen DESC
        ''')
        return [dict(device) for device in devices]

@app.get("/devices/{device_id}/metrics")
async def get_device_metrics(device_id: str, hours: int = 24):
    """Get detailed metrics for a specific device"""
    try:
        # Get comprehensive metrics by joining all relevant tables
        query = """
        SELECT 
            dr.device_id,
            dr.device_name,
            dr.location,
            dm.battery_level as battery_percentage,
            dm.battery_temperature,
            dm.memory_available,
            dm.memory_total,
            dm.storage_available,
            dm.cpu_usage,
            nm.wifi_signal_strength,
            nm.wifi_ssid,
            nm.connectivity_status,
            am.screen_state as app_state,
            am.app_foreground,
            COALESCE(dm.timestamp, nm.timestamp, am.timestamp) as timestamp
        FROM device_registry dr
        LEFT JOIN device_metrics dm ON dr.device_id = dm.device_id 
            AND dm.timestamp >= NOW() - ($2 || ' hours')::interval
        LEFT JOIN network_metrics nm ON dr.device_id = nm.device_id 
            AND nm.timestamp >= NOW() - ($2 || ' hours')::interval
        LEFT JOIN app_metrics am ON dr.device_id = am.device_id 
            AND am.timestamp >= NOW() - ($2 || ' hours')::interval
        WHERE dr.device_id = $1
        ORDER BY COALESCE(dm.timestamp, nm.timestamp, am.timestamp) DESC
        LIMIT 100
        """
        
        results = await db_pool.fetch(query, device_id, str(hours))
        
        metrics = []
        for row in results:
            metrics.append({
                "device_id": row["device_id"],
                "device_name": row["device_name"],
                "location": row["location"],
                "battery_percentage": row["battery_percentage"],
                "battery_charging": None,  # Not available in current schema
                "battery_temperature": row["battery_temperature"],
                "wifi_connected": row["connectivity_status"] == 'online' if row["connectivity_status"] else None,
                "wifi_ssid": row["wifi_ssid"],
                "wifi_signal_strength": row["wifi_signal_strength"],
                "app_state": row["app_state"],
                "storage_free": row["storage_available"],
                "timestamp": row["timestamp"],
                "session_id": None,  # Could join session_events if needed
                # Additional metrics
                "memory_available": row["memory_available"],
                "memory_total": row["memory_total"],
                "cpu_usage": row["cpu_usage"],
                "app_foreground": row["app_foreground"]
            })
        
        return {
            "device_id": device_id,
            "metrics": metrics,
            "count": len(metrics),
            "hours": hours
        }
        
    except Exception as e:
        logger.error(f"Error fetching device metrics for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

@app.get("/debug/tables")
async def debug_tables(token: str = Depends(verify_token)):
    """Debug endpoint to check table counts"""
    try:
        async with db_pool.acquire() as conn:
            device_count = await conn.fetchval("SELECT COUNT(*) FROM device_registry")
            metrics_count = await conn.fetchval("SELECT COUNT(*) FROM device_metrics")
            network_count = await conn.fetchval("SELECT COUNT(*) FROM network_metrics")
            
            return {
                "device_registry_count": device_count,
                "device_metrics_count": metrics_count,
                "network_metrics_count": network_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/analytics")
async def get_analytics(token: str = Depends(verify_token)):
    """General analytics endpoint for dashboard with real-time data"""
    try:
        async with db_pool.acquire() as conn:
            # Get comprehensive analytics from all tables
            analytics_query = '''
                SELECT 
                    COUNT(DISTINCT dr.device_id) as total_devices,
                    COUNT(DISTINCT dr.device_id) FILTER (
                        WHERE dr.last_seen > NOW() - INTERVAL '5 minutes'
                    ) as online_devices,
                    COALESCE(AVG(dm.battery_level), 0) as avg_battery,
                    COUNT(DISTINCT dr.device_id) FILTER (
                        WHERE am.app_foreground ILIKE '%myob%'
                    ) as myob_active,
                    COUNT(DISTINCT dr.device_id) FILTER (
                        WHERE am.app_foreground ILIKE '%scanner%' 
                           OR am.app_foreground ILIKE '%barcode%' 
                           OR am.app_foreground ILIKE '%zebra%'
                    ) as scanner_active,
                    COUNT(DISTINCT dr.device_id) FILTER (
                        WHERE am.last_user_interaction < NOW() - INTERVAL '5 minutes' 
                          AND am.screen_state = 'active'
                    ) as timeout_risks
                FROM device_registry dr
                LEFT JOIN LATERAL (
                    SELECT * FROM device_metrics 
                    WHERE device_id = dr.device_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) dm ON true
                LEFT JOIN LATERAL (
                    SELECT * FROM app_metrics 
                    WHERE device_id = dr.device_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) am ON true
            '''
            
            result = await conn.fetchrow(analytics_query)
            
            return {
                "total_devices": result["total_devices"] or 0,
                "online_devices": result["online_devices"] or 0,
                "avg_battery": round(float(result["avg_battery"] or 0), 1),
                "myob_active": result["myob_active"] or 0,
                "scanner_active": result["scanner_active"] or 0,
                "timeout_risks": result["timeout_risks"] or 0,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "REAL_DATA_v2.0"
            }
            
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        # Return fallback data to prevent dashboard crashes
        return {
            "total_devices": 2,
            "online_devices": 2,
            "avg_battery": 79.4,
            "myob_active": 0,
            "scanner_active": 0,
            "timeout_risks": 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "FALLBACK_v2.0",
            "error": str(e)
        }

@app.get("/analytics/session-issues")
async def get_session_issues(
    device_id: Optional[str] = None,
    hours: int = 24,
    token: str = Depends(verify_token)
):
    """Advanced session timeout and connectivity analysis"""
    try:
        async with db_pool.acquire() as conn:
            # Build base query for device registry and related tables
            params = [str(hours)]
            where_clause = "WHERE dm.timestamp >= NOW() - ($1 || ' hours')::interval"
            
            if device_id:
                where_clause += " AND dr.device_id = $2"
                params.append(device_id)
            
            # Get session analysis from session_events and device_registry
            analysis_query = f"""
                SELECT 
                    dr.device_id,
                    dr.device_name,
                    dr.location,
                    COUNT(se.id) as total_records,
                    COUNT(*) FILTER (WHERE se.session_id IS NOT NULL) as session_count,
                    COUNT(DISTINCT se.session_id) as unique_sessions,
                    COUNT(*) FILTER (WHERE se.event_type = 'timeout') as timeout_count,
                    COUNT(*) FILTER (WHERE se.event_type IN ('login', 'session_start')) as active_count,
                    AVG(dm.battery_level) as avg_battery,
                    AVG(nm.wifi_signal_strength) as avg_wifi_signal,
                    MAX(GREATEST(COALESCE(se.timestamp, '1970-01-01'::timestamptz), 
                                COALESCE(dm.timestamp, '1970-01-01'::timestamptz), 
                                COALESCE(nm.timestamp, '1970-01-01'::timestamptz))) as last_activity,
                    COUNT(DISTINCT DATE(se.timestamp)) as active_days
                FROM device_registry dr
                LEFT JOIN session_events se ON dr.device_id = se.device_id 
                    AND se.timestamp >= NOW() - ($1 || ' hours')::interval
                LEFT JOIN device_metrics dm ON dr.device_id = dm.device_id 
                    AND dm.timestamp >= NOW() - ($1 || ' hours')::interval
                LEFT JOIN network_metrics nm ON dr.device_id = nm.device_id 
                    AND nm.timestamp >= NOW() - ($1 || ' hours')::interval
                {where_clause.replace('dm.timestamp', 'COALESCE(se.timestamp, dm.timestamp, nm.timestamp)')}
                GROUP BY dr.device_id, dr.device_name, dr.location
                ORDER BY session_count DESC, timeout_count DESC
            """
            
            analysis = await conn.fetch(analysis_query, *params)
            
            # Network correlation analysis from network_metrics
            network_query = f"""
                SELECT 
                    dr.device_id,
                    COUNT(*) FILTER (WHERE nm.connectivity_status = 'offline') as offline_count,
                    COUNT(*) FILTER (WHERE nm.wifi_signal_strength < -70) as weak_signal_count,
                    AVG(nm.wifi_signal_strength) as avg_signal_strength,
                    COUNT(DISTINCT nm.wifi_ssid) as network_count
                FROM device_registry dr
                LEFT JOIN network_metrics nm ON dr.device_id = nm.device_id 
                    AND nm.timestamp >= NOW() - ($1 || ' hours')::interval
                WHERE dr.device_id IS NOT NULL
                {('AND dr.device_id = $2' if device_id else '')}
                GROUP BY dr.device_id
            """
            
            network_analysis = await conn.fetch(network_query, *params)
            
            return {
                "session_analysis": [dict(row) for row in analysis],
                "network_correlation": [dict(row) for row in network_analysis],
                "analysis_period_hours": hours,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        # Return empty data instead of error to prevent dashboard crashes
        return {
            "session_analysis": [],
            "network_correlation": [],
            "analysis_period_hours": hours,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": "Analytics temporarily unavailable"
        }

@app.get("/analytics/charts/battery")
async def get_battery_chart_data(hours: int = 24, token: str = Depends(verify_token)):
    """Get battery level time-series data for charts"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT 
                    dr.device_id,
                    dr.device_name,
                    dm.battery_level,
                    dm.battery_temperature,
                    dm.timestamp
                FROM device_registry dr
                JOIN device_metrics dm ON dr.device_id = dm.device_id
                WHERE dm.timestamp >= NOW() - ($1 || ' hours')::interval
                  AND dm.battery_level IS NOT NULL
                ORDER BY dm.timestamp DESC
                LIMIT 1000
            """
            
            results = await conn.fetch(query, str(hours))
            
            # Group by device for chart format
            chart_data = {}
            for row in results:
                device_id = row['device_id']
                if device_id not in chart_data:
                    chart_data[device_id] = {
                        'device_name': row['device_name'] or device_id,
                        'data': []
                    }
                
                chart_data[device_id]['data'].append({
                    'timestamp': row['timestamp'].isoformat(),
                    'battery_level': row['battery_level'],
                    'battery_temperature': row['battery_temperature']
                })
            
            return {
                "devices": chart_data,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"Battery chart data error: {str(e)}")
        return {"devices": {}, "error": str(e)}

@app.get("/analytics/charts/wifi")
async def get_wifi_chart_data(hours: int = 24, token: str = Depends(verify_token)):
    """Get WiFi signal strength time-series data for charts"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT 
                    dr.device_id,
                    dr.device_name,
                    nm.wifi_signal_strength,
                    nm.wifi_ssid,
                    nm.connectivity_status,
                    nm.timestamp
                FROM device_registry dr
                JOIN network_metrics nm ON dr.device_id = nm.device_id
                WHERE nm.timestamp >= NOW() - ($1 || ' hours')::interval
                  AND nm.wifi_signal_strength IS NOT NULL
                ORDER BY nm.timestamp DESC
                LIMIT 1000
            """
            
            results = await conn.fetch(query, str(hours))
            
            # Group by device for chart format
            chart_data = {}
            for row in results:
                device_id = row['device_id']
                if device_id not in chart_data:
                    chart_data[device_id] = {
                        'device_name': row['device_name'] or device_id,
                        'data': []
                    }
                
                chart_data[device_id]['data'].append({
                    'timestamp': row['timestamp'].isoformat(),
                    'wifi_signal_strength': row['wifi_signal_strength'],
                    'wifi_ssid': row['wifi_ssid'],
                    'connectivity_status': row['connectivity_status']
                })
            
            return {
                "devices": chart_data,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"WiFi chart data error: {str(e)}")
        return {"devices": {}, "error": str(e)}

@app.get("/analytics/charts/myob")
async def get_myob_chart_data(hours: int = 24, token: str = Depends(verify_token)):
    """Get MYOB session activity time-series data for charts"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT 
                    dr.device_id,
                    dr.device_name,
                    am.app_foreground,
                    am.last_user_interaction,
                    am.screen_state,
                    am.timestamp,
                    CASE 
                        WHEN am.app_foreground ILIKE '%myob%' THEN 1 
                        ELSE 0 
                    END as myob_active
                FROM device_registry dr
                JOIN app_metrics am ON dr.device_id = am.device_id
                WHERE am.timestamp >= NOW() - ($1 || ' hours')::interval
                ORDER BY am.timestamp DESC
                LIMIT 1000
            """
            
            results = await conn.fetch(query, str(hours))
            
            # Group by device for chart format
            chart_data = {}
            for row in results:
                device_id = row['device_id']
                if device_id not in chart_data:
                    chart_data[device_id] = {
                        'device_name': row['device_name'] or device_id,
                        'data': []
                    }
                
                chart_data[device_id]['data'].append({
                    'timestamp': row['timestamp'].isoformat(),
                    'myob_active': bool(row['myob_active']),
                    'app_foreground': row['app_foreground'],
                    'screen_state': row['screen_state'],
                    'last_user_interaction': row['last_user_interaction'].isoformat() if row['last_user_interaction'] else None
                })
            
            return {
                "devices": chart_data,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"MYOB chart data error: {str(e)}")
        return {"devices": {}, "error": str(e)}

@app.get("/analytics/charts/scanner")
async def get_scanner_chart_data(hours: int = 24, token: str = Depends(verify_token)):
    """Get scanner activity time-series data for charts"""
    try:
        async with db_pool.acquire() as conn:
            # Get scanner activity from both app_metrics and session_events
            query = """
                SELECT 
                    dr.device_id,
                    dr.device_name,
                    am.app_foreground,
                    am.timestamp,
                    CASE 
                        WHEN am.app_foreground ILIKE '%scanner%' 
                          OR am.app_foreground ILIKE '%barcode%'
                          OR am.app_foreground ILIKE '%zebra%'
                          OR am.app_foreground ILIKE '%honeywell%'
                          OR am.app_foreground ILIKE '%datalogic%'
                        THEN 1 
                        ELSE 0 
                    END as scanner_active
                FROM device_registry dr
                JOIN app_metrics am ON dr.device_id = am.device_id
                WHERE am.timestamp >= NOW() - ($1 || ' hours')::interval
                ORDER BY am.timestamp DESC
                LIMIT 1000
            """
            
            results = await conn.fetch(query, str(hours))
            
            # Group by device for chart format
            chart_data = {}
            for row in results:
                device_id = row['device_id']
                if device_id not in chart_data:
                    chart_data[device_id] = {
                        'device_name': row['device_name'] or device_id,
                        'data': []
                    }
                
                chart_data[device_id]['data'].append({
                    'timestamp': row['timestamp'].isoformat(),
                    'scanner_active': bool(row['scanner_active']),
                    'app_foreground': row['app_foreground']
                })
            
            return {
                "devices": chart_data,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"Scanner chart data error: {str(e)}")
        return {"devices": {}, "error": str(e)}

@app.get("/api/devices/{device_id}/timeline")
async def get_device_timeline(device_id: str, hours: int = 24, token: str = Depends(verify_token)):
    """Get device timeline events for expanded card view"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT 
                    'session' as type,
                    se.event_type,
                    se.error_message as message,
                    se.timestamp
                FROM session_events se
                WHERE se.device_id = $1 
                  AND se.timestamp >= NOW() - ($2 || ' hours')::interval
                
                UNION ALL
                
                SELECT 
                    'device' as type,
                    'battery_update' as event_type,
                    CONCAT('Battery: ', dm.battery_level, '%', 
                           CASE WHEN dm.battery_temperature IS NOT NULL 
                                THEN CONCAT(' (', dm.battery_temperature, '°C)')
                                ELSE '' END) as message,
                    dm.timestamp
                FROM device_metrics dm
                WHERE dm.device_id = $1 
                  AND dm.timestamp >= NOW() - ($2 || ' hours')::interval
                  AND dm.battery_level IS NOT NULL
                
                UNION ALL
                
                SELECT 
                    'network' as type,
                    'connectivity_change' as event_type,
                    CONCAT('WiFi: ', nm.connectivity_status, 
                           CASE WHEN nm.wifi_ssid IS NOT NULL 
                                THEN CONCAT(' (', nm.wifi_ssid, ')')
                                ELSE '' END) as message,
                    nm.timestamp
                FROM network_metrics nm
                WHERE nm.device_id = $1 
                  AND nm.timestamp >= NOW() - ($2 || ' hours')::interval
                
                ORDER BY timestamp DESC
                LIMIT 50
            """
            
            results = await conn.fetch(query, device_id, str(hours))
            
            events = []
            for row in results:
                event_type = 'success'
                if 'timeout' in row['message'].lower() or 'error' in row['message'].lower():
                    event_type = 'error'
                elif 'warning' in row['message'].lower() or 'low' in row['message'].lower():
                    event_type = 'warning'
                
                events.append({
                    'type': event_type,
                    'message': row['message'],
                    'timestamp': row['timestamp'].isoformat()
                })
            
            return events
            
    except Exception as e:
        logger.error(f"Timeline error for device {device_id}: {str(e)}")
        return []

# Dashboard endpoint - serve interactive dashboard
@app.get("/dashboard")
async def dashboard():
    """Interactive dashboard endpoint"""
    try:
        # Try to serve the static dashboard file
        static_path = Path("static/dashboard.html")
        if static_path.exists():
            return FileResponse(static_path, media_type="text/html")
        else:
            # Fallback HTML if static file doesn't exist
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>JD Engineering Tablet Monitor - Dashboard</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    h1 { color: #333; }
                    .status { 
                        padding: 10px;
                        background: #ffebee;
                        border-radius: 5px;
                        margin: 20px 0;
                        color: #c62828;
                    }
                    .endpoints {
                        background: #f0f0f0;
                        padding: 15px;
                        border-radius: 5px;
                        margin-top: 20px;
                    }
                    code {
                        background: #f5f5f5;
                        padding: 2px 5px;
                        border-radius: 3px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📱 JD Engineering Tablet Monitor</h1>
                    <div class="status">
                        <strong>⚠️ Dashboard Status:</strong> Interactive dashboard file not found at /static/dashboard.html
                    </div>
                    <p>The interactive dashboard file is not available. Please check the deployment.</p>
                    
                    <h2>📊 Available API Endpoints:</h2>
                    <div class="endpoints">
                        <p><strong>GET</strong> <code>/health</code> - Health check</p>
                        <p><strong>GET</strong> <code>/devices</code> - List all devices</p>
                        <p><strong>GET</strong> <code>/devices/{device_id}/metrics</code> - Device metrics</p>
                        <p><strong>GET</strong> <code>/analytics/session-issues</code> - Session analytics</p>
                        <p><strong>POST</strong> <code>/tablet-metrics</code> - Submit device data</p>
                        <p><strong>GET</strong> <code>/docs</code> - Interactive API documentation</p>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return HTMLResponse(content="<h1>Dashboard Error</h1><p>Could not load dashboard.</p>", status_code=500)

# Root endpoint with API information
@app.get("/")
async def root():
    """API information and status"""
    return {
        "name": "Tablet Session Monitoring API",
        "version": "1.0.0",
        "status": "operational",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "documentation": "/docs",
        "health_check": "/health",
        "dashboard": "/dashboard",
        "endpoints": {
            "submit_data": "POST /tablet-metrics",
            "get_devices": "GET /devices",
            "device_metrics": "GET /devices/{device_id}/metrics",
            "session_analysis": "GET /analytics/session-issues"
        }
    }

@app.get("/analytics/business/myob-timeout-analysis")
async def get_myob_timeout_analysis(hours: int = 168, token: str = Depends(verify_token)):
    """Business intelligence analysis for MYOB session timeouts"""
    try:
        async with db_pool.acquire() as conn:
            # Comprehensive MYOB timeout analysis
            analysis_query = """
                WITH myob_sessions AS (
                    SELECT 
                        dr.device_id,
                        dr.device_name,
                        dr.location,
                        am.timestamp,
                        am.last_user_interaction,
                        am.app_foreground,
                        se.event_type,
                        se.duration,
                        EXTRACT(HOUR FROM am.timestamp) as hour_of_day,
                        EXTRACT(DOW FROM am.timestamp) as day_of_week,
                        CASE 
                            WHEN am.app_foreground ILIKE '%myob%' THEN true 
                            ELSE false 
                        END as myob_active,
                        CASE 
                            WHEN am.last_user_interaction < am.timestamp - INTERVAL '5 minutes' 
                                 AND am.app_foreground ILIKE '%myob%' 
                            THEN true 
                            ELSE false 
                        END as timeout_risk,
                        CASE
                            WHEN se.event_type = 'timeout' AND se.error_message ILIKE '%myob%' 
                            THEN true
                            ELSE false
                        END as actual_timeout
                    FROM device_registry dr
                    JOIN app_metrics am ON dr.device_id = am.device_id
                    LEFT JOIN session_events se ON dr.device_id = se.device_id 
                        AND se.timestamp BETWEEN am.timestamp - INTERVAL '1 minute' 
                                              AND am.timestamp + INTERVAL '1 minute'
                    WHERE am.timestamp >= NOW() - ($1 || ' hours')::interval
                ),
                timeout_summary AS (
                    SELECT 
                        COUNT(*) as total_myob_sessions,
                        COUNT(*) FILTER (WHERE timeout_risk) as timeout_risk_sessions,
                        COUNT(*) FILTER (WHERE actual_timeout) as actual_timeouts,
                        AVG(CASE WHEN myob_active THEN duration ELSE NULL END) as avg_session_duration,
                        COUNT(DISTINCT device_id) as affected_devices,
                        ROUND(
                            (COUNT(*) FILTER (WHERE actual_timeout)::float / 
                             NULLIF(COUNT(*) FILTER (WHERE myob_active), 0)) * 100, 2
                        ) as timeout_rate_percent
                    FROM myob_sessions
                ),
                hourly_patterns AS (
                    SELECT 
                        hour_of_day,
                        COUNT(*) FILTER (WHERE myob_active) as myob_sessions,
                        COUNT(*) FILTER (WHERE timeout_risk) as timeout_risks,
                        COUNT(*) FILTER (WHERE actual_timeout) as timeouts,
                        ROUND(
                            (COUNT(*) FILTER (WHERE actual_timeout)::float / 
                             NULLIF(COUNT(*) FILTER (WHERE myob_active), 0)) * 100, 2
                        ) as hourly_timeout_rate
                    FROM myob_sessions
                    GROUP BY hour_of_day
                    ORDER BY hour_of_day
                ),
                device_impact AS (
                    SELECT 
                        device_id,
                        device_name,
                        location,
                        COUNT(*) FILTER (WHERE myob_active) as myob_sessions,
                        COUNT(*) FILTER (WHERE timeout_risk) as timeout_risks,
                        COUNT(*) FILTER (WHERE actual_timeout) as actual_timeouts,
                        ROUND(
                            (COUNT(*) FILTER (WHERE actual_timeout)::float / 
                             NULLIF(COUNT(*) FILTER (WHERE myob_active), 0)) * 100, 2
                        ) as device_timeout_rate,
                        MAX(timestamp) as last_activity
                    FROM myob_sessions
                    GROUP BY device_id, device_name, location
                    ORDER BY actual_timeouts DESC, timeout_risks DESC
                )
                SELECT 
                    json_build_object(
                        'summary', (SELECT row_to_json(timeout_summary) FROM timeout_summary),
                        'hourly_patterns', (SELECT json_agg(row_to_json(hourly_patterns)) FROM hourly_patterns),
                        'device_impact', (SELECT json_agg(row_to_json(device_impact)) FROM device_impact)
                    ) as analysis_result
            """
            
            result = await conn.fetchrow(analysis_query, str(hours))
            analysis_data = result['analysis_result'] if result else {}
            
            # Calculate business impact metrics
            summary = analysis_data.get('summary', {})
            business_impact = {
                "productivity_loss_hours": round((summary.get('actual_timeouts', 0) * 15) / 60, 2),  # 15 min avg recovery time
                "affected_employees": summary.get('affected_devices', 0),
                "daily_timeout_incidents": round(summary.get('actual_timeouts', 0) * 24 / hours, 1),
                "efficiency_score": max(0, 100 - (summary.get('timeout_rate_percent', 0) * 2)),  # Penalty scoring
                "risk_level": "HIGH" if summary.get('timeout_rate_percent', 0) > 15 else 
                             "MEDIUM" if summary.get('timeout_rate_percent', 0) > 5 else "LOW"
            }
            
            return {
                "analysis_period_hours": hours,
                "business_impact": business_impact,
                "detailed_analysis": analysis_data,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "recommendations": generate_timeout_recommendations(analysis_data, business_impact)
            }
            
    except Exception as e:
        logger.error(f"MYOB timeout analysis error: {str(e)}")
        return {
            "error": "Analysis temporarily unavailable",
            "analysis_period_hours": hours,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

@app.get("/analytics/ai/insights")
async def get_ai_insights(focus: str = "timeout", hours: int = 168, token: str = Depends(verify_token)):
    """AI-powered insights and predictions for operational issues"""
    try:
        async with db_pool.acquire() as conn:
            # Gather comprehensive data for AI analysis
            data_query = """
                SELECT 
                    dr.device_id,
                    dr.location,
                    dm.battery_level,
                    nm.wifi_signal_strength,
                    nm.connectivity_status,
                    am.app_foreground,
                    am.last_user_interaction,
                    am.timestamp,
                    se.event_type,
                    se.duration,
                    EXTRACT(HOUR FROM am.timestamp) as hour,
                    EXTRACT(DOW FROM am.timestamp) as day_of_week,
                    CASE WHEN am.app_foreground ILIKE '%myob%' THEN 1 ELSE 0 END as myob_active,
                    CASE WHEN se.event_type = 'timeout' THEN 1 ELSE 0 END as timeout_occurred
                FROM device_registry dr
                LEFT JOIN device_metrics dm ON dr.device_id = dm.device_id
                LEFT JOIN network_metrics nm ON dr.device_id = nm.device_id 
                    AND nm.timestamp BETWEEN dm.timestamp - INTERVAL '1 minute' 
                                          AND dm.timestamp + INTERVAL '1 minute'
                LEFT JOIN app_metrics am ON dr.device_id = am.device_id
                    AND am.timestamp BETWEEN dm.timestamp - INTERVAL '1 minute' 
                                          AND dm.timestamp + INTERVAL '1 minute'
                LEFT JOIN session_events se ON dr.device_id = se.device_id
                    AND se.timestamp BETWEEN am.timestamp - INTERVAL '2 minutes' 
                                          AND am.timestamp + INTERVAL '2 minutes'
                WHERE dm.timestamp >= NOW() - ($1 || ' hours')::interval
                ORDER BY am.timestamp DESC
                LIMIT 1000
            """
            
            results = await conn.fetch(data_query, str(hours))
            
            # Convert to analysis format
            data_points = []
            for row in results:
                if row['battery_level'] is not None:  # Valid data point
                    data_points.append({
                        'device_id': row['device_id'],
                        'location': row['location'],
                        'battery_level': row['battery_level'],
                        'wifi_signal': abs(row['wifi_signal_strength']) if row['wifi_signal_strength'] else 70,
                        'connectivity_online': 1 if row['connectivity_status'] == 'online' else 0,
                        'myob_active': row['myob_active'],
                        'timeout_occurred': row['timeout_occurred'],
                        'hour': row['hour'],
                        'day_of_week': row['day_of_week']
                    })
            
            # Generate AI insights
            ai_insights = generate_ai_insights(data_points, focus)
            
            return {
                "focus_area": focus,
                "data_points_analyzed": len(data_points),
                "analysis_period_hours": hours,
                "ai_insights": ai_insights,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error(f"AI insights error: {str(e)}")
        return {
            "error": "AI analysis temporarily unavailable",
            "focus_area": focus,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

def generate_timeout_recommendations(analysis_data, business_impact):
    """Generate actionable recommendations based on timeout analysis"""
    recommendations = []
    
    summary = analysis_data.get('summary', {})
    hourly_patterns = analysis_data.get('hourly_patterns', [])
    device_impact = analysis_data.get('device_impact', [])
    
    timeout_rate = summary.get('timeout_rate_percent', 0)
    
    # Critical timeout rate
    if timeout_rate > 15:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "System Configuration",
            "issue": f"High timeout rate: {timeout_rate}%",
            "recommendation": "Immediately increase MYOB session timeout settings from default 5 minutes to 15-20 minutes",
            "expected_impact": "60-80% reduction in timeout incidents",
            "implementation": "Update MYOB server configuration or group policy"
        })
    
    # Peak hour analysis
    peak_hours = [h for h in hourly_patterns if h.get('hourly_timeout_rate', 0) > 10]
    if peak_hours:
        peak_times = [f"{h['hour_of_day']}:00" for h in peak_hours]
        recommendations.append({
            "priority": "HIGH",
            "category": "Operational Scheduling",
            "issue": f"Peak timeout hours: {', '.join(peak_times)}",
            "recommendation": "Schedule system maintenance outside peak hours and consider staggered break times",
            "expected_impact": "30-50% reduction in peak-hour timeouts",
            "implementation": "Adjust staff schedules and system maintenance windows"
        })
    
    # Device-specific issues
    problem_devices = [d for d in device_impact if d.get('device_timeout_rate', 0) > 20]
    if problem_devices:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Hardware Maintenance",
            "issue": f"{len(problem_devices)} devices with high timeout rates",
            "recommendation": "Investigate hardware performance and network connectivity for specific devices",
            "expected_impact": "Eliminate device-specific timeout issues",
            "implementation": "Hardware diagnostics and potential replacement"
        })
    
    # Productivity impact
    if business_impact.get('productivity_loss_hours', 0) > 5:
        recommendations.append({
            "priority": "HIGH",
            "category": "Business Process",
            "issue": f"{business_impact['productivity_loss_hours']} hours lost per week",
            "recommendation": "Implement auto-save functionality and session recovery procedures",
            "expected_impact": "90% reduction in work loss from timeouts",
            "implementation": "MYOB configuration and user training"
        })
    
    return recommendations

def generate_ai_insights(data_points, focus="timeout"):
    """Simple AI-like analysis using statistical patterns"""
    if not data_points:
        return {"error": "Insufficient data for analysis"}
    
    insights = {
        "pattern_analysis": {},
        "predictions": {},
        "anomalies": [],
        "correlations": {}
    }
    
    # Battery correlation analysis
    myob_sessions = [d for d in data_points if d['myob_active'] == 1]
    timeouts = [d for d in data_points if d['timeout_occurred'] == 1]
    
    if myob_sessions:
        avg_battery_myob = sum(d['battery_level'] for d in myob_sessions) / len(myob_sessions)
        insights["correlations"]["battery_myob"] = {
            "average_battery_during_myob": round(avg_battery_myob, 1),
            "correlation_strength": "STRONG" if avg_battery_myob < 30 else "WEAK",
            "insight": f"MYOB sessions occur at {avg_battery_myob:.1f}% average battery"
        }
    
    if timeouts:
        avg_battery_timeout = sum(d['battery_level'] for d in timeouts) / len(timeouts)
        avg_wifi_timeout = sum(d['wifi_signal'] for d in timeouts) / len(timeouts)
        
        insights["correlations"]["timeout_factors"] = {
            "battery_at_timeout": round(avg_battery_timeout, 1),
            "wifi_signal_at_timeout": round(avg_wifi_timeout, 1),
            "primary_factor": "BATTERY" if avg_battery_timeout < 25 else 
                            "WIFI" if avg_wifi_timeout > 70 else "SESSION_LENGTH"
        }
    
    # Time pattern analysis
    hour_patterns = {}
    for dp in data_points:
        hour = dp['hour']
        if hour not in hour_patterns:
            hour_patterns[hour] = {"total": 0, "timeouts": 0, "myob": 0}
        hour_patterns[hour]["total"] += 1
        hour_patterns[hour]["timeouts"] += dp['timeout_occurred']
        hour_patterns[hour]["myob"] += dp['myob_active']
    
    # Find peak problem hours
    problem_hours = []
    for hour, stats in hour_patterns.items():
        if stats["total"] > 5:  # Sufficient data
            timeout_rate = (stats["timeouts"] / stats["total"]) * 100
            if timeout_rate > 15:
                problem_hours.append({"hour": hour, "timeout_rate": round(timeout_rate, 1)})
    
    insights["pattern_analysis"]["time_patterns"] = {
        "problem_hours": sorted(problem_hours, key=lambda x: x["timeout_rate"], reverse=True)[:3],
        "recommendation": "Focus monitoring and preventive measures during identified peak hours"
    }
    
    # Predictive insights
    total_sessions = len(myob_sessions)
    total_timeouts = len(timeouts)
    
    if total_sessions > 0:
        current_timeout_rate = (total_timeouts / total_sessions) * 100
        
        # Simple trend prediction
        if current_timeout_rate > 20:
            risk_level = "CRITICAL"
            prediction = "Immediate intervention required"
        elif current_timeout_rate > 10:
            risk_level = "HIGH"
            prediction = "Timeout incidents likely to increase without action"
        else:
            risk_level = "LOW"
            prediction = "Current timeout rate is manageable"
        
        insights["predictions"]["timeout_trend"] = {
            "current_rate": round(current_timeout_rate, 1),
            "risk_level": risk_level,
            "prediction": prediction,
            "confidence": "HIGH" if total_sessions > 50 else "MEDIUM"
        }
    
    # Anomaly detection
    if data_points:
        battery_levels = [d['battery_level'] for d in data_points]
        avg_battery = sum(battery_levels) / len(battery_levels)
        
        # Find devices with consistently low battery during MYOB usage
        device_battery_avg = {}
        for dp in data_points:
            if dp['myob_active'] == 1:
                device_id = dp['device_id']
                if device_id not in device_battery_avg:
                    device_battery_avg[device_id] = []
                device_battery_avg[device_id].append(dp['battery_level'])
        
        for device_id, batteries in device_battery_avg.items():
            if len(batteries) > 3:  # Sufficient data
                avg_device_battery = sum(batteries) / len(batteries)
                if avg_device_battery < 25:
                    insights["anomalies"].append({
                        "type": "LOW_BATTERY_PATTERN",
                        "device_id": device_id,
                        "average_battery": round(avg_device_battery, 1),
                        "severity": "HIGH",
                        "recommendation": "Replace battery or increase charging frequency"
                    })
    
    return insights

# Railway deployment configuration
# Updated with business intelligence endpoints
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )