import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template

from config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.tickets.routes import tickets_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Configure Logging
    configure_logging(app)

    # Error Handlers
    register_error_handlers(app)

    app.logger.info('Helpdesk startup')

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
        app.logger.info('Helpdesk startup')


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        # Handle file upload too large
        app.logger.warning('File upload too large')
        return render_template('errors/500.html', error_msg="File too large. Maximum size is 5MB."), 413

@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))
