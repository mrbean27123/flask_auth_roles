from flask import Blueprint, request, render_template, redirect, flash
from app.services.auth import AuthService
from app.services.flash_error import FlashError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', endpoint='login', methods=['GET', 'POST'])
def login():
    data = {
        'title': 'Auth',
        'request_data': None
    }

    if request.method == 'POST':
        request_data = request.form.to_dict()
        data['request_data'] = request_data

        # Если данные не верные
        if not AuthService.login(**request_data):
            flash("Incorrect credentials!", FlashError.DANGER)
            return render_template('auth.html', data=data)

        return redirect('/')

    return render_template('auth.html', data=data)

@auth_bp.route('/logout', endpoint='logout')
def logout():
    AuthService.logout()
    return redirect('/')