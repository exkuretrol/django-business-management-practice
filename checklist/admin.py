from django.contrib import admin

from .models import Checklist, ChecklistTemplate


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = [
        "branch",
        "content",
        "status",
        "order",
        "priority",
        "effective_start_date",
        "effective_end_date",
        "created_at",
        "last_modified",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["branch__name", "content"]


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "content",
        "order",
        "effective_start_date",
        "effective_end_date",
    ]
    search_fields = ["content"]
