"""Application factory for the NL-to-SQL Flask app."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "data/advanced_nlsql.db"
UPLOAD_FOLDER = "data/uploads"


def create_app(db_path: str = None) -> Flask:
    """Build and return a fully-configured Flask application.

    Services are initialised once at startup and stored on
    ``app.config["SERVICES"]`` so blueprints can access them
    via ``current_app``.
    """
    load_dotenv()

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "static"),
    )
    CORS(app)

    # ---- Configuration ---------------------------------------------------
    app.config["DEFAULT_DB_PATH"] = DEFAULT_DB_PATH
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["CURRENT_DB_NAME"] = "Default Database"

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # ---- Logging ---------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/nlsql_system.log"),
            logging.StreamHandler(),
        ],
    )

    # ---- Services --------------------------------------------------------
    from backend.services.database import DatabaseService
    from backend.services.sql_generator import SQLGeneratorService
    from backend.services.visualizer import VisualizationEngine
    from backend.services.export_service import ExportService

    db_svc = DatabaseService(db_path or os.getenv("DB_PATH", DEFAULT_DB_PATH))
    gen_svc = SQLGeneratorService()
    viz_svc = VisualizationEngine()
    exp_svc = ExportService()

    # Similarity is optional (heavy deps)
    sim_svc = None
    try:
        from backend.services.similarity import SimilarityService
        sim_svc = SimilarityService()
    except Exception as exc:
        logger.info("Similarity features disabled: %s", exc)

    app.config["SERVICES"] = {
        "db": db_svc,
        "generator": gen_svc,
        "similarity": sim_svc,
        "viz": viz_svc,
        "export": exp_svc,
    }

    # ---- Blueprints ------------------------------------------------------
    from backend.routes.query_routes import query_bp
    from backend.routes.similarity_routes import similarity_bp
    from backend.routes.db_routes import db_bp
    from backend.routes.export_routes import export_bp

    app.register_blueprint(query_bp)
    app.register_blueprint(similarity_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(export_bp)

    # ---- Root route ------------------------------------------------------
    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    logger.info("Application created successfully")
    return app
