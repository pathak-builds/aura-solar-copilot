import json
from tools.solar_tools import calculate_tilt_anomaly, calculate_power_loss

def test_tilt_anomaly_normal():
    result = json.loads(calculate_tilt_anomaly(16.5))
    assert result["status"] == "NORMAL"
    assert result["deviation_deg"] == 1.5

def test_power_loss():
    result = json.loads(calculate_power_loss(100, 88))
    assert result["loss_percent"] == 12.0
    assert result["severity"] == "HIGH"