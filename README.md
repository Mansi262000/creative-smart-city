# Smart City Management Platform

A comprehensive IoT-enabled smart city management system with real-time monitoring, predictive analytics, and advanced alert management.

## 🌟 Features

### Core Functionality
- **Real-time Monitoring**: Live sensor data from traffic, environment, utilities, and waste management
- **Advanced Analytics**: Predictive analytics with ML-powered insights and optimization suggestions
- **Alert Management**: Intelligent alert system with escalation, acknowledgment, and resolution workflows
- **Role-based Access**: Granular permissions for different city departments
- **Interactive Dashboard**: Modern React-based UI with real-time updates via WebSocket

### Technical Features
- **Scalable Architecture**: Microservices with Docker containers
- **Real-time Communication**: WebSocket-based live updates
- **IoT Integration**: MQTT broker for sensor data ingestion
- **Data Analytics**: Time-series data processing and trend analysis
- **Monitoring & Logging**: Comprehensive observability with Prometheus, Grafana, and ELK stack
- **API-First Design**: RESTful APIs with OpenAPI documentation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   PostgreSQL    │
│                 │    │                 │    │    Database     │
│  - Dashboard    │◄──►│  - REST APIs    │◄──►│                 │
│  - Real-time UI │    │  - WebSocket    │    │  - Sensor Data  │
│  - Charts       │    │  - Analytics    │    │  - Alerts       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   MQTT Broker   │    │      Redis      │
│   (Reverse      │    │   (Mosquitto)   │    │   (Caching)     │
│    Proxy)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                                ▼
                    ┌─────────────────┐
                    │  IoT Sensors    │
                    │  & Simulator    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd smart-city-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Configuration section)
nano .env
```

### 3. Start with Docker Compose
```bash
# Start core services
docker-compose up -d

# Or start with all services including monitoring
docker-compose --profile monitoring --profile simulation up -d

# Check service status
docker-compose ps
```

### 4. Access the Application
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:3000/admin
- **Monitoring (Grafana)**: http://localhost:3001 (admin/admin123)
- **Logs (Kibana)**: http://localhost:5601

### 5. Login Credentials
```
Role: Admin
Username: admin@city.local
Password: admin123

Other demo accounts:
- traffic@city.local / traffic123 (Traffic Controller)
- env@city.local / env123 (Environment Officer)
- utility@city.local / utility123 (Utility Manager)
```

## 📁 Project Structure

```
smart-city-platform/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic services
│   │   ├── middleware/        # Custom middleware
│   │   └── main.py           # Application entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API and WebSocket services
│   │   ├── utils/            # Utility functions
│   │   └── App.jsx           # Main application component
│   ├── package.json
│   └── Dockerfile
├── database/                   # Database scripts and migrations
│   ├── migrations/
│   └── init/
├── monitoring/                 # Monitoring configuration
│   ├── prometheus/
│   ├── grafana/
│   └── logstash/
├── nginx/                      # Nginx configuration
├── simulation/                 # Sensor data simulator
├── tests/                      # Test suites
├── docker-compose.yml          # Main compose file
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── .env.example               # Environment template
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

#### Database Configuration
```bash
DB_NAME=smartcity
DB_USER=city
DB_PASSWORD=your_secure_password_here
DB_PORT=5432
```

#### Security Configuration
```bash
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRE_MINUTES=1440
ENCRYPTION_KEY=your-32-character-encryption-key
```

#### Feature Flags
```bash
ALLOW_DEMO_SEED=true           # Enable demo data seeding
ENABLE_ANALYTICS=true          # Enable predictive analytics
ENABLE_PREDICTIONS=true        # Enable ML predictions
```

#### External Services
```bash
EMAIL_SERVICE_URL=             # Email notification service
SMS_SERVICE_URL=               # SMS notification service
```

### Sensor Types and Categories

The platform supports various sensor types organized by category:

#### Traffic
- `traffic_congestion` - Vehicle count and speed monitoring
- `traffic_signal_status` - Traffic light operational status
- `parking_occupancy` - Parking space availability

#### Environment
- `air_quality_pm25` - PM2.5 air pollution levels
- `air_quality_pm10` - PM10 air pollution levels
- `noise_level` - Ambient noise monitoring
- `weather_temperature` - Temperature sensors
- `weather_humidity` - Humidity sensors

#### Utilities
- `energy_usage` - Power consumption monitoring
- `water_pressure` - Water system pressure
- `water_quality` - Water quality parameters
- `power_grid_load` - Electrical grid load monitoring

#### Waste Management
- `waste_level` - Waste bin fill levels
- `recycling_rate` - Recycling efficiency metrics

## 🚀 Deployment Options

### Development Deployment
```bash
# Start development environment with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend frontend
```

### Production Deployment
```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable monitoring and logging
docker-compose --profile monitoring --profile logging up -d
```

### Cloud Deployment (AWS/GCP/Azure)

#### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml smart-city

# Scale services
docker service scale smart-city_backend=3
```

#### Using Kubernetes
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Deploy to cluster
kubectl apply -f .
```

## 📊 Monitoring and Observability

### Metrics (Prometheus + Grafana)
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: Sensor health, alert volumes, user activity

### Logging (ELK Stack)
- **Application Logs**: Structured JSON logs from all services
- **Access Logs**: Nginx request logs
- **Audit Logs**: User actions and system changes

### Health Checks
```bash
# Check overall system health
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# WebSocket connection stats
curl http://localhost:8000/api/ws/stats
```

## 🔧 Development

### Local Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

#### Database Setup
```bash
# Start only database
docker-compose up -d postgres

# Run migrations
cd backend
alembic upgrade head

# Seed demo data
python -c "from app.db import seed_demo_user_if_enabled; seed_demo_user_if_enabled()"
```

### Testing

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

#### Integration Tests
```bash
# Start test environment
docker-compose --profile testing up -d

# Run integration tests
docker-compose exec tests pytest /app/tests/integration/
```

### API Documentation

#### Interactive API Docs
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

#### API Endpoints Overview

##### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user profile

##### Sensors
- `GET /api/sensors` - List all sensors
- `POST /api/sensors` - Create new sensor
- `GET /api/sensors/{id}` - Get sensor details
- `PUT /api/sensors/{id}` - Update sensor
- `DELETE /api/sensors/{id}` - Delete sensor

##### Metrics
- `GET /api/metrics` - Get sensor metrics
- `POST /api/metrics/ingest` - Ingest new metrics
- `GET /api/metrics/summary` - Get aggregated metrics
- `GET /api/metrics/analytics` - Get analytics data

##### Alerts
- `GET /api/alerts` - List alerts with filtering
- `POST /api/alerts` - Create new alert
- `PUT /api/alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /api/alerts/{id}/resolve` - Resolve alert
- `GET /api/alerts/stats` - Get alert statistics

##### WebSocket
- `WS /api/ws/ws` - Real-time WebSocket connection
- `POST /api/ws/broadcast` - Admin broadcast message
- `GET /api/ws/stats` - Connection statistics

## 🎯 Use Cases and Scenarios

### Traffic Management
```javascript
// Monitor traffic congestion
const trafficData = await api.get('/api/metrics', {
  params: { sensor_type: 'traffic_congestion', time_range: '1h' }
});

// Apply optimization suggestions
await api.post('/api/analytics/apply-optimization', {
  optimization_id: 'traffic-signal-timing-001'
});
```

### Environmental Monitoring
```javascript
// Check air quality
const airQuality = await api.get('/api/sensors', {
  params: { category: 'environment', type: 'air_quality_pm25' }
});

// Create environmental alert
if (airQuality.current_value > 100) {
  await api.post('/api/alerts', {
    sensor_id: airQuality.id,
    severity: 'high',
    title: 'Air Quality Alert',
    message: 'PM2.5 levels exceed safe limits'
  });
}
```

### Waste Management Optimization
```javascript
// Get waste bin status
const wasteBins = await api.get('/api/sensors', {
  params: { category: 'waste' }
});

// Get optimized collection routes
const routes = await api.get('/api/analytics/waste-routes', {
  params: { min_fill_level: 80 }
});
```

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: Granular permissions by user role
- **Session Management**: Secure session handling with Redis

### Data Security
- **Encryption**: Data encryption at rest and in transit
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Secure cross-origin requests

### Network Security
- **Reverse Proxy**: Nginx with security headers
- **SSL/TLS**: HTTPS encryption for all communications
- **Container Security**: Isolated container environments

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### WebSocket Connection Issues
```bash
# Check WebSocket service
curl -H "Upgrade: websocket" \
     -H "Connection: upgrade" \
     -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/api/ws/ws

# View WebSocket logs
docker-compose logs backend | grep -i websocket
```

#### Frontend Build Issues
```bash
# Clear node modules and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# View performance metrics
curl http://localhost:8000/api/system/info

# Scale services
docker-compose up -d --scale backend=3
```

### Log Analysis

#### Application Logs
```bash
# View all logs
docker-compose logs -f

# Filter by service
docker-compose logs -f backend frontend

# Search for errors
docker-compose logs backend | grep -i error
```

#### Access Logs
```bash
# Nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Application access logs
docker-compose logs backend | grep "GET\|POST"
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# Manual backup
docker-compose exec postgres pg_dump -U city smartcity > backup.sql

# Automated backup (runs daily at 2 AM)
docker-compose --profile backup up -d backup

# Restore from backup
docker-compose exec postgres psql -U city smartcity < backup.sql
```

### Configuration Backup
```bash
# Backup all configuration
tar -czf config-backup.tar.gz \
  .env nginx/ monitoring/ database/

# Backup volumes
docker run --rm -v smart-city_postgres_data:/data \
  -v $(pwd):/backup ubuntu \
  tar -czf /backup/postgres-data.tar.gz /data
```

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Optimized indexes for time-series data
- **Partitioning**: Table partitioning for large datasets
- **Connection Pooling**: Efficient database connections

### API Optimization
- **Caching**: Redis caching for frequently accessed data
- **Pagination**: Efficient data pagination
- **Compression**: Response compression with gzip

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Caching**: Browser and CDN caching
- **Bundling**: Optimized JavaScript bundles

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` and `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create a Pull Request

### Code Standards
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow ESLint configuration
- **Commit Messages**: Use conventional commit format
- **Documentation**: Update docs for new features

### Testing Requirements
- Unit tests for all new functions
- Integration tests for API endpoints
- Frontend component tests
- End-to-end tests for critical user flows

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: contact@smartcity-platform.com

### Commercial Support
For enterprise support, custom development, and consulting services, contact our team.

---

## 🎯 Quick Commands Reference

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f [service_name]

# Scale services
docker-compose up -d --scale backend=3

# Update services
docker-compose pull && docker-compose up -d

# Stop all services
docker-compose down

# Clean up (removes volumes)
docker-compose down -v

# Health check
curl http://localhost:8000/health

# Database backup
docker-compose exec postgres pg_dump -U city smartcity > backup.sql
```

---

Built with ❤️ for smarter cities and better urban management.