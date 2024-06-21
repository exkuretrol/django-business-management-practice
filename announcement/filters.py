import django_filters as filters
from django import forms
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _

from .models import Announcement, StatusChoices


class AnnouncementFilter(filters.FilterSet):
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
        widget=DateInput(attrs={"type": "date", "placeholder": "請選擇起始日期"}),
        label=_("起始日期"),
    )
    effective_end_date = filters.DateFilter(
        lookup_expr="lte",
        widget=DateInput(attrs={"type": "date", "placeholder": "請選擇結束日期"}),
        label=_("結束日期"),
    )
    status = filters.ChoiceFilter(
        choices=StatusChoices.choices, empty_label=_("不指定")
    )

    class Meta:
        model = Announcement
        fields = [
            "title",
            "content",
            "branchs",
            "effective_start_date",
            "effective_end_date",
            "status",
        ]
