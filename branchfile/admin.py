from django.contrib import admin

from .models import BranchFile


@admin.register(BranchFile)
class BranchFileAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "type",
        "original_filename",
        "attachment",
        "declaration_date",
        "uploaded_at",
        "branch",
        "result",
        "reason",
        "is_latest",
    ]
    list_filter = ["result", "type", "declaration_date", "is_latest"]
    search_fields = ["file", "branch__name"]
