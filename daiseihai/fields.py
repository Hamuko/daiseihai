import re

from django.db import models
from django import forms
from django.forms.widgets import Input


class ColorWidget(Input):
    input_type = 'color'


class ColorFormField(forms.CharField):
    widget = ColorWidget

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clean(self, value):
        if self.required and not re.match(r'^#[A-Fa-f0-9]+$', value):
            raise forms.ValidationError('Not a color code')
        return value


class ColorField(models.Field):
    widget = ColorWidget
    form_class = ColorFormField

    @staticmethod
    def _to_int(value):
        return int(value[1:], 16)

    def db_type(self, connection):
        return 'integer UNSIGNED'

    def formfield(self, **kwargs):
        defaults = {'form_class': ColorFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        value = hex(value).lstrip('0x').zfill(6)
        return f'#{value}'

    def get_prep_value(self, value):
        if isinstance(value, str):
            value = ColorField._to_int(value)
        return value

    def to_python(self, value) -> str:
        if isinstance(value, str):
            value = ColorField._to_int(value)
        return value
