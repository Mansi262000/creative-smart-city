import os, json, threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from .db import SessionLocal
from . import models
from .services import rules, notifier

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = "sensors/+/metrics"

def _handle_message(payload: bytes):
    data = json.loads(payload.decode("utf-8"))
    sensor_id = int(data["sensor_id"])
    metric_type = data["metric_type"]
    value = float(data["value"])
    ts_str = data.get("ts")
    if ts_str:
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z","+00:00"))
        except Exception:
            ts = datetime.now(timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    db: Session = SessionLocal()
    try:
        m = models.Metric(sensor_id=sensor_id, metric_type=metric_type, value=value, ts=ts)
        db.add(m)
        db.commit()
        db.refresh(m)

        res = rules.evaluate(metric_type, value)
        if res:
            severity, message = res
            alert = models.Alert(sensor_id=sensor_id, metric_type=metric_type, severity=severity, message=message)
            db.add(alert)
            db.commit()
            notifier.notify(severity, message)
    finally:
        db.close()

def _on_connect(client, userdata, flags, reason_code, properties=None):
    print("[MQTT] Connected:", reason_code)
    client.subscribe(TOPIC)

def _on_message(client, userdata, msg):
    try:
        _handle_message(msg.payload)
    except Exception as e:
        print("[MQTT] Error:", e)

def start_mqtt_background():
    def run():
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = _on_connect
        client.on_message = _on_message
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_forever()
    t = threading.Thread(target=run, daemon=True)
    t.start()
