import django_filters as filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from branch.models import Branch
from core.widgets import Bootstrap5TagsSelect

from .models import Checklist


class ChecklistFilter(filters.FilterSet):
    branch = filters.ModelChoiceFilter(
        empty_label=_("請選擇一間門市"),
        queryset=Branch.objects.all(),
        widget=Bootstrap5TagsSelect,
    )

    class Meta:
        model = Checklist
        fields = ["branch"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.add_input(Submit("submit", _("篩選")))
        helper.form_method = "get"
        self.form.helper = helper

    @property
    def qs(self):
        queryset = super().qs
        branch = self.request.GET.get("branch", None)
        if branch is None or branch == "":
            return queryset.none()

        return queryset.filter(
            effective_start_date__lte=timezone.now(),
            effective_end_date__gte=timezone.now(),
        )
