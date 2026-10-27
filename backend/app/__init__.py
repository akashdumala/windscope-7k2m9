
import os
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    allowed_origins = [
        "https://windscope-7k2m9.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
    )

    from app.routes import api
    app.register_blueprint(api, url_prefix="/api")

    return app
