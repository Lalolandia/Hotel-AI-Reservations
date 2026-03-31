# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Por favor inicia sesión para acceder a esta página."
    login_manager.login_message_category = "info"

    # Importar blueprints y registrar
    from app.routes.auth import auth_bp
    from app.routes.main import main

    app.register_blueprint(auth_bp)
    app.register_blueprint(main)

    # Importar modelos para que Alembic los detecte
    with app.app_context():
        from app import models  # models/__init__.py importa cada modelo
        from app import models
        from app.routes.habitacion_routes import habitacion_bp

        app.register_blueprint(habitacion_bp)

    return app