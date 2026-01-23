from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'core.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Import and Register Routes
    from app.routes.core import core_bp
    app.register_blueprint(core_bp)
    
    # Auto-create tables if they don't exist
    with app.app_context():
        from app.database.models import Project, Deployment, User
        db.create_all()
        
    return app
