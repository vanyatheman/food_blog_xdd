import re

from django.core.exceptions import ValidationError


def username_validator(value):
    regex = r"^[\w.@+-]+\Z"
    if re.search(regex, value) is None:
        invalid_characters = set(re.findall(r"[^\w.@+-]", value))
        raise ValidationError(
            (
                f"Недопустимые символы {invalid_characters} в username. "
                f"username может содержать только буквы, цифры и "
                f"знаки @/./+/-/_."
            ),
        )
    
    if value.lower() == 'me':
        raise ValidationError(
            "Использовать имя 'me' в качестве "
            "username запрещено."
        )
