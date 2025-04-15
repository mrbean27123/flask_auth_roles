from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash

from app.services.user import UserService
from app.services.flash_error import FlashError

main_bp = Blueprint('main', __name__)


@main_bp.route('/', endpoint='main')
@login_required
def main():
    data = {
        "title": "Main page"
    }
    return render_template('main.html', data=data)


@main_bp.route('/profile', endpoint='profile', methods=['GET', 'POST'])
@login_required
def profile():
    data = {
        "title": f"Profile {current_user.username}",
    }

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Проверка текущего пароля
        if not check_password_hash(current_user.password, current_password):
            flash('Current password not correct', FlashError.WARNING)

        # Проверка совпадения нового пароля с подтверждением
        if new_password != confirm_password:
            flash('Passwords do not match', FlashError.WARNING)

        # Попытка изменить пароль
        if not UserService.change_password(user_id=current_user.id, new_password=new_password):
            flash('Error', FlashError.DANGER)

        return redirect(url_for('main.profile'))
    return render_template('profile.html', data=data)