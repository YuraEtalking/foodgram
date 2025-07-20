import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """
    Проверяет корректность имени.

    Недопустимы символы отличные от разрешенных.
    """
    pattern = r'[\w.@+-]'
    invalid_char = re.sub(pattern, '', username)
    if invalid_char:
        raise ValidationError(f'Некорректное имя пользователя, '
                              'недопустимые символы: '
                              f'{", ".join(set(invalid_char))}')
