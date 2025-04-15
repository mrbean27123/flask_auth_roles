import click
from click import Command
from flask.cli import with_appcontext
from app.core.init_admin import init_admin
from app.core.config import Config


@click.command("init-admin")
@with_appcontext
def _init_admin_command():
    """Создает или обновляет администратора."""
    init_admin(email=Config.ADMIN_EMAIL, password=Config.ADMIN_PASSWORD)
    click.echo("Администратор создан или обновлен")

init_admin_command: Command = _init_admin_command