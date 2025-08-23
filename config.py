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

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass
