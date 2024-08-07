import django_filters as filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Reset, Row, Submit
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.forms import get_all_branch_choices
from core.widgets import (
    Bootstrap5TagsSelect,
    LitePickerDateInput,
    Tagify,
    TagifyMultipleChoiceFilter,
)

from .forms import AnnouncementFilterForm
from .models import Announcement, StatusChoices


class AnnouncementBranchsFilter(filters.FilterSet):
    title = filters.CharFilter(
        lookup_expr="icontains",
        label=_("標題"),
        widget=forms.TextInput(attrs={"placeholder": "請輸入公告標題"}),
    )
    content = filters.CharFilter(
        lookup_expr="icontains",
        label=_("內容"),
        widget=forms.TextInput(attrs={"placeholder": "請輸入公告內容"}),
    )
    effective_start_date = filters.DateFilter(
        lookup_expr="gte",
        widget=LitePickerDateInput(attrs={"placeholder": "不指定起始日期"}),
        label=_("起始日期"),
    )
    effective_end_date = filters.DateFilter(
        lookup_expr="lte",
        widget=LitePickerDateInput(attrs={"placeholder": "不指定結束日期"}),
        label=_("結束日期"),
    )
    status = filters.ChoiceFilter(
        choices=StatusChoices.choices,
        empty_label=_("不指定"),
        widget=Bootstrap5TagsSelect,
    )
    branchs = TagifyMultipleChoiceFilter(
        field_name="branchs",
        label=_("門市"),
        choices=get_all_branch_choices,
        required=False,
        widget=Tagify(config={"placeholder": _("請選擇門市")}),
    )

    class Meta:
        model = Announcement
        form = AnnouncementFilterForm
        fields = [
            "title",
            "content",
            "branchs",
            "effective_start_date",
            "effective_end_date",
            "status",
        ]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        form = self.form
        helper = FormHelper()
        helper.form_method = "get"
        helper.disable_csrf = True
        helper.layout = Layout(
            "title",
            "content",
            "branchs",
            Row(
                Column("effective_start_date", css_class="col-md-5"),
                Column("effective_end_date", css_class="col-md-5"),
                Column("status", css_class="col-md-2"),
            ),
            Submit("submit", "搜尋", css_class="btn-primary"),
            Reset("reset", "清除", css_class="btn-light"),
        )
        form.helper = helper


class AnnouncementFilter(filters.FilterSet):
    title = filters.CharFilter(
        lookup_expr="icontains",
        label=_("標題"),
        widget=forms.TextInput(attrs={"placeholder": "請輸入公告標題"}),
    )

    effective_start_date = filters.DateFilter(
        lookup_expr="gte",
        widget=LitePickerDateInput(attrs={"placeholder": "不指定起始日期"}),
        label=_("起始日期"),
    )

    effective_end_date = filters.DateFilter(
        lookup_expr="lte",
        widget=LitePickerDateInput(attrs={"placeholder": "不指定結束日期"}),
        label=_("結束日期"),
    )

    class Meta:
        model = Announcement
        fields = [
            "title",
            "effective_start_date",
            "effective_end_date",
        ]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        form = self.form
        helper = FormHelper()
        helper.form_method = "get"
        helper.disable_csrf = True
        helper.layout = Layout(
            "title",
            Row(
                Column("effective_start_date", css_class="col-md-6"),
                Column("effective_end_date", css_class="col-md-6"),
            ),
            Submit("submit", "搜尋", css_class="btn-primary"),
            Reset("reset", "清除", css_class="btn-light"),
        )
        form.helper = helper

    @property
    def qs(self):
        return super().qs.filter(
            Q(status=StatusChoices.PUBLISHED)
            & (
                Q(branchs__isnull=True)
                | Q(branchs__in=[self.request.user.member_set.first().org])
            )
        )
