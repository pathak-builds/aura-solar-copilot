"""
Deterministic O&M engineering tools.
Each returns a JSON string.
"""
import json
import math
from datetime import datetime

def calculate_tilt_anomaly(measured_tilt: float, design_tilt: float = 15.0) -> str:
    """Checks deviation from design tilt angle."""
    deviation = abs(measured_tilt - design_tilt)
    if deviation <= 2.0:
        status = "NORMAL"
    elif deviation <= 5.0:
        status = "WARNING"
    else:
        status = "CRITICAL"
    result = {
        "measured_tilt_deg": measured_tilt,
        "design_tilt_deg": design_tilt,
        "deviation_deg": round(deviation, 2),
        "status": status,
        "recommendation": "No action" if status == "NORMAL" else "Inspect mooring tension and anchor position"
    }
    return json.dumps(result)

def calculate_power_loss(rated_power_kw: float, actual_power_kw: float) -> str:
    """Computes percentage power loss."""
    if rated_power_kw <= 0:
        return json.dumps({"error": "Rated power must be positive"})
    loss_percent = ((rated_power_kw - actual_power_kw) / rated_power_kw) * 100
    result = {
        "rated_power_kw": rated_power_kw,
        "actual_power_kw": actual_power_kw,
        "loss_percent": round(loss_percent, 2),
        "severity": "HIGH" if loss_percent > 10 else "NORMAL"
    }
    return json.dumps(result)

def calculate_generation_loss(design_generation_kwh: float, actual_generation_kwh: float) -> str:
    """Daily/monthly generation loss."""
    if design_generation_kwh <= 0:
        return json.dumps({"error": "Design generation must be positive"})
    loss_percent = ((design_generation_kwh - actual_generation_kwh) / design_generation_kwh) * 100
    result = {
        "design_generation_kwh": design_generation_kwh,
        "actual_generation_kwh": actual_generation_kwh,
        "loss_percent": round(loss_percent, 2)
    }
    return json.dumps(result)

def weather_risk(wind_speed_kmh: float, rainfall_mm: float, lightning: bool) -> str:
    """Assesses weather-related risk for field work."""
    risk_level = "LOW"
    reasons = []
    if wind_speed_kmh > 40:
        risk_level = "HIGH"
        reasons.append("High wind speed")
    if rainfall_mm > 10:
        risk_level = "HIGH"
        reasons.append("Heavy rainfall")
    if lightning:
        risk_level = "CRITICAL"
        reasons.append("Lightning alert")
    result = {
        "risk_level": risk_level,
        "safe_for_work": risk_level == "LOW",
        "reasons": reasons
    }
    return json.dumps(result)

def generate_compliance_ticket(equipment_id: str, issue: str, priority: str = "Medium") -> str:
    """Generates a mock compliance/maintenance ticket."""
    ticket = {
        "ticket_id": f"WO-{datetime.now().strftime('%Y%m%d')}-{hash(equipment_id+issue) % 1000:03d}",
        "equipment_id": equipment_id,
        "issue": issue,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }
    return json.dumps(ticket)

def estimate_repair_priority(safety_risk: str, generation_loss_percent: float, spare_available: bool) -> str:
    """Estimates repair urgency."""
    if safety_risk == "high":
        priority = "Critical"
    elif generation_loss_percent > 5:
        priority = "High"
    elif not spare_available:
        priority = "Medium"
    else:
        priority = "Low"
    result = {
        "priority": priority,
        "safety_risk": safety_risk,
        "generation_loss_percent": generation_loss_percent,
        "spare_available": spare_available
    }
    return json.dumps(result)