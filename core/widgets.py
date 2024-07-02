from django import forms


class LitePickerDateInput(forms.DateInput):
    template_name = "litepicker/widget.html"

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs=attrs, format=format)


class Bootstrap5TagsSelectMultiple(forms.SelectMultiple):
    template_name = "bootstrap5-tags/widget.html"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)


class Bootstrap5TagsSelect(forms.Select):
    template_name = "bootstrap5-tags/widget.html"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)
