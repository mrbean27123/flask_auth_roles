from app.models.role import Role
from app.api.v1.model_view.routes import MODELS
from app import db


def init_roles():
    """
    Добавляет все существующие роли в таблицу
    :return:
    """
    existing_roles = {role.name for role in Role.query.all()}

    new_roles = []
    for model_name in MODELS:
        if model_name not in existing_roles:
            new_roles.append(Role(name=model_name, description=f"Access to table: {model_name}"))

    if new_roles:
        db.session.add_all(new_roles)
        db.session.commit()