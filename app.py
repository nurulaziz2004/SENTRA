from flask import Flask

from services.decisiontree_service import init_ml
from services.yolo_service import init_yolo
from services.mqtt_service import init_mqtt
from web.routes import register_routes

def create_app():
    app = Flask(
        __name__,
        template_folder="web/templates",
        static_folder="static"
    )

    # init subsystems
    init_ml()     # train/load Decision Tree + save tree.png
    init_yolo()   # load YOLO model (yolov8n_selada.pt)
    init_mqtt()   # connect mqtt & loop_start

    register_routes(app)
    return app

if __name__ == "__main__":
    app = create_app()
    print("Open dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
