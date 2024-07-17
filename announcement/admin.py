from django.contrib import admin

from .models import Announcement


class AttachmentInline(admin.TabularInline):
    model = Announcement.attachments.through
    extra = 1


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_content",
        "effective_start_date",
        "effective_end_date",
        "author",
        "last_modified",
        "last_modified_by",
    )

    exclude = ("attachments",)

    inlines = [AttachmentInline]

    def get_content(self, obj):
        content = obj.content.plain
        if len(content) > 50:
            return content[:50] + "..."
        return content

    get_content.short_description = "content"
