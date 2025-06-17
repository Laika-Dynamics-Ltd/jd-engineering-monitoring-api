# JD Engineering Monitoring API

A FastAPI-based monitoring system for tracking tablet device metrics in engineering environments. This system collects and analyzes device performance, network connectivity, and application usage data from Android tablets deployed in field operations.

## 🏗️ Architecture

- **Backend**: FastAPI with async PostgreSQL support
- **Database**: PostgreSQL (via asyncpg)
- **Authentication**: JWT tokens with python-jose
- **Deployment**: Railway with Docker containerization
- **Client**: Python script for Termux-enabled Android tablets

## 📋 Features

### Device Monitoring
- Battery level and temperature tracking
- Memory usage and CPU performance
- Screen state and activity monitoring
- Real-time connectivity status

### Network Analytics
- WiFi signal strength monitoring
- DNS response time tracking
- Connection stability analysis
- Network type detection

### Session Management
- User login/logout tracking
- Session duration analysis
- Application usage patterns
- Notification monitoring

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/tablet-metrics` | POST | Submit device metrics |
| `/devices` | GET | List all monitored devices |
| `/devices/{device_id}/metrics` | GET | Get device-specific metrics |
| `/analytics/session-issues` | GET | Session analytics and issues |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Railway account (for deployment)
- Android tablet with Termux (for client)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jd-engineering-monitoring-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/monitoring_db"
   export API_SECRET_KEY="your-secret-key"
   export API_TOKEN="your-api-token"
   ```

4. **Run the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

```bash
# Build the image
docker build -t monitoring-api .

# Run the container
docker run -p 8000:8000 \
  -e DATABASE_URL="your-db-url" \
  -e API_SECRET_KEY="your-secret" \
  monitoring-api
```

### Railway Deployment

1. **Deploy to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login and deploy
   railway login
   railway link
   railway up
   ```

2. **Configure environment variables in Railway dashboard**
   - `DATABASE_URL`: PostgreSQL connection string
   - `API_SECRET_KEY`: JWT secret key
   - `API_TOKEN`: API authentication token

## 📱 Client Setup (Android Tablet)

### Termux Installation

1. Install Termux from F-Droid or Google Play
2. Install required packages:
   ```bash
   pkg update && pkg upgrade
   pkg install python termux-api
   ```

3. Configure the monitoring script:
   ```bash
   # Edit configuration in tablet_client.py
   RAILWAY_API_URL = "https://your-app.railway.app"
   API_TOKEN = "your-railway-api-token"
   DEVICE_ID = "tablet_electrical_dept"
   ```

4. Run the monitoring client:
   ```bash
   python scripts/tablet_client.py
   ```

### Client Features

- **Automatic Data Collection**: Collects metrics every 30 seconds
- **Battery Monitoring**: Level, temperature, and charging status
- **Network Testing**: WiFi strength, connectivity, and latency
- **Screen Activity**: Active/locked state detection
- **Error Recovery**: Automatic retry on connection failures

## 🧪 Testing

### API Testing

Run the comprehensive test suite:

```bash
python scripts/test_api.py https://your-app.railway.app your-api-token
```

### Test Coverage

The test script validates:
- Health check endpoint
- Data submission functionality
- Device listing and metrics retrieval
- Session analytics endpoints
- Authentication and authorization

## 📊 Data Models

### Device Metrics
```json
{
  "device_id": "tablet_electrical_dept",
  "device_name": "Android Tablet - Electrical Dept",
  "location": "Electrical Department",
  "timestamp": "2024-01-15T10:30:00Z",
  "device_metrics": {
    "battery_level": 85,
    "battery_temperature": 32.5,
    "memory_available": 2147483648,
    "cpu_usage": 45.2
  },
  "network_metrics": {
    "wifi_signal_strength": -45,
    "connectivity_status": "online",
    "dns_response_time": 12.5
  },
  "app_metrics": {
    "screen_state": "active",
    "notification_count": 3
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `API_SECRET_KEY` | JWT token secret | Yes |
| `API_TOKEN` | Client authentication token | Yes |
| `PORT` | Server port (default: 8000) | No |

### Client Configuration

Update `scripts/tablet_client.py`:
- `RAILWAY_API_URL`: Your deployed API endpoint
- `API_TOKEN`: Authentication token
- `DEVICE_ID`: Unique identifier for the tablet

## 📈 Monitoring & Analytics

### Health Monitoring
- API uptime and response times
- Database connection status
- Client connectivity status

### Performance Metrics
- Device battery degradation patterns
- Network connectivity reliability
- Application usage statistics
- Session duration analytics

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **asyncpg**: Async PostgreSQL driver for high performance
- **Pydantic**: Data validation using Python type annotations
- **python-jose**: JWT token handling
- **Uvicorn**: ASGI server implementation
- **Gunicorn**: WSGI HTTP server for production

## 🚨 Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check network connectivity
   - Verify API endpoint URL
   - Confirm authentication token

2. **Authentication Errors**
   - Validate API_TOKEN configuration
   - Check JWT secret key setup
   - Verify token expiration

3. **Data Collection Issues**
   - Ensure Termux API permissions
   - Check Android battery optimization settings
   - Verify script execution permissions

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=debug
uvicorn main:app --log-level debug
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the engineering team
- Check the troubleshooting section above

---

**Status**: Production Ready | **Version**: 1.0.0 | **Last Updated**: $(date +%Y-%m-%d)
