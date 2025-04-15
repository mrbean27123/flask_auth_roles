import click
from click import Command
from flask.cli import with_appcontext
from app.core.init_roles import init_roles


@click.command("init-roles")
@with_appcontext
def _init_roles_command():
    """Создает или обновляет администратора."""
    init_roles()
    click.echo("Необходимые роли созданы")

init_roles_command: Command = _init_roles_command