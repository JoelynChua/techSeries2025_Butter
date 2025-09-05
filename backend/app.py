from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import os

from config import Settings
from routes import register_blueprints

def create_app():
    # Load env early so config/env reads work
    load_dotenv()

    app = Flask(__name__)

    # Basic config
    app.config["SWAGGER"] = Settings.SWAGGER

    # CORS
    CORS(app, resources={r"/*": {"origins": [Settings.FRONTEND_ORIGIN]}})

    # Swagger
    Swagger(app)

    # Blueprints
    register_blueprints(app)

    @app.get("/health")
    def health():
        return {"ok": True}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)