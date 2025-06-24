#!/usr/bin/env python3
"""
Production Configuration for J&D McLennan Engineering Dashboard
Enterprise-grade database connections, caching, and error handling
"""

import os
import asyncio
import asyncpg
import redis.asyncio as redis
from typing import Optional, Dict, Any
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionConfig:
    """Enterprise-grade configuration management"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Database Configuration
        self.database_url = os.getenv("DATABASE_URL")
        self.db_pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.db_max_connections = int(os.getenv("DB_MAX_CONNECTIONS", "100"))
        self.db_timeout = int(os.getenv("DB_TIMEOUT", "30"))
        
        # Redis Configuration  
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
        
        # Security Configuration
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
        
        # API Configuration
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))  # requests per minute
        self.api_timeout = int(os.getenv("API_TIMEOUT", "30"))
        
        # Monitoring Configuration
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"

class DatabaseManager:
    """Production-grade database connection management with resilience"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False
        self.connection_attempts = 0
        self.max_retries = 5
        
    async def initialize(self):
        """Initialize database connection pool with retry logic"""
        if not self.config.database_url:
            logger.warning("No DATABASE_URL configured - running in mock mode")
            self.is_connected = False
            return
            
        for attempt in range(self.max_retries):
            try:
                self.pool = await asyncpg.create_pool(
                    self.config.database_url,
                    min_size=5,
                    max_size=self.config.db_pool_size,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300,
                    timeout=self.config.db_timeout,
                    command_timeout=60
                )
                
                # Test connection
                async with self.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                
                self.is_connected = True
                logger.info(f"✅ Database connected successfully (attempt {attempt + 1})")
                break
                
            except Exception as e:
                self.connection_attempts = attempt + 1
                logger.error(f"❌ Database connection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = min(2 ** attempt, 30)  # Exponential backoff
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("🚨 All database connection attempts failed - running in fallback mode")
                    self.is_connected = False
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with automatic fallback"""
        if not self.is_connected or not self.pool:
            # Return a mock connection for fallback mode
            yield MockConnection()
            return
            
        try:
            async with self.pool.acquire() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            yield MockConnection()
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        if not self.pool:
            return {
                "status": "disconnected",
                "is_connected": False,
                "pool_size": 0,
                "connection_attempts": self.connection_attempts
            }
        
        try:
            async with self.pool.acquire() as conn:
                # Test query performance
                start_time = datetime.now()
                await conn.fetchval("SELECT 1")
                query_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "status": "healthy",
                    "is_connected": True,
                    "pool_size": self.pool.get_size(),
                    "pool_max_size": self.config.db_pool_size,
                    "query_response_time": f"{query_time:.3f}s",
                    "connection_attempts": self.connection_attempts
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "is_connected": False,
                "error": str(e),
                "connection_attempts": self.connection_attempts
            }
    
    async def close(self):
        """Gracefully close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")

class MockConnection:
    """Mock database connection for fallback mode"""
    
    async def fetch(self, query: str, *args):
        """Return mock data for common queries"""
        logger.warning(f"Mock query executed: {query}")
        
        if "device_registry" in query:
            return [
                {"device_id": "tablet-001", "device_name": "Production Tablet 1", "location": "Warehouse A", "is_active": True},
                {"device_id": "tablet-002", "device_name": "Production Tablet 2", "location": "Warehouse B", "is_active": True},
                {"device_id": "tablet-003", "device_name": "Production Tablet 3", "location": "Office", "is_active": True}
            ]
        
        if "device_metrics" in query:
            return [
                {"device_id": "tablet-001", "battery_level": 85, "timestamp": datetime.now(timezone.utc)},
                {"device_id": "tablet-002", "battery_level": 72, "timestamp": datetime.now(timezone.utc)},
                {"device_id": "tablet-003", "battery_level": 91, "timestamp": datetime.now(timezone.utc)}
            ]
        
        return []
    
    async def fetchval(self, query: str, *args):
        """Return mock single values"""
        if "COUNT" in query:
            return 3
        if "SELECT 1" in query:
            return 1
        return None
    
    async def execute(self, query: str, *args):
        """Mock execute for INSERT/UPDATE queries"""
        logger.warning(f"Mock execute: {query}")
        return "MOCK"

class CacheManager:
    """Production-grade Redis caching with fallback"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.redis: Optional[redis.Redis] = None
        self.is_connected = False
        
    async def initialize(self):
        """Initialize Redis connection with fallback"""
        try:
            self.redis = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=10,
                socket_connect_timeout=10,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis.ping()
            self.is_connected = True
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e} - using memory cache fallback")
            self.is_connected = False
            self._memory_cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value with fallback"""
        if self.is_connected and self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to memory cache
        return self._memory_cache.get(key) if hasattr(self, '_memory_cache') else None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with fallback"""
        ttl = ttl or self.config.cache_ttl
        
        if self.is_connected and self.redis:
            try:
                await self.redis.setex(key, ttl, json.dumps(value, default=str))
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback to memory cache
        if hasattr(self, '_memory_cache'):
            self._memory_cache[key] = value
            return True
        return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        if self.is_connected and self.redis:
            try:
                await self.redis.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if hasattr(self, '_memory_cache'):
            self._memory_cache.pop(key, None)
            return True
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Redis health check"""
        if not self.is_connected:
            return {"status": "disconnected", "cache_type": "memory_fallback"}
        
        try:
            start_time = datetime.now()
            await self.redis.ping()
            ping_time = (datetime.now() - start_time).total_seconds()
            
            info = await self.redis.info()
            return {
                "status": "healthy",
                "cache_type": "redis",
                "ping_time": f"{ping_time:.3f}s",
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

class ErrorHandler:
    """Centralized error handling for production"""
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> Dict[str, Any]:
        """Handle database errors gracefully"""
        logger.error(f"Database error during {operation}: {error}")
        
        return {
            "error": True,
            "message": "Service temporarily unavailable",
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fallback_active": True
        }
    
    @staticmethod
    def handle_api_error(error: Exception, endpoint: str) -> Dict[str, Any]:
        """Handle API errors with proper logging"""
        logger.error(f"API error at {endpoint}: {error}")
        
        return {
            "error": True,
            "message": "Request could not be processed",
            "endpoint": endpoint,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global instances
config = ProductionConfig()
db_manager = DatabaseManager(config)
cache_manager = CacheManager(config)
error_handler = ErrorHandler() 