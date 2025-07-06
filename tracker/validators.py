import re

from rest_framework.exceptions import ValidationError


class NameValidator:
    """Валидатор для проверки имен, фамилий и отчеств."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        for field_name in self.field:
            field_value = value.get(field_name)
            if field_value is None or field_value == "":
                continue

            if not re.match(r"^[А-ЯЁA-Z][а-яёa-z]*$", field_value):
                raise ValidationError(f"{field_name} должно начинаться с заглавной буквы и содержать только буквы.")
