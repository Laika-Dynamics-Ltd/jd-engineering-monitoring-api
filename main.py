# main.py - Railway.app optimized FastAPI application
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, RedirectResponse, Response
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
import httpx

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
    
    # Close Streamlit proxy client
    if streamlit_client:
        await streamlit_client.aclose()
        logger.info("Streamlit proxy client closed")

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
    """Get list of all monitored devices with summary statistics"""
    async with db_pool.acquire() as conn:
        devices = await conn.fetch('''
            SELECT dr.*,
                   EXTRACT(EPOCH FROM (NOW() - dr.last_seen))::INTEGER as seconds_since_last_seen,
                   CASE 
                       WHEN dr.last_seen > NOW() - INTERVAL '5 minutes' THEN 'online'
                       WHEN dr.last_seen > NOW() - INTERVAL '1 hour' THEN 'recent'
                       ELSE 'offline'
                   END as status
            FROM device_registry dr
            ORDER BY dr.last_seen DESC
        ''')
        return [dict(device) for device in devices]

@app.get("/devices/{device_id}/metrics")
async def get_device_metrics(
    device_id: str,
    hours: int = 24,
    token: str = Depends(verify_token)
):
    """Get comprehensive metrics for a specific device"""
    async with db_pool.acquire() as conn:
        # Get recent metrics with time range
        interval_str = f"{hours} hours"
        
        device_data = await conn.fetch('''
            SELECT * FROM device_metrics 
            WHERE device_id = $1 AND timestamp > NOW() - INTERVAL $2
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', device_id, interval_str)
        
        network_data = await conn.fetch('''
            SELECT * FROM network_metrics 
            WHERE device_id = $1 AND timestamp > NOW() - INTERVAL $2
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', device_id, interval_str)
        
        app_data = await conn.fetch('''
            SELECT * FROM app_metrics 
            WHERE device_id = $1 AND timestamp > NOW() - INTERVAL $2
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', device_id, interval_str)
        
        session_data = await conn.fetch('''
            SELECT * FROM session_events 
            WHERE device_id = $1 AND timestamp > NOW() - INTERVAL $2
            ORDER BY timestamp DESC
            LIMIT 500
        ''', device_id, interval_str)
        
        return {
            "device_id": device_id,
            "time_range_hours": hours,
            "device_metrics": [dict(row) for row in device_data],
            "network_metrics": [dict(row) for row in network_data],
            "app_metrics": [dict(row) for row in app_data],
            "session_events": [dict(row) for row in session_data],
            "summary": {
                "total_device_records": len(device_data),
                "total_network_records": len(network_data),
                "total_app_records": len(app_data),
                "total_session_events": len(session_data)
            }
        }

@app.get("/analytics/session-issues")
async def get_session_issues(
    device_id: Optional[str] = None,
    hours: int = 24,
    token: str = Depends(verify_token)
):
    """Advanced session timeout and connectivity analysis"""
    async with db_pool.acquire() as conn:
        interval_str = f"{hours} hours"
        params = [interval_str]
        where_clause = "WHERE se.timestamp > NOW() - INTERVAL $1"
        if device_id:
            where_clause += " AND se.device_id = $2"
            params.append(device_id)
            
        # Comprehensive session analysis
        analysis = await conn.fetch(f'''
            SELECT 
                se.device_id,
                dr.device_name,
                dr.location,
                COUNT(*) FILTER (WHERE se.event_type = 'timeout') as timeout_count,
                COUNT(*) FILTER (WHERE se.event_type IN ('login', 'session_start')) as login_count,
                COUNT(*) FILTER (WHERE se.event_type IN ('logout', 'session_end')) as logout_count,
                COUNT(*) FILTER (WHERE se.event_type = 'error') as error_count,
                AVG(se.duration) FILTER (WHERE se.duration IS NOT NULL) as avg_session_duration,
                MAX(se.timestamp) as last_activity,
                COUNT(DISTINCT DATE(se.timestamp)) as active_days
            FROM session_events se
            JOIN device_registry dr ON se.device_id = dr.device_id
            {where_clause}
            GROUP BY se.device_id, dr.device_name, dr.location
            ORDER BY timeout_count DESC, login_count DESC
        ''', *params)
        
        # Network correlation analysis
        network_where = where_clause.replace('se.', 'nm.')
        network_analysis = await conn.fetch(f'''
            SELECT 
                nm.device_id,
                COUNT(*) FILTER (WHERE nm.connectivity_status = 'offline') as offline_count,
                COUNT(*) FILTER (WHERE nm.connectivity_status = 'limited') as limited_count,
                AVG(nm.wifi_signal_strength) as avg_signal_strength,
                AVG(nm.dns_response_time) as avg_dns_time
            FROM network_metrics nm
            {network_where}
            GROUP BY nm.device_id
        ''', *params)
        
        return {
            "session_analysis": [dict(row) for row in analysis],
            "network_correlation": [dict(row) for row in network_analysis],
            "analysis_period_hours": hours,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# Proxy client for Streamlit
streamlit_client = None

def get_streamlit_client():
    global streamlit_client
    if streamlit_client is None:
        streamlit_url = os.getenv("STREAMLIT_INTERNAL_URL", "http://localhost:8501")
        streamlit_client = httpx.AsyncClient(base_url=streamlit_url, timeout=30.0)
    return streamlit_client

# Dashboard proxy endpoints
@app.get("/dashboard")
@app.post("/dashboard")
async def dashboard_root():
    """Redirect to dashboard with trailing slash"""
    return RedirectResponse(url="/dashboard/", status_code=307)

@app.api_route("/dashboard/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def dashboard_proxy(request: Request, path: str = ""):
    """Proxy all requests to Streamlit dashboard"""
    client = get_streamlit_client()
    
    # Build the target URL
    target_path = f"/dashboard/{path}" if path else "/dashboard/"
    
    try:
        # Forward the request to Streamlit
        response = await client.request(
            method=request.method,
            url=target_path,
            headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'connection']},
            content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
            params=dict(request.query_params)
        )
        
        # Return the response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() not in ['connection', 'transfer-encoding']},
            media_type=response.headers.get("content-type", "text/html")
        )
    except Exception as e:
        logger.error(f"Dashboard proxy error: {str(e)}")
        if os.getenv("RAILWAY_ENVIRONMENT"):
            return JSONResponse(
                status_code=503,
                content={"error": "Dashboard temporarily unavailable", "detail": str(e)}
            )
        else:
            # In development, redirect to Streamlit directly
            return RedirectResponse(url=f"http://localhost:8501/dashboard/{path}", status_code=307)

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

# Railway deployment configuration
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )