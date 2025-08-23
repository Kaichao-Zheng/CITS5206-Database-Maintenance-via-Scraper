from flask import Flask
from config import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_login import LoginManager
import os
from werkzeug.security import generate_password_hash

load_dotenv()
db = SQLAlchemy()  
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()
def create_app(config_class=os.environ.get("FLASK_CONFIG") or DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)       
    migrate.init_app(app, db)
    csrf.init_app(app) 
    login.init_app(app)
    login.login_view = 'login'
    
    with app.app_context():
        from . import main
        app.register_blueprint(main.bp)
    return app