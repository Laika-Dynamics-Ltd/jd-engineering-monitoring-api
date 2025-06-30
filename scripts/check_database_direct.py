import asyncio
import asyncpg
import json

DATABASE_URL = "postgresql://postgres:qEQLrrqeSJKiiIYrowvcilAGauMiAHOB@interchange.proxy.rlwy.net:40358/railway"

async def check_data():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Check device registry
    devices = await conn.fetch("SELECT * FROM device_registry")
    print(f"📱 Device Registry: {len(devices)} devices")
    for device in devices:
        print(f"   - {device['device_id']} ({device['device_name']})")
    
    # Check recent metrics
    metrics = await conn.fetch("SELECT DISTINCT device_id FROM device_metrics ORDER BY created_at DESC LIMIT 10")
    print(f"\n📊 Recent Device Metrics: {len(metrics)} devices")
    for metric in metrics:
        print(f"   - {metric['device_id']}")
    
    # Check raw data
    total_metrics = await conn.fetchval("SELECT COUNT(*) FROM device_metrics")
    print(f"\n📈 Total Metrics Stored: {total_metrics}")
    
    await conn.close()

asyncio.run(check_data())
