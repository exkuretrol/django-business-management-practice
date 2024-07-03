import django_filters as filters
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Div, Layout, Row, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from branch.models import Branch
from core.widgets import (
    Bootstrap5TagsSelect,
    Bootstrap5TagsSelectMultiple,
    LitePickerDateInput,
)

from .forms import CheckListBranchForm
from .models import Checklist


class ChecklistBranchFilter(filters.FilterSet):
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


class ChecklistFilter(filters.FilterSet):

    all_branches = (0, _("所有門市"))
    branch_choices = list(Branch.objects.values_list("pk", "name"))
    branch_choices.insert(0, all_branches)

    branch = filters.MultipleChoiceFilter(
        choices=branch_choices,
        widget=Bootstrap5TagsSelectMultiple(config={"placeholder": "請選擇門市"}),
        method="filter_branch",
    )

    content = filters.CharFilter(
        field_name="content",
        label=_("內容"),
        lookup_expr="icontains",
    )

    date = filters.DateFilter(
        field_name="date",
        label=_("日期"),
        widget=LitePickerDateInput(
            attrs={"value": timezone.localdate().strftime("%Y-%m-%d")}
        ),
        method="filter_date",
    )

    status_choices = (
        ("0", _("未完成")),
        ("1", _("已完成")),
    )

    status = filters.ChoiceFilter(
        empty_label=_("全部"),
        field_name="status",
        widget=forms.RadioSelect(),
        choices=status_choices,
        method="filter_status",
    )

    def filter_branch(self, queryset, name, value):
        if len(value) == 1 and int(value[0]) == 0:
            return queryset

        return queryset.filter(branch__in=value)

    def filter_date(self, queryset, name, value):
        if value is None:
            return queryset

        return queryset.filter(
            effective_start_date__lte=value,
            effective_end_date__gte=value,
        )

    def filter_status(self, queryset, name, value):
        if value is None or value == "all":
            return queryset
        return queryset.filter(status=bool(int(value)))

    @property
    def qs(self):
        queryset = super().qs
        branch = self.request.GET.get("branch", None)
        if branch is None or branch == "":
            return queryset.none()
        return queryset

    class Meta:
        model = Checklist
        form = CheckListBranchForm
        fields = ["branch", "content", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = "get"
        helper.layout = Layout(
            Row(
                Column(
                    "branch",
                    css_class="col-8",
                ),
                Column(
                    InlineRadios(
                        "status", template="bootstrap5/radioselect_inline.html"
                    ),
                    css_class="col-4",
                ),
            ),
            "content",
            "date",
            Div(
                Submit("submit", _("篩選")),
                Button(
                    "匯出",
                    _("匯出"),
                    css_class="btn btn-outline-success",
                    onclick="window.location = '/checklist/export/csv?' + (new URLSearchParams(window.location.search).toString())",
                ),
            ),
        )

        self.form.helper = helper
        print(self.form.fields["branch"].initial)
