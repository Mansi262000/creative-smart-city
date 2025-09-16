from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    role_id: int
    department: Optional[str] = None

class RoleOut(BaseModel):
    id: int
    name: str
    permissions: List[str]
    
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    department: Optional[str]
    is_active: bool
    role: Optional[RoleOut] = None
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Now Token can reference UserOut since it's defined above
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None

class SensorTypeOut(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    description: Optional[str]
    thresholds: Dict[str, Any]
    
    class Config:
        from_attributes = True

class SensorCreate(BaseModel):
    name: str
    sensor_type_id: int
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None

class SensorOut(BaseModel):
    id: int
    name: str
    sensor_type: SensorTypeOut
    location_lat: Optional[float]
    location_lng: Optional[float]
    location_address: Optional[str]
    status: str
    battery_level: Optional[float]
    signal_strength: Optional[float]
    last_maintenance: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    status: Optional[str] = None

class MetricIn(BaseModel):
    sensor_id: int
    metric_type: str
    value: float
    ts: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = 1.0

class MetricOut(BaseModel):
    id: int
    sensor_id: int
    metric_type: str
    value: float
    ts: datetime
    quality_score: float
    sensor: Optional[SensorOut] = None
    
    class Config:
        from_attributes = True

class MetricAggregation(BaseModel):
    metric_type: str
    sensor_id: Optional[int] = None
    time_period: str  # hour, day, week, month
    avg: float
    min: float
    max: float
    count: int
    last_value: float
    trend: Optional[str] = None  # increasing, decreasing, stable

class AlertCreate(BaseModel):
    sensor_id: int
    metric_type: str
    severity: SeverityLevel
    title: str
    message: str
    trigger_value: Optional[float] = None
    threshold_value: Optional[float] = None

class AlertOut(BaseModel):
    id: int
    alert_id: str
    sensor_id: int
    sensor: Optional[SensorOut] = None
    metric_type: str
    severity: SeverityLevel
    status: AlertStatus
    title: str
    message: str
    trigger_value: Optional[float]
    threshold_value: Optional[float]
    location_lat: Optional[float]
    location_lng: Optional[float]
    location_address: Optional[str]
    zone: Optional[str]
    assigned_to: Optional[UserOut] = None
    acknowledged_by: Optional[UserOut] = None
    acknowledged_at: Optional[datetime]
    resolved_by: Optional[UserOut] = None
    resolved_at: Optional[datetime]
    priority: int
    category: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None

class AlertAcknowledge(BaseModel):
    notes: Optional[str] = None

class AlertResolve(BaseModel):
    resolution: str
    notes: Optional[str] = None

class AlertActionOut(BaseModel):
    id: int
    action: str
    notes: Optional[str]
    timestamp: datetime
    user: UserOut
    
    class Config:
        from_attributes = True

# Rest of your schemas remain the same...
class DashboardWidget(BaseModel):
    type: str
    title: str
    position: Dict[str, int]
    size: Dict[str, int]
    config: Dict[str, Any]

class DashboardCreate(BaseModel):
    name: str
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[List[DashboardWidget]] = None
    is_public: bool = False

class DashboardOut(BaseModel):
    id: int
    name: str
    layout: Optional[Dict[str, Any]]
    widgets: Optional[List[DashboardWidget]]
    is_public: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[UserOut] = None
    
    class Config:
        from_attributes = True

# Add the rest of your schemas here...

class ReportCreate(BaseModel):
    title: str
    type: str
    category: str
    parameters: Dict[str, Any]

class ReportOut(BaseModel):
    id: int
    title: str
    type: str
    category: str
    parameters: Dict[str, Any]
    status: str
    file_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    generated_by: Optional[UserOut] = None
    
    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    read: bool
    data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_sensors: int
    active_sensors: int
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    system_health: float
    uptime: str
    last_updated: datetime

class SensorStats(BaseModel):
    sensor_id: int
    sensor_name: str
    total_metrics: int
    last_reading: Optional[datetime]
    avg_value_24h: Optional[float]
    status: str
    health_score: float

class AnalyticsData(BaseModel):
    metric_type: str
    time_series: List[Dict[str, Any]]
    aggregations: Dict[str, float]
    trends: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None

class OptimizationSuggestion(BaseModel):
    id: str
    category: str
    title: str
    description: str
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    savings: Optional[Dict[str, Any]] = None
    implementation_steps: List[str]
    confidence_score: float

class TrafficOptimization(BaseModel):
    intersection_id: str
    current_timing: Dict[str, int]
    suggested_timing: Dict[str, int]
    expected_improvement: float
    reason: str

class EnergyOptimization(BaseModel):
    grid_section: str
    current_load: float
    suggested_redistribution: Dict[str, float]
    expected_savings: float
    reason: str

class WasteOptimization(BaseModel):
    route_id: str
    current_route: List[Dict[str, Any]]
    optimized_route: List[Dict[str, Any]]
    time_savings: float
    fuel_savings: float
    reason: str

class PredictiveAlert(BaseModel):
    sensor_id: int
    metric_type: str
    predicted_value: float
    predicted_time: datetime
    confidence: float
    severity: SeverityLevel
    message: str

class SummaryPoint(BaseModel):
    metric_type: str
    count: int
    avg: float
    min: float
    max: float

# Query Parameters
class AlertFilters(BaseModel):
    severity: Optional[List[SeverityLevel]] = None
    status: Optional[List[AlertStatus]] = None
    category: Optional[List[str]] = None
    assigned_to_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sensor_ids: Optional[List[int]] = None

class MetricFilters(BaseModel):
    sensor_ids: Optional[List[int]] = None
    metric_types: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class SensorFilters(BaseModel):
    category: Optional[str] = None
    status: Optional[List[str]] = None
    location_bounds: Optional[Dict[str, float]] = None  # lat_min, lat_max, lng_min, lng_max

# Response models
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
