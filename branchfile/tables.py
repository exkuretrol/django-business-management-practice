import itertools

import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from member.models import Organization

from .models import BranchFile, ResultChoices


class BranchFileUploadRecordsTable(tables.Table):
    delete = tables.TemplateColumn(
        template_name="django_tables2/delete_column.html",
        orderable=False,
        verbose_name=_("刪除"),
    )
    row_number = tables.Column(empty_values=(), verbose_name="#")
    declaration_date = tables.Column(orderable=True)

    uploaded_at = tables.Column(orderable=True)

    class Meta:
        model = BranchFile
        fields = [
            "type",
            "declaration_date",
            "uploaded_at",
            "result",
            "original_filename",
        ]
        sequence = [
            "delete",
            "row_number",
            "type",
            "original_filename",
            "declaration_date",
            "uploaded_at",
            "result",
        ]
        order_by = "-uploaded_at"
        orderable = False
        empty_text = _("目前沒有上傳紀錄")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count(1)

    def render_row_number(self):
        return f"{next(self.counter)}"

    def render_result(self, value, record):
        return format_html(
            '<span class="badge rounded-pill bg-{}">{}</span>',
            "success" if record.result == ResultChoices.SUCCESS else "danger",
            value,
        )


class BranchFileBranchsDownloadFilesTable(tables.Table):
    org_code = tables.Column(verbose_name=_("門市代號"))
    short_name = tables.Column(verbose_name=_("門市名稱"))
    health_insurance_file = tables.TemplateColumn(
        template_name="django_tables2/file_column.html", verbose_name=_("健保申報總表")
    )
    payment_notification_file = tables.TemplateColumn(
        template_name="django_tables2/file_column.html", verbose_name=_("付款通知書")
    )
    withholding_certificate_file = tables.TemplateColumn(
        template_name="django_tables2/file_column.html", verbose_name=_("扣繳憑單")
    )
    detailed_paid_amount_statement_file = tables.TemplateColumn(
        template_name="django_tables2/file_column.html",
        verbose_name=_("實付金額明細表"),
    )
    breakdown_of_items_table_file = tables.TemplateColumn(
        template_name="django_tables2/file_column.html", verbose_name=_("分列項目表")
    )
    last_uploaded_date = tables.Column(
        accessor="last_uploaded_date", verbose_name=_("最新上傳日期"), empty_values=()
    )
    declaration_date = tables.Column(
        accessor="declaration_date", verbose_name=_("申報日期")
    )

    def render_last_uploaded_date(self, value):
        if value is None:
            return ""
        return value.strftime("%Y-%m-%d")

    def render_declaration_date(self, value):
        if value is None:
            return ""
        return value.strftime("%Y-%m-%d")

    class Meta:
        model = Organization
        fields = [
            "org_code",
            "short_name",
            "last_uploaded_date",
            "declaration_date",
            "health_insurance_file",
            "payment_notification_file",
            "withholding_certificate_file",
            "detailed_paid_amount_statement_file",
            "breakdown_of_items_table_file",
        ]
        labels = {"short_name": "門市"}

        orderable = False
        empty_text = _("請選擇至少一間門市")
        attrs = {"class": "table table-striped text-nowrap"}
        row_attrs = {"data-id": lambda record: record.pk}
        per_page = 20
