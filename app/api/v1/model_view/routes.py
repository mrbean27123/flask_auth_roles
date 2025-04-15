from flask import Blueprint, render_template, redirect, flash, request, url_for
from flask_login import login_required
from app import db
from sqlalchemy import String, func

from app.services.flash_error import FlashError
from app.services.role_access import RoleAccess, AccessLevel
from app.models import role, user_role, user
from app.services.model_view import ModelViewService

model_view_bp = Blueprint('model_view', __name__)

MODELS = {
    "user_roles": user_role.UserRole,
    "roles": role.Role,
    "users": user.User,
}


# Models page
@model_view_bp.route('/models', endpoint='models')
@login_required
def models():
    data = {
        "title": "Tables",
        "models": MODELS,
    }
    return render_template('model_view/models.html', data=data)


# Models data page
@model_view_bp.route('/models/<string:model_name>', endpoint='models_get', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name=lambda **kwargs: kwargs["model_name"], min_level=AccessLevel.viewer)
def model_view(model_name):
    model = MODELS[model_name]
    model_data = model.query.order_by(model.id.asc()).all()
    data = {
        "title": model_name,
        "columns": model.__table__.columns,
        "columns_blocked": [],
        "model_data": model_data,
        "filter_data": None
    }
    if request.method == 'POST':
        data['filter_data'] = request.form.to_dict()
        query = db.session.query(model)

        for field, value in request.form.items():
            column = getattr(model, field, None)
            if column is not None:
                query = query.filter(func.cast(column, String).ilike(f"%{value}%"))
        data["model_data"] = query.order_by(model.id.asc()).all()

    return render_template('model_view/model.html', data=data)


# Models add page
@model_view_bp.route('/models/<string:model_name>/add', endpoint='models_add', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name=lambda **kwargs: kwargs["model_name"], min_level=AccessLevel.editor)
def model_add(model_name):
    model = MODELS[model_name]
    data = {
        "title": model_name,
        "columns": model.__table__.columns
    }
    if request.method == 'POST':
        result_data = request.form.to_dict()
        error_message = ModelViewService.add_to_model(model=model, **result_data)
        if error_message:
            flash(error_message, FlashError.DANGER)
            return redirect(url_for('model_view.models_add', model_name=model_name))

        flash(f"Success",  FlashError.SUCCESS)
        return redirect(url_for('model_view.models_add', model_name=model_name))

    return render_template('model_view/model_add.html', data=data)


# Models edit page
@model_view_bp.route('/models/<string:model_name>/<int:model_id>/edit', endpoint='models_edit', methods=['GET', 'POST'])
@login_required
@RoleAccess.role_required(role_name=lambda **kwargs: kwargs["model_name"], min_level=AccessLevel.editor)
def model_edit(model_name, model_id):
    model = MODELS[model_name]
    model_data = model.query.get(model_id)
    data = {
        "title": model_name,
        "columns": model.__table__.columns,
        "model_data": model_data
    }
    if request.method == 'POST':
        result_data = request.form.to_dict()
        error_message = ModelViewService.edit_model(model=model, model_data=model_data, **result_data)
        if error_message:
            flash(error_message, FlashError.DANGER)
            return redirect(url_for('model_view.models_edit', model_name=model_name, model_id=model_id))

        return redirect(url_for('model_view.models_get', model_name=model_name))

    return render_template('model_view/model_add.html', data=data)


# Models remove page
@model_view_bp.route('/models/<string:model_name>/<int:model_id>/delete', endpoint='models_delete')
@login_required
@RoleAccess.role_required(role_name=lambda **kwargs: kwargs["model_name"], min_level=AccessLevel.editor)
def model_delete(model_name, model_id):
    model = MODELS[model_name]

    # Попытка удалить юзера
    error_message = ModelViewService.delete_model(model=model, model_id=model_id)
    if error_message:
        flash(error_message, FlashError.DANGER)

    return redirect(url_for('model_view.models_get', model_name=model_name))