from typing import Optional, Tuple

THRESHOLDS = {
    "air_quality_pm25": {"warning": 50, "critical": 100},
    "traffic_congestion": {"warning": 60, "critical": 85},
    "waste_level": {"warning": 70, "critical": 90},
    "energy_usage": {"warning": 800, "critical": 1200},
}

def evaluate(metric_type: str, value: float) -> Optional[Tuple[str, str]]:
    cfg = THRESHOLDS.get(metric_type)
    if not cfg:
        return None
    if value >= cfg["critical"]:
        return ("critical", f"{metric_type} CRITICAL at {value}")
    if value >= cfg["warning"]:
        return ("warning", f"{metric_type} elevated at {value}")
    return None
