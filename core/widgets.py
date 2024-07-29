from typing import Any

from django import forms
from django.core.serializers.json import DjangoJSONEncoder


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        # if isinstance(obj, CustomType):
        #     return str(obj)
        return super().default(obj)


json_encorder = LazyEncoder().encode


class LitePickerDateInput(forms.DateInput):
    template_name = "litepicker/widget.html"

    def __init__(self, attrs=None, config=None, format=None):
        super().__init__(attrs=attrs, format=format)
        self.config = config or {}
        self.config.update({"lang": "zh-TW"})

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["litepicker"] = json_encorder(self.config)
        return context


class Bootstrap5TagsSelectMultiple(forms.SelectMultiple):
    template_name = "bootstrap5-tags/widget.html"

    def __init__(self, attrs=None, config=None):
        super().__init__(attrs=attrs)
        self.config = config or {}

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["tags"] = json_encorder(self.config)
        return context


class Bootstrap5TagsSelect(forms.Select):
    template_name = "bootstrap5-tags/widget.html"

    def __init__(self, attrs=None, config=None):
        super().__init__(attrs=attrs)
        self.config = config or {}

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["tags"] = json_encorder(self.config)
        return context
