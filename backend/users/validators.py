import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """
    Проверяет корректность имени.

    Недопустимо имя 'me' и символы отличные от разрешенных.
    """
    if username == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть me.'),
            params={'value': username},
        )
    pattern = r'[\w.@+-]'
    invalid_char = re.sub(pattern, '', username)
    if invalid_char:
        raise ValidationError(f'Некорректное имя пользователя, '
                              'недопустимые символы: '
                              f'{", ".join(set(invalid_char))}')
