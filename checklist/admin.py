from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Checklist, ChecklistTemplate


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = [
        "template_id",
        "branch",
        "status",
        "order",
        "get_priority",
        "effective_start_date",
        "effective_end_date",
        "created_at",
        "is_archived",
        "last_modified",
        "last_modified_by",
    ]

    @admin.display(description=_("優先度"), ordering="template_id__priority")
    def get_priority(self, obj):
        return obj.template_id.priority

    def get_effective_end_date(self, obj):
        return obj.template_id.effective_end_date

    list_filter = ["status", "template_id__priority"]
    search_fields = ["branch__name", "content"]


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = [
        # "branchs",
        "content",
        "order",
        "priority",
        "effective_start_date",
        "effective_end_date",
        "last_modified",
        "last_modified_by",
    ]

    search_fields = ["content"]
