# Smart City Platform

A comprehensive IoT-based smart city management system with real-time monitoring, alerting, and analytics capabilities.

## Project Architecture

### System Overview
```
Frontend (React/Vite) ←→ Backend (FastAPI) ←→ Database (PostgreSQL)
     ↓                        ↓                      ↓
Dashboard UI           REST APIs              Data Storage
Analytics              Authentication         Sensor Data
Alerts                 CRUD Operations        User Management
```

### Technology Stack

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- Recharts for data visualization
- Responsive design

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL database
- JWT authentication
- Pydantic for data validation

**Infrastructure:**
- Docker & Docker Compose
- GitHub Codespaces
- RESTful API design

## Database Schema (ER Diagram)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Users    │    │    Roles     │    │   Sensors   │
├─────────────┤    ├──────────────┤    ├─────────────┤
│ id (PK)     │───→│ id (PK)      │    │ id (PK)     │
│ email       │    │ name         │    │ name        │
│ password_hash│   │ permissions  │    │ location    │
│ role_id (FK)│    └──────────────┘    │ sensor_type │
│ created_at  │                        │ status      │
└─────────────┘                        │ created_at  │
                                       └─────────────┘
                                              │
┌─────────────┐    ┌──────────────┐          │
│   Alerts    │    │   Metrics    │          │
├─────────────┤    ├──────────────┤          │
│ id (PK)     │    │ id (PK)      │          │
│ alert_id    │    │ sensor_id(FK)│←─────────┘
│ title       │    │ metric_type  │
│ message     │    │ value        │
│ severity    │    │ timestamp    │
│ status      │    │ created_at   │
│ category    │    └──────────────┘
│ created_at  │
└─────────────┘
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Sensors
- `GET /sensors` - List all sensors
- `POST /sensors` - Create sensor
- `GET /sensors/{id}` - Get sensor details
- `PUT /sensors/{id}` - Update sensor

### Alerts
- `GET /alerts` - List alerts
- `POST /alerts` - Create alert
- `POST /alerts/{id}/acknowledge` - Acknowledge alert
- `POST /alerts/{id}/resolve` - Resolve alert

### Metrics
- `GET /metrics` - List metrics
- `POST /metrics` - Add metric data

## Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd smart-city-platform

# Start services
docker-compose up -d

# Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

### Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev
```

## Features Implemented

### Core Features
✅ User authentication (JWT)
✅ Role-based access control
✅ Sensor data management
✅ Real-time alert system
✅ Dashboard with metrics
✅ Responsive UI design

### Dashboard Capabilities
- **Overview Tab**: System metrics, sensor status, live charts
- **Traffic Management**: Traffic flow monitoring
- **Environmental Monitoring**: Air quality data
- **Alert Management**: Create, acknowledge, resolve alerts
- **Analytics**: Data visualization and trends

### Security Features
- JWT token authentication
- Password hashing (bcrypt)
- Role-based permissions
- CORS protection
- Input validation

## Demo Credentials
- **Email**: admin@example.com
- **Password**: admin123
- **Role**: Administrator

## File Structure
```
smart-city-platform/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Authentication
│   │   ├── db.py           # Database config
│   │   └── routers/        # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main app
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Login test
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

## Deployment Considerations

### Production Setup
- Use environment variables for secrets
- Enable HTTPS/SSL
- Configure proper CORS origins
- Set up database backups
- Implement monitoring and logging

### Scaling Options
- Load balancer for frontend
- Database read replicas
- Redis for caching
- Microservices architecture
- Container orchestration (Kubernetes)

## Future Enhancements

### Planned Features
- Real-time WebSocket updates
- Mobile app (React Native)
- Advanced analytics with ML
- Integration with IoT devices
- Notification system (SMS/Email)
- Report generation (PDF/Excel)

### Technical Improvements
- Unit test coverage > 80%
- API rate limiting
- Database optimization
- Caching layer
- CI/CD pipeline

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License
MIT License

## Support
For issues and questions, please create GitHub issues or contact the development team.
