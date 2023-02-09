import re

from django.core.exceptions import ValidationError


def validate_referal(value):
    """Валидация реферального кода"""
    # длина строки должна быть менее пяти символов
    if len(value) < 5:
        raise ValidationError(f'Длина "{value}" менее пяти символов.')
    # строка должна состоять из латинских букв и цифр, регистр не важен
    pattern = re.compile(r'[A-Za-z0-9]*')
    if pattern.fullmatch(value) is None:
        raise ValidationError(f'Промокод "{value}" состоит не только из латинских букв и цифр.')
    # занятые промо '12345', 'halyava'
    if value in ['12345', 'halyava']:
        raise ValidationError(f'Промокод "{value}" уже занят.')
    # не должно быть содержания следующих слов
    words = ('durak', 'money', 'credit', 'monet', 'free', '2021', '2020')
    for word in words:
        if word in value:
            raise ValidationError(f'Промокод "{value}" не должен содержать подстроку "{word}".')
