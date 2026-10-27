
import os

from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173",
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    frontend_url,
                    "http://127.0.0.1:5173",
                ]
            }
        },
    )

    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    return app
