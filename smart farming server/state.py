import time
from collections import deque
from config import SENSOR_KEYS, MAX_HISTORY

# ===== Sensor & relay realtime state =====
sensor_data = {k: None for k in SENSOR_KEYS}
sensor_timestamp = {k: "-" for k in SENSOR_KEYS}

relay_state = {1: "OFF", 2: "OFF", 3: "OFF"}
control_mode = {"mode": "manual"}  # "manual" / "auto"

# ===== ML state =====
model = None
tree_rules_text = ""
model_acc = 0.0

decision_info = {
    "ready": False,
    "updated_at": None,
    "pots": {
        "pot_1": {"features": None, "prediction": None, "status": None, "proba": None, "actual": None},
        "pot_2": {"features": None, "prediction": None, "status": None, "proba": None, "actual": None},
        "pot_3": {"features": None, "prediction": None, "status": None, "proba": None, "actual": None},
    }
}

# ===== Realtime history chart =====
history = {
    "time": deque(maxlen=MAX_HISTORY),
    "soil_1": deque(maxlen=MAX_HISTORY),
    "soil_2": deque(maxlen=MAX_HISTORY),
    "soil_3": deque(maxlen=MAX_HISTORY),
    "actual_1": deque(maxlen=MAX_HISTORY),
    "actual_2": deque(maxlen=MAX_HISTORY),
    "actual_3": deque(maxlen=MAX_HISTORY),
    "pred_1": deque(maxlen=MAX_HISTORY),
    "pred_2": deque(maxlen=MAX_HISTORY),
    "pred_3": deque(maxlen=MAX_HISTORY),
    "acc": deque(maxlen=MAX_HISTORY),
}

correct_count = 0
total_count = 0

START_TS = time.time()

# ===== YOLO state =====
yolo_state = {
    "updated_at": None,
    "image_url": None,
    "summary": {},
    "top": None,
}

# ===== MQTT client holder =====
mqtt_client = None
