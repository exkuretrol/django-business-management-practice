from django.contrib import admin

from .models import Announcement, AnnouncementAttachment


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_content",
        "effective_start_date",
        "effective_end_date",
    )

    def get_content(self, obj):
        return obj.content[:50]

    get_content.short_description = "content"


@admin.register(AnnouncementAttachment)
class AnnouncementAttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "attachment", "get_create_date")

    def get_create_date(self, obj):
        return obj.create_datetime.date()

    get_create_date.short_description = "create_datetime"
