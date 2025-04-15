from sqlalchemy.exc import IntegrityError, DataError
from typing import Optional

from app import db
from app.services.parce_db_error import DBErrorParser


class ModelViewService:
    @classmethod
    def add_to_model(cls, model: db.Model, **kwargs) -> Optional[str]:
        # Enum-проверка
        enum_error = cls._check_validate_enum(model=model, **kwargs)
        if enum_error:
            return enum_error

        # Если такие данные уже существуют
        data_exist = model.query.filter_by(**kwargs).first()
        if data_exist:
            return f"Data already exist for id: {data_exist.id}"

        try:
            new_data = model(**kwargs)
            db.session.add(new_data)
            db.session.commit()
            return None
        except (IntegrityError, DataError) as e:
            db.session.rollback()
            return DBErrorParser.get_message_model_view(exception=e, model=model, kwargs=kwargs)


    @classmethod
    def edit_model(cls, model: db.Model, model_data, **kwargs) -> Optional[str]:
        # Enum-проверка
        enum_error = cls._check_validate_enum(model=model, **kwargs)
        if enum_error:
            return enum_error

        # Если такие данные уже существуют
        data_exist = model.query.filter_by(**kwargs).first()
        if data_exist:
            return f"Data already exist for id: {data_exist.id}"

        try:
            for key, value in kwargs.items():
                if hasattr(model_data, key):
                    setattr(model_data, key, value)
            db.session.commit()
            return None
        except (IntegrityError, DataError) as e:
            db.session.rollback()
            return DBErrorParser.get_message_model_view(exception=e, model=model, kwargs=kwargs)


    @staticmethod
    def delete_model(model: db.Model, model_id: int) -> Optional[str]:
        try:
            model_data = model.query.get(model_id)
            db.session.delete(model_data)
            db.session.commit()
            return None
        except Exception as e:
            db.session.rollback()
            return str(e)


    @staticmethod
    def _check_validate_enum(model: db.Model, **kwargs) -> Optional[str]:
        # Enum-проверка
        for column in model.__table__.columns:
            if isinstance(column.type, db.Enum):
                enum_class = column.type.enum_class
                value = kwargs.get(column.name)
                if value and value not in enum_class.__members__ and value not in [e.value for e in enum_class]:
                    valid_values = ", ".join(str(e.name) for e in enum_class)
                    return f'Not valid value: "{value}" for field "{column.name}". Valid values: {valid_values}'
        return None