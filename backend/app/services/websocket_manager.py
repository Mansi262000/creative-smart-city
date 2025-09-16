import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from .auth import get_current_user_websocket
from . import models

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Active connections: user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Role-based connections: role_name -> set of websockets
        self.role_connections: Dict[str, Set[WebSocket]] = {}
        # Channel subscriptions: channel -> set of websockets
        self.channel_subscriptions: Dict[str, Set[WebSocket]] = {}
        # WebSocket to user mapping
        self.ws_to_user: Dict[WebSocket, int] = {}
        # WebSocket to role mapping
        self.ws_to_role: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        """Connect a websocket for a specific user and role"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Add to role connections
        if role not in self.role_connections:
            self.role_connections[role] = set()
        self.role_connections[role].add(websocket)
        
        # Store mappings
        self.ws_to_user[websocket] = user_id
        self.ws_to_role[websocket] = role
        
        logger.info(f"User {user_id} ({role}) connected via WebSocket")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_status",
            "status": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "role": role
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket"""
        user_id = self.ws_to_user.get(websocket)
        role = self.ws_to_role.get(websocket)
        
        # Remove from user connections
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from role connections
        if role and role in self.role_connections:
            self.role_connections[role].discard(websocket)
            if not self.role_connections[role]:
                del self.role_connections[role]
        
        # Remove from channel subscriptions
        for channel, websockets in self.channel_subscriptions.items():
            websockets.discard(websocket)
        
        # Clean up mappings
        self.ws_to_user.pop(websocket, None)
        self.ws_to_role.pop(websocket, None)
        
        logger.info(f"User {user_id} ({role}) disconnected from WebSocket")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific websocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def send_to_user(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.disconnect(ws)

    async def send_to_role(self, message: dict, role: str):
        """Send a message to all connections of a specific role"""
        if role in self.role_connections:
            disconnected = set()
            for websocket in self.role_connections[role].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to role {role}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.disconnect(ws)

    async def send_to_channel(self, message: dict, channel: str):
        """Send a message to all subscribers of a channel"""
        if channel in self.channel_subscriptions:
            disconnected = set()
            for websocket in self.channel_subscriptions[channel].copy():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to channel {channel}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast(self, message: dict):
        """Send a message to all connected clients"""
        all_websockets = set()
        for user_connections in self.active_connections.values():
            all_websockets.update(user_connections)
        
        disconnected = set()
        for websocket in all_websockets:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)

    def subscribe_to_channel(self, websocket: WebSocket, channel: str):
        """Subscribe a websocket to a channel"""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)
        logger.info(f"WebSocket subscribed to channel: {channel}")

    def unsubscribe_from_channel(self, websocket: WebSocket, channel: str):
        """Unsubscribe a websocket from a channel"""
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(websocket)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
        logger.info(f"WebSocket unsubscribed from channel: {channel}")

    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        return {
            "total_connections": total_connections,
            "users_online": len(self.active_connections),
            "connections_by_role": {
                role: len(connections) 
                for role, connections in self.role_connections.items()
            },
            "channel_subscriptions": {
                channel: len(subscribers)
                for channel, subscribers in self.channel_subscriptions.items()
            }
        }

# Global connection manager instance
manager = ConnectionManager()

class WebSocketService:
    def __init__(self, db: Session):
        self.db = db

    async def handle_websocket_message(self, websocket: WebSocket, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        
        try:
            if message_type == "subscribe":
                await self._handle_subscribe(websocket, message)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(websocket, message)
            elif message_type == "acknowledge_alert":
                await self._handle_acknowledge_alert(websocket, message)
            elif message_type == "resolve_alert":
                await self._handle_resolve_alert(websocket, message)
            elif message_type == "request_data":
                await self._handle_data_request(websocket, message)
            elif message_type == "ping":
                await self._handle_ping(websocket)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await manager.send_personal_message({
                "type": "error",
                "message": "Internal server error"
            }, websocket)

    async def _handle_unsubscribe(self, websocket: WebSocket, message: dict):
        """Handle channel unsubscription"""
        channels = message.get("channels", [])
        for channel in channels:
            manager.unsubscribe_from_channel(websocket, channel)
        
        await manager.send_personal_message({
            "type": "unsubscription_confirmed",
            "channels": channels,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _handle_acknowledge_alert(self, websocket: WebSocket, message: dict):
        """Handle alert acknowledgment"""
        user_id = manager.ws_to_user.get(websocket)
        if not user_id:
            return
        
        alert_id = message.get("alert_id")
        notes = message.get("notes", "")
        
        # Find and update alert
        alert = self.db.query(models.Alert).filter(
            models.Alert.alert_id == alert_id
        ).first()
        
        if alert:
            alert.status = models.AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by_id = user_id
            alert.acknowledged_at = datetime.now(timezone.utc)
            alert.acknowledged_notes = notes
            
            # Add action log
            action = models.AlertAction(
                alert_id=alert.id,
                user_id=user_id,
                action="acknowledge",
                notes=notes
            )
            self.db.add(action)
            self.db.commit()
            
            # Broadcast alert update
            await manager.broadcast({
                "type": "alert_acknowledged",
                "alert_id": alert_id,
                "acknowledged_by": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            await manager.send_personal_message({
                "type": "action_success",
                "action": "acknowledge_alert",
                "alert_id": alert_id
            }, websocket)

    async def _handle_resolve_alert(self, websocket: WebSocket, message: dict):
        """Handle alert resolution"""
        user_id = manager.ws_to_user.get(websocket)
        if not user_id:
            return
        
        alert_id = message.get("alert_id")
        resolution = message.get("resolution", "")
        notes = message.get("notes", "")
        
        # Find and update alert
        alert = self.db.query(models.Alert).filter(
            models.Alert.alert_id == alert_id
        ).first()
        
        if alert:
            alert.status = models.AlertStatus.RESOLVED
            alert.resolved_by_id = user_id
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolution = resolution
            alert.resolution_notes = notes
            
            # Add action log
            action = models.AlertAction(
                alert_id=alert.id,
                user_id=user_id,
                action="resolve",
                notes=f"Resolution: {resolution}. Notes: {notes}"
            )
            self.db.add(action)
            self.db.commit()
            
            # Broadcast alert update
            await manager.broadcast({
                "type": "alert_resolved",
                "alert_id": alert_id,
                "resolved_by": user_id,
                "resolution": resolution,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            await manager.send_personal_message({
                "type": "action_success",
                "action": "resolve_alert",
                "alert_id": alert_id
            }, websocket)

    async def _handle_data_request(self, websocket: WebSocket, message: dict):
        """Handle real-time data requests"""
        data_type = message.get("data_type")
        parameters = message.get("parameters", {})
        
        if data_type == "sensor_data":
            await self._send_sensor_data(websocket, parameters)
        elif data_type == "alerts":
            await self._send_alerts(websocket, parameters)
        elif data_type == "system_stats":
            await self._send_system_stats(websocket)
        elif data_type == "analytics":
            await self._send_analytics(websocket, parameters)

    async def _handle_ping(self, websocket: WebSocket):
        """Handle ping request"""
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _send_sensor_data(self, websocket: WebSocket, parameters: dict):
        """Send latest sensor data"""
        sensor_types = parameters.get("sensor_types", [])
        limit = parameters.get("limit", 100)
        
        # Query latest metrics
        query = self.db.query(models.Metric).join(models.Sensor)
        
        if sensor_types:
            query = query.join(models.SensorType).filter(
                models.SensorType.name.in_(sensor_types)
            )
        
        metrics = query.order_by(models.Metric.ts.desc()).limit(limit).all()
        
        # Convert to JSON-serializable format
        data = []
        for metric in metrics:
            data.append({
                "id": metric.id,
                "sensor_id": metric.sensor_id,
                "sensor_name": metric.sensor.name,
                "metric_type": metric.metric_type,
                "value": metric.value,
                "timestamp": metric.ts.isoformat(),
                "location": {
                    "lat": metric.sensor.location_lat,
                    "lng": metric.sensor.location_lng,
                    "address": metric.sensor.location_address
                }
            })
        
        await manager.send_personal_message({
            "type": "sensor_data_response",
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _send_alerts(self, websocket: WebSocket, parameters: dict):
        """Send active alerts"""
        status_filter = parameters.get("status", ["active"])
        severity_filter = parameters.get("severity", [])
        
        query = self.db.query(models.Alert).filter(
            models.Alert.status.in_(status_filter)
        )
        
        if severity_filter:
            query = query.filter(models.Alert.severity.in_(severity_filter))
        
        alerts = query.order_by(models.Alert.created_at.desc()).limit(50).all()
        
        # Convert to JSON-serializable format
        data = []
        for alert in alerts:
            data.append({
                "id": alert.id,
                "alert_id": alert.alert_id,
                "sensor_id": alert.sensor_id,
                "sensor_name": alert.sensor.name if alert.sensor else None,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "created_at": alert.created_at.isoformat(),
                "location": {
                    "lat": alert.location_lat,
                    "lng": alert.location_lng,
                    "address": alert.location_address
                }
            })
        
        await manager.send_personal_message({
            "type": "alerts_response",
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _send_system_stats(self, websocket: WebSocket):
        """Send system statistics"""
        # Count sensors by status
        sensor_stats = self.db.query(
            models.Sensor.status,
            self.db.func.count(models.Sensor.id)
        ).group_by(models.Sensor.status).all()
        
        # Count alerts by severity
        alert_stats = self.db.query(
            models.Alert.severity,
            self.db.func.count(models.Alert.id)
        ).filter(models.Alert.status == models.AlertStatus.ACTIVE)\
         .group_by(models.Alert.severity).all()
        
        stats = {
            "sensors": {status: count for status, count in sensor_stats},
            "alerts": {severity.value: count for severity, count in alert_stats},
            "connections": manager.get_connection_stats(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await manager.send_personal_message({
            "type": "system_stats_response",
            "data": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _send_analytics(self, websocket: WebSocket, parameters: dict):
        """Send analytics data"""
        metric_type = parameters.get("metric_type")
        time_range = parameters.get("time_range", "24h")
        
        # Calculate time range
        now = datetime.now(timezone.utc)
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(hours=24)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(hours=24)
        
        # Query metrics
        query = self.db.query(models.Metric).filter(
            models.Metric.ts >= start_time
        )
        
        if metric_type:
            query = query.filter(models.Metric.metric_type == metric_type)
        
        metrics = query.order_by(models.Metric.ts.desc()).all()
        
        # Group by time intervals
        time_series = {}
        for metric in metrics:
            time_key = metric.ts.strftime("%Y-%m-%d %H:00:00")
            if time_key not in time_series:
                time_series[time_key] = []
            time_series[time_key].append(metric.value)
        
        # Calculate averages
        analytics_data = []
        for time_key, values in time_series.items():
            analytics_data.append({
                "timestamp": time_key,
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            })
        
        await manager.send_personal_message({
            "type": "analytics_response",
            "data": {
                "metric_type": metric_type,
                "time_range": time_range,
                "time_series": sorted(analytics_data, key=lambda x: x["timestamp"])
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

# Real-time alert broadcaster
async def broadcast_new_alert(alert: models.Alert):
    """Broadcast new alert to all connected clients"""
    alert_data = {
        "type": "new_alert",
        "alert": {
            "id": alert.id,
            "alert_id": alert.alert_id,
            "sensor_id": alert.sensor_id,
            "sensor_name": alert.sensor.name if alert.sensor else None,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "created_at": alert.created_at.isoformat(),
            "location": {
                "lat": alert.location_lat,
                "lng": alert.location_lng,
                "address": alert.location_address
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await manager.broadcast(alert_data)
    
    # Send to specific roles based on alert category
    if alert.category == "traffic":
        await manager.send_to_role(alert_data, "traffic_control")
    elif alert.category == "environment":
        await manager.send_to_role(alert_data, "environment_officer")
    elif alert.category == "utility":
        await manager.send_to_role(alert_data, "utility_officer")

# Real-time sensor data broadcaster
async def broadcast_sensor_update(metric: models.Metric):
    """Broadcast sensor data update"""
    update_data = {
        "type": "sensor_update",
        "sensor_id": metric.sensor_id,
        "metric_type": metric.metric_type,
        "value": metric.value,
        "timestamp": metric.ts.isoformat(),
        "sensor_name": metric.sensor.name if metric.sensor else None
    }
    
    # Broadcast to subscribers of sensor updates
    await manager.send_to_channel(update_data, "sensor_updates")
    await manager.send_to_channel(update_data, f"sensor_{metric.sensor_id}")

# System health broadcaster
async def broadcast_system_health():
    """Broadcast system health status periodically"""
    health_data = {
        "type": "system_health",
        "status": "healthy",
        "uptime": "99.9%",
        "active_sensors": 45,
        "total_sensors": 50,
        "active_alerts": 12,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await manager.broadcast(health_data)
handle_subscribe(self, websocket: WebSocket, message: dict):
        """Handle channel subscription"""
        channels = message.get("channels", [])
        for channel in channels:
            manager.subscribe_to_channel(websocket, channel)
        
        await manager.send_personal_message({
            "type": "subscription_confirmed",
            "channels": channels,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)

    async def _