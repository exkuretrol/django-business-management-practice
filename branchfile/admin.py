from django.contrib import admin

from .models import BranchFile


@admin.register(BranchFile)
class BranchFileAdmin(admin.ModelAdmin):
    list_display = [
        "attachment",
        "type",
        "declaration_date",
    ]
    list_filter = ["type", "declaration_date"]
    search_fields = ["file", "branch__name"]
