from app.models.user_role import UserRole
from app.models.user import User
from app.models.role import Role
from app.models.user_role import AccessLevel
from app.services.flash_error import FlashError
from functools import wraps
from flask import redirect, request, flash
from flask_login import current_user
from typing import Callable, Union


class RoleAccess:
    """
    Управление доступом по ролям
    """
    # Есть ли доступ у роли к ресурсу
    @staticmethod
    def has_access_to(role_name: str, min_level: AccessLevel = AccessLevel.viewer, user_id: int = None) -> bool:
        # Если айди не указан, то берём текущего пользователя
        if user_id is None:
            user_id = current_user.id
            user = current_user
        else:
            user = User.query.get(user_id)

        # Если пользователя нет, ошибка
        if not user:
            raise ValueError(f"User id:{user_id} not found")

        # Если пользователь админ, то доступ есть
        if user.is_admin:
            return True

        role_exist = (
            UserRole.query
            .join(Role)
            .filter(
                UserRole.user_id == user_id,
                Role.name == role_name,
                UserRole.access_level >= min_level,
            )
            .first()
        )
        return bool(role_exist)

    # Декоратор для ограничения доступа к странице по роли
    @staticmethod
    def role_required(
            role_name: Union[str, Callable[..., str]],
            min_level: AccessLevel = AccessLevel.viewer):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Вычисляем имя роли
                resolved_role_name = role_name(**kwargs) if callable(role_name) else role_name
                if not RoleAccess.has_access_to(role_name=resolved_role_name, min_level=min_level):
                    flash("You don't have the permission to access the requested resource", FlashError.DANGER)
                    return redirect(request.referrer or "/")
                return f(*args, **kwargs)
            return wrapper
        return decorator