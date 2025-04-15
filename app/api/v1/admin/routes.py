from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_required, current_user
from app import db
from sqlalchemy import String, func

from app.services.role_access import RoleAccess, AccessLevel
from app.models.user import User
from app.services.user import UserService
from app.services.flash_error import FlashError

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users', endpoint='users', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name="admin", min_level=AccessLevel.admin)
def users_view():
    users = User.query.order_by(User.id.asc()).all()
    data = {
        "title": "Admin users",
        "columns": User.__table__.columns,
        "columns_blocked": ["password"],
        "users": users,
        "filter_data": None,
    }
    if request.method == 'POST':
        data['filter_data'] = request.form.to_dict()
        query = db.session.query(User)

        for field, value in request.form.items():
            column = getattr(User, field, None)
            if column is not None:
                query = query.filter(func.cast(column, String).ilike(f"%{value}%"))
        data["users"] = query.order_by(User.id.asc()).all()

    return render_template('users/users.html', data=data)


@admin_bp.route('/admin/users/<int:user_id>/delete', endpoint='users_delete')
@login_required
@RoleAccess.role_required(role_name="admin", min_level=AccessLevel.admin)
def users_delete(user_id):
    # Проверка если айди текущего пользователя и удаленного совпадают
    if current_user.id == user_id:
        flash('You cannot delete yourself', FlashError.WARNING)

    # Попытка удалить юзера
    if not UserService.delete_user(user_id=user_id):
        flash('Error deleting user', FlashError.DANGER)

    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/add', endpoint='users_add', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name="admin", min_level=AccessLevel.admin)
def users_add():
    data = {
        "title": "Users: Add user",
    }
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        password = UserService.add_user(username=username, email=email)
        if not password:
            flash('Error create user', FlashError.DANGER)
            return redirect(url_for('admin.users_add'))

        flash(f"{email} {password}",  FlashError.SUCCESS)
        return redirect(url_for('admin.users_add'))

    return render_template('users/users_add.html', data=data)


@admin_bp.route('/admin/users/<int:user_id>/edit', endpoint='users_edit', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name="admin", min_level=AccessLevel.admin)
def users_edit(user_id):
    user = User.query.get(user_id)
    data = {
        "title": f"Users: Edit user {user_id}",
        "user": user,
    }
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        user.username = username
        user.email = email

        db.session.commit()

        return redirect(url_for('admin.users'))

    return render_template('users/users_add.html', data=data)