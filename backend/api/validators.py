import datetime as dt

from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Валидатор имени пользователя.

    Проверяет, что имя пользователя не является 'user'.

    Аргументы:
    - value: значение имени пользователя

    Выбрасывает исключение ValidationError, если имя пользователя равно 'user'.
    """
    if value.lower() == 'user':
        raise ValidationError(
            ('Имя пользователя не может быть "user"'),
            params={'value': value},
        )


def validate_year(value):
    """
    Валидатор года.

    Проверяет, что указанный год не превышает текущий год.

    Аргументы:
    - value: значение года

    Выбрасывает исключение ValidationError, если год больше текущего года.
    """
    year = dt.date.today().year
    if not (value <= year):
        raise ValidationError('Дата указана некорректно')
    return value


def validate_ingredients(self, value):
    """
    Валидатор ингредиентов.

    Проверяет, что список ингредиентов не пуст и
    что все количества ингредиентов больше 0.

    Аргументы:
    - value: список ингредиентов

    Выбрасывает исключение ValidationError, если список ингредиентов пуст или
    содержит некорректные количества.

    Возвращает:
    Список ингредиентов.

    Пример использования:
    validate_ingredients(self, value)
    """
    if not value:
        raise ValidationError('Добавьте ингредиенты')
    for amount in value:
        if amount['amount'] <= 0:
            raise ValidationError(
                'Количество ингредиентов должно быть больше 0')
    return value
