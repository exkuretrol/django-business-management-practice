import django_filters as filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import gettext_lazy as _

from .models import Checklist


class ChecklistFilter(filters.FilterSet):
    class Meta:
        model = Checklist
        fields = ["branch"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.add_input(Submit("submit", _("篩選")))
        helper.form_method = "get"
        self.form.helper = helper
