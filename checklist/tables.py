import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.columns import CheckBoxColumn

from .models import Checklist


class ChecklistTable(tables.Table):
    def get_status(value, record):
        return value

    status = CheckBoxColumn(
        checked=get_status,
        attrs={
            "th__input": {"class": "form-check-input", "id": "check_all"},
            "td__input": {"class": "form-check-input"},
        },
    )

    class Meta:
        model = Checklist
        fields = ["status", "content", "order", "priority"]
        empty_text = _("沒有可顯示的待做項目")
        order_by = (
            "-priority",
            "order",
        )
