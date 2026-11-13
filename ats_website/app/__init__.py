from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ats-pro-secret-key-2024-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'ats_pro.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
    app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "txt"}
    # Disable CSRF — forms use manual validation (not WTForms)
    app.config["WTF_CSRF_ENABLED"] = False

    # Ensure directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access ATS PRO."
    login_manager.login_message_category = "warning"

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.jobs import jobs_bp
    from app.routes.resumes import resumes_bp
    from app.routes.analysis import analysis_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(resumes_bp, url_prefix="/resumes")
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # Register template filters
    @app.template_filter('enumerate')
    def jinja_enumerate(iterable, start=0):
        return enumerate(iterable, start=start)

    with app.app_context():
        db.create_all()

    return app
