import os, time, random, json, requests
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
API_URL = os.getenv("API_URL", "http://backend:8000")

SENSORS = [
    {"sensor_id": 1, "metric_type": "air_quality_pm25", "base": 45, "noise": 25},
    {"sensor_id": 2, "metric_type": "traffic_congestion", "base": 40, "noise": 35},
    {"sensor_id": 3, "metric_type": "waste_level", "base": 50, "noise": 40},
    {"sensor_id": 4, "metric_type": "energy_usage", "base": 700, "noise": 500},
]

def publish_mqtt(client, payload):
    topic = f"sensors/{payload['sensor_id']}/metrics"
    client.publish(topic, json.dumps(payload), qos=0)

def publish_http(payload):
    try:
        r = requests.post(f"{API_URL}/metrics/ingest", json=payload, timeout=3)
        print("HTTP ingest:", r.status_code)
    except Exception as e:
        print("HTTP ingest failed:", e)

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    while True:
        for s in SENSORS:
            val = max(0, s["base"] + random.uniform(-s["noise"], s["noise"]))
            payload = {
                "sensor_id": s["sensor_id"],
                "metric_type": s["metric_type"],
                "value": round(val, 2),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            publish_mqtt(client, payload)
            if random.random() < 0.2:
                publish_http(payload)
            print("Published:", payload)
            time.sleep(0.5)
        time.sleep(1)

if __name__ == "__main__":
    main()
