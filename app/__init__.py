from flask import Flask

from app.core.config import Config
from app.core.extensions import db, migrate, login_manager
from app.cli.commands.init_admin import init_admin_command
from app.cli.commands.init_roles import init_roles_command

from app.api.v1.main.routes import main_bp
from app.api.v1.auth.routes import auth_bp
from app.api.v1.admin.routes import admin_bp
from app.api.v1.model_view.routes import model_view_bp

def create_app(config_class = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Миграции
    from app.models import user, role, user_role

    # Авторизация
    login_manager.init_app(app)

    # Регистрация маршрутов
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(model_view_bp)

    # Регистрируем CLI-команды
    app.cli.add_command(init_admin_command)
    app.cli.add_command(init_roles_command)

    return app