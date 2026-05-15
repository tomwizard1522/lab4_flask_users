import re
from flask import flash


class UserValidator:
    """Класс для валидации данных пользователя"""

    # Допустимые символы для пароля
    PASSWORD_SPECIAL_CHARS = "~!?@#$%^&*_-+()[]{}></\\|\"'.,:;"

    @staticmethod
    def validate_username(username):
        """
        Проверка логина:
        - только латинские буквы и цифры
        - длина не менее 5 символов
        """
        errors = []

        if not username:
            errors.append("Логин не может быть пустым")
        elif len(username) < 5:
            errors.append("Логин должен содержать не менее 5 символов")
        elif not re.match(r'^[a-zA-Z0-9]+$', username):
            errors.append("Логин может содержать только латинские буквы и цифры")

        return len(errors) == 0, errors

    @staticmethod
    def validate_password(password, confirm_password=None):
        """
        Проверка пароля:
        - не менее 8 символов
        - не более 128 символов
        - минимум одна заглавная и одна строчная буква
        - только латинские или кириллические буквы
        - минимум одна цифра (арабские)
        - без пробелов
        - допустимые спецсимволы
        """
        errors = []

        if not password:
            errors.append("Пароль не может быть пустым")
            return False, errors

        if len(password) < 8:
            errors.append("Пароль должен содержать не менее 8 символов")
        if len(password) > 128:
            errors.append("Пароль не должен превышать 128 символов")

        if ' ' in password:
            errors.append("Пароль не должен содержать пробелов")

        # Проверка наличия заглавных и строчных букв
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)

        if not has_upper:
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")
        if not has_lower:
            errors.append("Пароль должен содержать хотя бы одну строчную букву")

        # Проверка наличия цифр
        has_digit = any(c.isdigit() for c in password)
        if not has_digit:
            errors.append("Пароль должен содержать хотя бы одну цифру")

        # Проверка допустимых символов
        allowed_pattern = r'^[a-zA-Zа-яА-ЯёЁ0-9' + re.escape(UserValidator.PASSWORD_SPECIAL_CHARS) + r']+$'
        if not re.match(allowed_pattern, password):
            errors.append("Пароль содержит недопустимые символы")

        # Проверка совпадения паролей
        if confirm_password is not None and password != confirm_password:
            errors.append("Пароли не совпадают")

        return len(errors) == 0, errors

    @staticmethod
    def validate_required_fields(data, fields):
        """Проверка обязательных полей"""
        errors = {}
        for field in fields:
            if not data.get(field):
                errors[field] = f"Поле '{field}' не может быть пустым"
        return errors