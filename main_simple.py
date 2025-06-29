# Simple FastAPI for immediate tablet testing
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple FastAPI app
app = FastAPI(
    title="Tablet Session Monitoring API - Simple",
    description="Emergency version for tablet testing",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# In-memory storage for emergency use
tablet_data_store = []

# Models (simplified)
class DeviceMetrics(BaseModel):
    battery_level: Optional[int] = 50
    battery_temperature: Optional[float] = 25.0
    battery_status: Optional[str] = "unknown"

class NetworkMetrics(BaseModel):
    wifi_signal_strength: Optional[int] = -50
    wifi_ssid: Optional[str] = "unknown"
    connectivity_status: str = "unknown"

class AppMetrics(BaseModel):
    screen_state: str = "active"
    app_foreground: Optional[str] = "unknown"
    last_user_interaction: Optional[datetime] = None

class TabletData(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    location: Optional[str] = None
    device_metrics: Optional[DeviceMetrics] = None
    network_metrics: Optional[NetworkMetrics] = None
    app_metrics: Optional[AppMetrics] = None
    session_events: Optional[List[Dict]] = []
    raw_logs: Optional[List[str]] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    expected_token = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return credentials.credentials

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0-simple",
        "service": "operational"
    }

@app.post("/tablet-metrics")
async def receive_tablet_data(data: TabletData, token: str = Depends(verify_token)):
    """Receive tablet data - simplified version"""
    try:
        # Store in memory (emergency solution)
        data_dict = data.dict()
        data_dict["received_at"] = datetime.now(timezone.utc).isoformat()
        tablet_data_store.append(data_dict)
        
        # Keep only last 1000 entries
        if len(tablet_data_store) > 1000:
            tablet_data_store.pop(0)
        
        logger.info(f"📱 Tablet data received: {data.device_id}")
        
        return {
            "status": "success",
            "message": "Data received successfully",
            "device_id": data.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error storing tablet data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

@app.get("/devices")
async def get_devices(token: str = Depends(verify_token)):
    """Get device list"""
    devices = {}
    for entry in tablet_data_store[-100:]:  # Last 100 entries
        device_id = entry.get("device_id")
        if device_id:
            devices[device_id] = {
                "device_id": device_id,
                "device_name": entry.get("device_name", device_id),
                "location": entry.get("location", "Unknown"),
                "last_seen": entry.get("received_at"),
                "status": "active"
            }
    
    return list(devices.values())

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JD Engineering Tablet Monitoring API - Emergency Simple Version",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 