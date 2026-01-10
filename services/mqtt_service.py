import paho.mqtt.client as mqtt

import state
from config import BROKER, PORT, RELAY_TOPICS, sensor_topics
from utils import safe_float, now_hms
from services.decisiontree_service import maybe_infer_and_update

def publish_relay(rid: int, relay_state_value: str):
    """
    Publish relay ON/OFF and update state.relay_state.
    """
    if state.mqtt_client is None:
        return

    val = "ON" if str(relay_state_value).upper().strip() == "ON" else "OFF"
    topic = RELAY_TOPICS[rid]
    state.mqtt_client.publish(topic, val)
    state.relay_state[rid] = val

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected rc=", rc)
    for t in sensor_topics + list(RELAY_TOPICS.values()):
        client.subscribe(t)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore").strip()
    key = topic.split("/")[-1]

    # relay feedback topic
    for rid, rtopic in RELAY_TOPICS.items():
        if topic == rtopic:
            state.relay_state[rid] = payload.strip().upper()
            return

    # sensor update
    if key in state.sensor_data:
        val = safe_float(payload)
        if val is not None:
            state.sensor_data[key] = val
            state.sensor_timestamp[key] = now_hms()

        # update inference + history + optional auto relay
        maybe_infer_and_update(publish_relay_fn=publish_relay)

def init_mqtt():
    client = mqtt.Client(
        client_id="SMARTFARM_FINAL",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
        protocol=mqtt.MQTTv311
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    state.mqtt_client = client
    print("[MQTT] loop started")
