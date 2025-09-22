# config.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Base configuration class
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # In-memory database for testing

class ProductionConfig(Config):
    pass