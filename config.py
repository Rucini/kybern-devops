import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'helpdesk.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Debug
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
