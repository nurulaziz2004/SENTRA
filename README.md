# Smart Farming AI Server Dashboard (Flask + MQTT + Decision Tree + YOLO)

Server untuk monitoring & kontrol smart farming berbasis:
- ESP32 (sensor + relay)
- MQTT (broker)
- Flask Dashboard (web)
- Decision Tree (prediksi siram/tidak)
- YOLO (deteksi kondisi selada dari capture webcam)

## 1) Struktur Folder

smartfarming_server/
- app.py                -> entrypoint utama (jalankan ini)
- config.py             -> konfigurasi (broker, topic, path dataset, dll)
- state.py              -> state realtime (sensor, history, decision, yolo)
- utils.py              -> helper fungsi
- services/
  - mqtt_service.py     -> koneksi MQTT, subscribe topic, publish relay
  - ml_service.py       -> training & infer Decision Tree + update history
  - yolo_service.py     -> infer YOLO + simpan hasil gambar ke static/yolo/
- web/
  - routes.py           -> endpoint Flask (/sensors, /decision, /yolo_submit, dll)
  - templates/index.html-> dashboard UI
- static/
  - tree.png            -> gambar decision tree hasil training
  - yolo/               -> hasil capture YOLO (auto dibuat)

## 2) Requirements

Python 3.10+ disarankan.

Install dependency:
```bash
pip install -r requirements.txt
