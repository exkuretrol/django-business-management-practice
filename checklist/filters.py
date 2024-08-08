import django_filters as filters
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Div, Layout, Row, Submit
from django import forms
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import get_all_branch_choices
from core.widgets import (
    Bootstrap5TagsSelect,
    LitePickerDateInput,
    Tagify,
    TagifyMultipleChoiceFilter,
)

from .forms import CheckListBranchForm
from .models import Checklist, PriorityChoices


class ChecklistBranchFilter(filters.FilterSet):
    branch = TagifyMultipleChoiceFilter(
        widget=Tagify(config={"placeholder": "請選擇一間門市", "maxTags": 1}),
        required=True,
        # checklist branch filter didn't need all branch option
        choices=get_all_branch_choices(include_all_branch=False),
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
        today = timezone.localdate()

        queryset = (
            queryset.exclude(is_archived=True)
            .filter(
                effective_start_date__lte=today,
                effective_end_date__gte=today,
            )
            .annotate(
                priority=F("template_id__priority"),
                content=F("template_id__content"),
                template_id_pk=F("template_id__pk"),
            )
            .order_by("priority", "status")
        )
        return queryset


class ChecklistFilter(filters.FilterSet):

    branchs = filters.MultipleChoiceFilter(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Tagify(config={"placeholder": "請選擇門市"}),
        required=True,
        method="filter_branchs",
    )

    priority = filters.ChoiceFilter(
        label=_("類別"),
        choices=PriorityChoices,
        widget=Bootstrap5TagsSelect(config={"placeholder": "請選擇類別"}),
        required=False,
        method="filter_priority",
    )

    content = filters.CharFilter(
        field_name="content",
        label=_("內容"),
        lookup_expr="icontains",
        widget=Tagify(config={"placeholder": "請輸入待做事項"}),
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

    def filter_branchs(self, queryset, name, value):
        if len(value) == 0:
            return queryset

        return queryset.filter(branch__in=value)

    def filter_date(self, queryset, name, value):
        if value is None:
            return queryset

        queryset = queryset.filter(
            effective_start_date__lte=value,
            effective_end_date__gte=value,
        )
        return queryset

    def filter_priority(self, queryset, name, value):
        return queryset.filter(template_id__priority=value)

    def filter_status(self, queryset, name, value):
        if value is None or value == "all":
            return queryset
        return queryset.filter(status=bool(int(value)))

    @property
    def qs(self):
        branchs = self.request.GET.get("branchs", None)
        if branchs is None or branchs == "":
            return Checklist.objects.none()

        return super().qs

    class Meta:
        model = Checklist
        form = CheckListBranchForm
        fields = ["content", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = "get"
        helper.layout = Layout(
            Row(
                Column(
                    "branchs",
                    css_class="col-8",
                ),
                Column(
                    InlineRadios(
                        "status", template="bootstrap5/radioselect_inline.html"
                    ),
                    css_class="col-4",
                ),
            ),
            "priority",
            "content",
            "date",
            Div(
                Submit("submit", _("篩選")),
                Button(
                    "export",
                    _("匯出"),
                    css_class="btn btn-outline-success",
                    onclick=f"window.location = '{self.request.path}csv?' + (new URLSearchParams(window.location.search).toString())",
                ),
            ),
        )

        self.form.helper = helper


class ChecklistTemporaryFilter(ChecklistFilter):
    priority = None

    @property
    def qs(self):
        queryset_list = super().qs
        return queryset_list.filter(template_id__priority=PriorityChoices.TEMPORARY)
