from typing import Any

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.widgets import HiddenInput, SelectDateWidget
from django_quill.widgets import QuillWidget


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
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

    def __init__(self, attrs=None, config=None, choices=()):
        super().__init__(attrs=attrs, choices=choices)
        self.config = config or {}

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["widget"]["tags"] = json_encorder(self.config)
        return context


class MyQuillWidget(QuillWidget):
    @property
    def media(self):
        js = [
            # quill
            "https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js",
            # custom
            "js/quill/quill.js",
            "js/quill/django_quill.js",
        ]
        css = {
            # build from scss
        }
        return forms.Media(js=js, css=css)


class YearMonthWidget(SelectDateWidget):
    # select_widget = Bootstrap5TagsSelect
    use_fieldset = False
    template_name = "widgets/select_date.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        year_choices = [(i, str(i) + " 年") for i in self.years]
        day_name = self.day_field % name
        day_subwidget = forms.HiddenInput().get_context(
            name=day_name,
            value=1,
            attrs={
                **context["widget"]["attrs"],
                "id": f"id_{day_name}",
            },
        )
        # year widget
        year_name = self.year_field % name
        year_subwidget = self.select_widget(attrs, choices=year_choices).get_context(
            name=year_name,
            value=context["widget"]["value"]["year"],
            attrs={**context["widget"]["attrs"], "id": "id_%s" % year_name},
        )
        context["widget"]["subwidgets"][0] = year_subwidget["widget"]

        # day widget is hidden
        context["widget"]["subwidgets"][2] = day_subwidget["widget"]
        return context
