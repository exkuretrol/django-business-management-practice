from django.contrib import admin

from .forms import FileUploadForm
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "extension", "hash", "create_datetime")
    form = FileUploadForm
