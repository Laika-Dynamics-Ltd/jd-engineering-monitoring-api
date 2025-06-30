#!/usr/bin/env python3
"""
Initialize Database Tables for JD Engineering Monitoring API
Run this to create all required tables in PostgreSQL
"""

import asyncio
import asyncpg
import os
import sys

# Database connection string
DATABASE_URL = "postgresql://postgres:qEQLrrqeSJKiiIYrowvcilAGauMiAHOB@interchange.proxy.rlwy.net:40358/railway"

async def init_postgres_tables(conn):
    """Initialize PostgreSQL tables"""
    print("🔄 Creating PostgreSQL tables...")
    
    # Create extension for better timestamp handling
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Device metrics table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS device_metrics (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            battery_level INTEGER,
            battery_temperature FLOAT,
            memory_available BIGINT,
            memory_total BIGINT,
            storage_available BIGINT,
            cpu_usage FLOAT,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created device_metrics table")
    
    # Network metrics table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS network_metrics (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            wifi_signal_strength INTEGER,
            wifi_ssid VARCHAR(100),
            connectivity_status VARCHAR(20),
            network_type VARCHAR(50),
            ip_address VARCHAR(45),
            dns_response_time FLOAT,
            data_usage_mb FLOAT,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created network_metrics table")
    
    # App metrics table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS app_metrics (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            screen_state VARCHAR(20),
            app_foreground VARCHAR(200),
            app_memory_usage BIGINT,
            screen_timeout_setting INTEGER,
            last_user_interaction TIMESTAMPTZ,
            notification_count INTEGER,
            app_crashes INTEGER,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created app_metrics table")
    
    # Session events table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS session_events (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            event_type VARCHAR(50),
            session_id VARCHAR(100),
            duration INTEGER,
            error_message TEXT,
            user_id VARCHAR(100),
            app_version VARCHAR(50),
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created session_events table")
    
    # Raw logs table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS raw_logs (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            log_entry TEXT,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created raw_logs table")
    
    # Device registry table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS device_registry (
            id SERIAL PRIMARY KEY,
            device_id VARCHAR(50) UNIQUE NOT NULL,
            device_name VARCHAR(100),
            location VARCHAR(100),
            android_version VARCHAR(50),
            app_version VARCHAR(50),
            first_seen TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created device_registry table")
    
    # Create indexes for performance
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id ON device_metrics(device_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_device_metrics_timestamp ON device_metrics(timestamp)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_network_metrics_device_id ON network_metrics(device_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_app_metrics_device_id ON app_metrics(device_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_session_events_device_id ON session_events(device_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_device_registry_last_seen ON device_registry(last_seen)')
    print("✅ Created indexes")

async def main():
    """Main function to initialize database"""
    print("🚀 JD Engineering Database Initialization")
    print("=" * 50)
    print(f"📍 Database: Railway PostgreSQL")
    print(f"🌐 Connection: {DATABASE_URL[:50]}...")
    print("=" * 50)
    
    try:
        # Create connection
        print("🔄 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected successfully")
        
        # Initialize tables
        await init_postgres_tables(conn)
        
        # Verify tables
        print("\n📊 Verifying tables...")
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """
        tables = await conn.fetch(tables_query)
        
        print("\n✅ Created tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Test device registry
        test_query = "SELECT COUNT(*) as count FROM device_registry"
        result = await conn.fetchval(test_query)
        print(f"\n📱 Device registry ready: {result} devices registered")
        
        await conn.close()
        print("\n🎉 Database initialization complete!")
        print("✅ Your tablets can now connect and send data")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check DATABASE_URL is correct")
        print("2. Verify PostgreSQL service is running on Railway")
        print("3. Check network connectivity")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 