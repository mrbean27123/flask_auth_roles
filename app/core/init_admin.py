from app.models.user import User
from app.models.user_role import UserRole, AccessLevel
from app.models.role import Role
from app import db
from app.services.user import UserService


def init_admin(email: str, password: str):
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        # Создаем пользователя администратора
        UserService.add_user(username="admin", email=email, password=password)
        admin_user = User.query.filter_by(username="admin").first()

    # Если нет роли admin добавляем её и присваиваем
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Access to Admin panel, for create/update/delete users")
        db.session.add(admin_role)
        db.session.flush()

    admin_access = UserRole.query.filter_by(role_id=admin_role.id).first()
    if not admin_access:
        admin_access = UserRole(user_id=admin_user.id, role_id=admin_role.id, access_level=AccessLevel.admin)
        db.session.add(admin_access)

    db.session.commit()