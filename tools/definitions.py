TOOL_DEFINITIONS = [
    {
        "name": "calculate_tilt_anomaly",
        "description": "Compute deviation of a solar panel from design tilt angle.",
        "parameters": {
            "type": "object",
            "properties": {
                "measured_tilt": {"type": "number", "description": "Measured tilt in degrees"},
                "design_tilt": {"type": "number", "description": "Design tilt in degrees (default 15.0)"}
            },
            "required": ["measured_tilt"]
        }
    },
    {
        "name": "calculate_power_loss",
        "description": "Calculate percentage power loss of a string or inverter.",
        "parameters": {
            "type": "object",
            "properties": {
                "rated_power_kw": {"type": "number"},
                "actual_power_kw": {"type": "number"}
            },
            "required": ["rated_power_kw", "actual_power_kw"]
        }
    },
    {
        "name": "calculate_generation_loss",
        "description": "Calculate generation loss in kWh.",
        "parameters": {
            "type": "object",
            "properties": {
                "design_generation_kwh": {"type": "number"},
                "actual_generation_kwh": {"type": "number"}
            },
            "required": ["design_generation_kwh", "actual_generation_kwh"]
        }
    },
    {
        "name": "weather_risk",
        "description": "Assess weather-related risk for field work.",
        "parameters": {
            "type": "object",
            "properties": {
                "wind_speed_kmh": {"type": "number"},
                "rainfall_mm": {"type": "number"},
                "lightning": {"type": "boolean"}
            },
            "required": ["wind_speed_kmh", "rainfall_mm", "lightning"]
        }
    },
    {
        "name": "generate_compliance_ticket",
        "description": "Create a maintenance work order ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "equipment_id": {"type": "string"},
                "issue": {"type": "string"},
                "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]}
            },
            "required": ["equipment_id", "issue"]
        }
    },
    {
        "name": "estimate_repair_priority",
        "description": "Estimate urgency of repair based on safety and loss.",
        "parameters": {
            "type": "object",
            "properties": {
                "safety_risk": {"type": "string", "enum": ["none", "low", "medium", "high"]},
                "generation_loss_percent": {"type": "number"},
                "spare_available": {"type": "boolean"}
            },
            "required": ["safety_risk", "generation_loss_percent", "spare_available"]
        }
    }
]