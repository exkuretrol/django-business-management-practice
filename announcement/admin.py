from django.contrib import admin

from .models import Announcement, AnnouncementAttachment


class AttachmentInline(admin.TabularInline):
    model = Announcement.attachments.through
    extra = 1


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "content",
        # "get_content",
        "effective_start_date",
        "effective_end_date",
        "author",
    )

    exclude = ("attachments",)

    inlines = [AttachmentInline]

    def get_content(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + "..."
        return obj.content

    get_content.short_description = "content"


@admin.register(AnnouncementAttachment)
class AnnouncementAttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "attachment", "get_create_date")

    def get_create_date(self, obj):
        return obj.create_datetime.date()

    get_create_date.short_description = "create_datetime"
