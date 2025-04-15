from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    NotNullViolation,
)
from psycopg2.errors import StringDataRightTruncation
import re


class DBErrorParser:
    @classmethod
    def get_message_model_view(cls, exception, model, kwargs):
        # Если ошибка связана с превышением длины, попробуем извлечь информацию о поле
        orig_error = getattr(exception, 'orig', None)
        if orig_error and isinstance(orig_error, StringDataRightTruncation):
            field, limit = DBErrorParser.extract_length_info(str(orig_error))
            # Если в сообщении не нашлось поля, пробуем искать его по переданным данным
            if not field:
                field, limit = DBErrorParser.find_overflowed_field(model, kwargs)
            if field:
                return f'The value in the "{field}" field exceeds the allowed length ({limit} characters).'
            else:
                return f'One of the fields exceeds the allowed length ({limit} characters).'
        return DBErrorParser.parse_db_error(exception)

    @classmethod
    def parse_db_error(cls, error: Exception) -> str:
        """
        Обрабатывает ошибку SQLAlchemy/psycopg2 и возвращает понятное сообщение.
        """
        orig = getattr(error, 'orig', None)
        msg = str(orig) if orig else str(error)

        # Нарушение уникальности
        if isinstance(orig, UniqueViolation):
            field = cls._extract_unique_field(msg)
            return f'The "{field}" field must be unique.' if field else "Unique constraint violated."

        # Значение NULL для NOT NULL
        if isinstance(orig, NotNullViolation):
            field = cls._extract_not_null_field(msg)
            return f'The "{field}" field is required.' if field else "A required field is missing."

        # Нарушение внешнего ключа
        if isinstance(orig, ForeignKeyViolation):
            return "Foreign key constraint violated - please check related records."

        # Общие ошибки целостности и данных
        if isinstance(error, IntegrityError):
            return "Data integrity error (possibly due to foreign keys or duplicates)."
        if isinstance(error, DataError):
            return f"Invalid format or data value too long."

        return f"Unknown error while adding data. {msg}"


    @staticmethod
    def _extract_unique_field(msg: str) -> str:
        """
        Ищет имя поля в сообщении об ошибке уникальности.
        Пример: 'Key (email)=(test@example.com) already exists'
        """
        match = re.search(r'Key \("?(\w+)"?\)=', msg)
        return match.group(1) if match else ""


    @staticmethod
    def _extract_not_null_field(msg: str) -> str:
        """
        Ищет имя поля в сообщении об ошибке NOT NULL.
        Пример: 'null value in column "username" violates not-null constraint'
        """
        match = re.search(r'null value in column "(.*?)"', msg)
        return match.group(1) if match else ""


    @staticmethod
    def extract_length_info(msg: str) -> tuple[str, str]:
        """
        Извлекает имя поля (если есть) и максимальную длину.
        Пример сообщения:
          'value too long for type character varying(6)'
        или
          'column "access_level" value too long for type character varying(6)'
        """
        field_match = re.search(r'column "?(\w+)"?', msg)
        length_match = re.search(r'character varying\((\d+)\)', msg)

        field = field_match.group(1) if field_match else ""
        limit = length_match.group(1) if length_match else "unknown"
        return field, limit


    @classmethod
    def find_overflowed_field(cls, model, kwargs) -> tuple[str, str]:
        """
        Перебирает колонки модели и ищет ту, значение которой, присутствующее в kwargs,
        превышает допустимую длину.
        """
        for column in model.__table__.columns:
            if hasattr(column.type, 'length') and column.name in kwargs:
                max_len = column.type.length
                if max_len and isinstance(kwargs[column.name], str):
                    if len(kwargs[column.name]) > max_len:
                        return column.name, str(max_len)
        return "", "unknown"