import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_quill.fields import FieldQuill
from django_tables2.columns import CheckBoxColumn

from .models import Announcement, StatusChoices


class AnnouncementTable(tables.Table):
    check = CheckBoxColumn(
        empty_values=[],
        attrs={
            "th__input": {"class": "form-check-input", "id": "check_all"},
            "td__input": {"class": "form-check-input"},
        },
    )
    title = tables.LinkColumn(
        args=[tables.A("pk")],
        attrs={"td": {"class": "text-nowrap"}},
        orderable=False,
    )
    content = tables.Column(attrs={"td": {"class": "text-nowrap"}}, orderable=False)
    effective_start_date = tables.Column(
        verbose_name=_("日期"), attrs={"td": {"class": "text-nowrap"}}
    )
    status = tables.Column(
        attrs={"td": {"class": "text-nowrap"}, "th": {"class": "text-center"}},
        orderable=False,
    )
    attachments = tables.Column(orderable=False, attrs={"td": {"class": "text-nowrap"}})
    func = tables.TemplateColumn(
        verbose_name=_("操作"),
        template_name="django_tables2/func_column.html",
        orderable=False,
        attrs={"td": {"class": "text-nowrap"}, "th": {"class": "text-center"}},
    )

    def render_title(self, value):
        if len(value) > 16:
            return value[:16] + "..."
        return value

    def render_content(self, value: FieldQuill):
        content = value.plain
        if len(content) > 32:
            return content[:32] + "..."
        return content

    def render_status(self, value):
        if value == StatusChoices.DRAFT:
            return format_html(
                '<span class="d-block badge bg-secondary">{}</span>', _("草稿")
            )
        elif value == StatusChoices.PUBLISHED:
            return format_html(
                '<span class="d-block badge bg-success">{}</span>', _("已發佈")
            )
        elif value == StatusChoices.UNAVAILABLE:
            return format_html(
                '<span class="d-block badge bg-danger">{}</span>', _("已下架")
            )

    def render_attachments(self, value):
        attachments = value.all()
        if not attachments:
            return ""

        attachment_buttons = []
        for attachment in attachments:
            attachment_buttons.append(
                f"""
                <a href="%s" class="btn btn-warning rounded-pill" target="_blank">
                    <i class="pli-download-from-cloud"></i>
                    %s
                </a>
                """
                % (attachment.attachment.url, attachment.name)
            )
        return format_html(" ".join(attachment_buttons))

    def render_effective_start_date(self, value):
        return value.strftime("%Y-%m-%d")

    # TODO: add multiple actions implementation at the footer of the table

    class Meta:
        model = Announcement
        fields = (
            "title",
            "content",
            "effective_start_date",
            # "effective_end_date",
            # "author",
            "attachments",
            # "branchs",
        )
        empty_text = _("找不到公告")
        sequence = (
            "check",
            "effective_start_date",
            "title",
            "content",
            "attachments",
            "status",
            "func",
        )
        attrs = {"class": "table table-striped align-middle"}
        row_attrs = {"data-id": lambda record: record.pk}
        per_page = 4
        order_by = ("-effective_start_date",)
