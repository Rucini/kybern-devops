import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify

from config import Config
from app.extensions import db, jwt, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.tickets.routes import tickets_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/api/main')
    app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Configure Logging
    configure_logging(app)

    # Error Handlers
    register_error_handlers(app)

    app.logger.info('Helpdesk API startup')

    return app


def configure_logging(app):
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Helpdesk API startup')


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return jsonify({"error": "Internal Server Error"}), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning('File upload too large')
        return jsonify({"error": "File too large. Maximum size is 5MB."}), 413

    # Handle JWT errors
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"error": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired_token_response(header, payload):
        return jsonify({"error": "Token has expired"}), 401

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    from app.models import User
    return User.query.filter_by(id=identity).one_or_none()
