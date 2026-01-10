# SENTRA – Smart Farming Server

Backend server for smart farming system using Python and Flask.

## Features
- REST API for smart farming data
- MQTT communication using paho-mqtt
- Machine learning processing (scikit-learn)
- Computer vision using YOLO (Ultralytics)

## Tech Stack
- Python
- Flask
- Gunicorn
- MQTT (paho-mqtt)
- Scikit-learn
- Ultralytics YOLO

## Deployment
This application is deployed on Koyeb using:
- Procfile
- Gunicorn
- Environment-based PORT configuration

## Run Locally
```bash
pip install -r requirements.txt
python smart_farming_server/app.py
