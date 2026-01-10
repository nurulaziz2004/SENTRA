import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import state
from config import DATASET_PATH, FEATURES, TARGET, LABEL_MAP, STATIC_DIR, THRESH_SOIL_NEED_WATER
from utils import now_hms

def heuristic_actual_label(soil_percent: float):
    if soil_percent is None:
        return None
    return 1 if soil_percent <= THRESH_SOIL_NEED_WATER else 0

def train_model():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    for col in FEATURES + [TARGET]:
        if col not in df.columns:
            raise ValueError(f"Kolom '{col}' tidak ada. Kolom tersedia: {list(df.columns)}")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y if len(set(y)) > 1 else None
    )

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print("[ML] Model Accuracy (test):", round(acc, 4))

    # save tree image to static/tree.png
    plt.figure(figsize=(14, 7))
    plot_tree(model, feature_names=FEATURES, filled=True, rounded=True,
              class_names=["Tidak Siram", "Siram"])
    plt.savefig(os.path.join(STATIC_DIR, "tree.png"), dpi=150)
    plt.close()

    rules_text = export_text(model, feature_names=FEATURES)
    return model, rules_text, float(acc)

def init_ml():
    model, rules, acc = train_model()
    state.model = model
    state.tree_rules_text = rules
    state.model_acc = acc

def collect_features_per_pot():
    suhu = state.sensor_data.get("suhu")
    hum  = state.sensor_data.get("kelembaban")
    ldr  = state.sensor_data.get("ldr")

    pots = {}
    for i in range(1, 4):
        s1 = state.sensor_data.get(f"kelembaban_tanah_{i}A")
        s2 = state.sensor_data.get(f"kelembaban_tanah_{i}B")
        if None in (s1, s2, suhu, hum, ldr):
            return None

        soil_avg = (s1 + s2) / 2.0
        pots[f"pot_{i}"] = {
            "suhu": float(suhu),
            "kelembaban": float(hum),
            "kelembaban_tanah": float(soil_avg),
            "intensitas_cahaya": float(ldr),
        }
    return pots

def maybe_infer_and_update(publish_relay_fn=None):
    """
    Dipanggil setiap sensor masuk. Jika data lengkap -> infer + update state + history.
    Jika mode AUTO -> kontrol relay (butuh publish_relay_fn).
    """
    if state.model is None:
        return

    pots = collect_features_per_pot()
    if not pots:
        return

    t = now_hms()

    preds = {}
    actuals = {}

    for i in range(1, 4):
        pkey = f"pot_{i}"
        feats = pots[pkey]

        arr = np.array([feats[k] for k in FEATURES], dtype=float).reshape(1, -1)
        pred = int(state.model.predict(arr)[0])
        proba = state.model.predict_proba(arr)[0].tolist()

        actual = heuristic_actual_label(feats["kelembaban_tanah"])
        if actual is None:
            actual = pred

        preds[i] = pred
        actuals[i] = int(actual)

        state.decision_info["pots"][pkey] = {
            "features": feats,
            "prediction": pred,
            "status": LABEL_MAP[pred],
            "proba": proba,
            "actual": int(actual),
        }

    state.decision_info["ready"] = True
    state.decision_info["updated_at"] = t

    for i in (1, 2, 3):
        state.total_count += 1
        if preds[i] == actuals[i]:
            state.correct_count += 1

    acc_rt = round((state.correct_count / state.total_count) * 100, 2) if state.total_count else 0.0

    # history
    state.history["time"].append(t)
    state.history["soil_1"].append(float(pots["pot_1"]["kelembaban_tanah"]))
    state.history["soil_2"].append(float(pots["pot_2"]["kelembaban_tanah"]))
    state.history["soil_3"].append(float(pots["pot_3"]["kelembaban_tanah"]))

    state.history["actual_1"].append(int(actuals[1]))
    state.history["actual_2"].append(int(actuals[2]))
    state.history["actual_3"].append(int(actuals[3]))

    state.history["pred_1"].append(int(preds[1]))
    state.history["pred_2"].append(int(preds[2]))
    state.history["pred_3"].append(int(preds[3]))

    state.history["acc"].append(float(acc_rt))

    # AUTO relay control
    if state.control_mode["mode"] == "auto" and publish_relay_fn is not None:
        for i in (1, 2, 3):
            publish_relay_fn(i, "ON" if preds[i] == 1 else "OFF")
