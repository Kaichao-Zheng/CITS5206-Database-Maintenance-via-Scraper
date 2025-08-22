from flask import Flask
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    # Initialize extensions, blueprints, etc.
    with app.app_context():
        # Import and register blueprints
        from . import main
        app.register_blueprint(main.bp)
    return app