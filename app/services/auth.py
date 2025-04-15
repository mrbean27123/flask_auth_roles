from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from app.models.user import User


class AuthService:
    @staticmethod
    def login(email: str, password: str) -> bool:
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return True
        return False

    @staticmethod
    def logout():
        logout_user()