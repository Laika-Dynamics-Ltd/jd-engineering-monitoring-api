#!/usr/bin/env python3
"""
Database Migration Script for JD Engineering Monitoring API
Adds missing columns to support new tablet client data format
"""

import asyncio
import asyncpg
import os
from datetime import datetime

async def migrate_database():
    """Add missing columns to existing tables"""
    
    # Connect to Railway PostgreSQL database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return False
    
    print("🔄 Starting database migration...")
    print(f"📡 Connecting to database: {database_url[:50]}...")
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to PostgreSQL database")
        
        # Check if tables exist and get current schema
        tables_query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name IN ('device_metrics', 'network_metrics', 'app_metrics', 'session_events', 'device_registry')
        ORDER BY table_name, ordinal_position;
        """
        
        existing_schema = await conn.fetch(tables_query)
        print(f"📊 Found {len(existing_schema)} existing columns")
        
        # Get current columns by table
        current_columns = {}
        for row in existing_schema:
            table = row['table_name']
            if table not in current_columns:
                current_columns[table] = []
            current_columns[table].append(row['column_name'])
        
        print("🔍 Current table structure:")
        for table, columns in current_columns.items():
            print(f"   {table}: {len(columns)} columns")
        
        # Migration steps
        migrations = []
        
        # 1. Add missing columns to device_metrics
        if 'device_metrics' in current_columns:
            device_columns = current_columns['device_metrics']
            if 'battery_status' not in device_columns:
                migrations.append(("device_metrics", "ADD COLUMN battery_status TEXT"))
            if 'source' not in device_columns:
                migrations.append(("device_metrics", "ADD COLUMN source TEXT"))
        else:
            # Create device_metrics table if it doesn't exist
            migrations.append(("device_metrics", "CREATE_TABLE"))
        
        # 2. Add missing columns to network_metrics  
        if 'network_metrics' in current_columns:
            network_columns = current_columns['network_metrics']
            if 'source' not in network_columns:
                migrations.append(("network_metrics", "ADD COLUMN source TEXT"))
        else:
            migrations.append(("network_metrics", "CREATE_TABLE"))
        
        # 3. Add missing columns to app_metrics
        if 'app_metrics' in current_columns:
            app_columns = current_columns['app_metrics']
            missing_app_columns = []
            for col in ['myob_active', 'scanner_active', 'recent_movement', 'inactive_seconds', 'source']:
                if col not in app_columns:
                    missing_app_columns.append(col)
            
            for col in missing_app_columns:
                if col in ['myob_active', 'scanner_active', 'recent_movement']:
                    migrations.append(("app_metrics", f"ADD COLUMN {col} BOOLEAN"))
                elif col == 'inactive_seconds':
                    migrations.append(("app_metrics", f"ADD COLUMN {col} INTEGER CHECK ({col} >= 0)"))
                else:
                    migrations.append(("app_metrics", f"ADD COLUMN {col} TEXT"))
        else:
            migrations.append(("app_metrics", "CREATE_TABLE"))
        
        # 4. Create missing tables
        for table in ['session_events', 'device_registry']:
            if table not in current_columns:
                migrations.append((table, "CREATE_TABLE"))
        
        print(f"📝 {len(migrations)} migration steps required")
        
        # Execute migrations
        migration_count = 0
        for table, action in migrations:
            try:
                if action == "CREATE_TABLE":
                    await create_table(conn, table)
                    print(f"✅ Created table: {table}")
                else:
                    sql = f"ALTER TABLE {table} {action}"
                    await conn.execute(sql)
                    print(f"✅ Updated {table}: {action}")
                migration_count += 1
            except Exception as e:
                print(f"⚠️ Migration warning for {table}: {e}")
        
        print(f"🎉 Database migration completed! {migration_count} changes applied")
        
        # Verify the migration worked
        updated_schema = await conn.fetch(tables_query)
        print(f"📊 After migration: {len(updated_schema)} total columns")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

async def create_table(conn, table_name):
    """Create missing tables with proper schema"""
    
    if table_name == "device_metrics":
        sql = '''
        CREATE TABLE IF NOT EXISTS device_metrics (
            id BIGSERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            battery_level INTEGER CHECK (battery_level >= 0 AND battery_level <= 100),
            battery_temperature FLOAT,
            battery_status TEXT,
            memory_available BIGINT CHECK (memory_available >= 0),
            memory_total BIGINT CHECK (memory_total >= 0),
            storage_available BIGINT CHECK (storage_available >= 0),
            cpu_usage FLOAT CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
            source TEXT,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        '''
    elif table_name == "network_metrics":
        sql = '''
        CREATE TABLE IF NOT EXISTS network_metrics (
            id BIGSERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            wifi_signal_strength INTEGER CHECK (wifi_signal_strength >= -100 AND wifi_signal_strength <= 0),
            wifi_ssid VARCHAR(100),
            connectivity_status VARCHAR(20) NOT NULL CHECK (connectivity_status IN ('online', 'offline', 'limited', 'unknown')),
            network_type VARCHAR(50),
            ip_address TEXT,
            dns_response_time FLOAT CHECK (dns_response_time >= 0),
            data_usage_mb FLOAT CHECK (data_usage_mb >= 0),
            source TEXT,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        '''
    elif table_name == "app_metrics":
        sql = '''
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
            myob_active BOOLEAN,
            scanner_active BOOLEAN,
            recent_movement BOOLEAN,
            inactive_seconds INTEGER CHECK (inactive_seconds >= 0),
            source TEXT,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        '''
    elif table_name == "session_events":
        sql = '''
        CREATE TABLE IF NOT EXISTS session_events (
            id BIGSERIAL PRIMARY KEY,
            device_id VARCHAR(50) NOT NULL,
            event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('login', 'logout', 'timeout', 'error', 'reconnect', 'session_start', 'session_end')),
            session_id VARCHAR(100),
            duration INTEGER CHECK (duration >= 0),
            error_message VARCHAR(500),
            user_id VARCHAR(100),
            app_version VARCHAR(50),
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        '''
    elif table_name == "device_registry":
        sql = '''
        CREATE TABLE IF NOT EXISTS device_registry (
            id BIGSERIAL PRIMARY KEY,
            device_id VARCHAR(50) UNIQUE NOT NULL,
            device_name VARCHAR(100),
            location VARCHAR(100),
            android_version VARCHAR(50),
            app_version VARCHAR(50),
            first_seen TIMESTAMPTZ DEFAULT NOW(),
            last_seen TIMESTAMPTZ DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        '''
    
    await conn.execute(sql)
    
    # Create indexes
    await conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_device_id ON {table_name}(device_id)')
    if table_name != "device_registry":
        await conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name}(timestamp)')

if __name__ == "__main__":
    print("🚀 JD Engineering Database Migration")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run migration
    success = asyncio.run(migrate_database())
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📊 The tablet data should now be stored properly in the database")
        print("🔄 Try refreshing your dashboard to see the devices")
    else:
        print("\n❌ Migration failed - check the error messages above")
    
    print("=" * 50) 