from typing import Any

from django import forms

from .models import Announcement


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]

        return result


class AnnouncementCreateForm(forms.ModelForm):
    # TODO: let user change the file name
    attachments = MultipleFileField(required=False)

    class Meta:
        model = Announcement
        fields = [
            "title",
            "content",
            "effective_start_date",
            "effective_end_date",
            "branchs",
        ]

    def save(self, commit: bool = ...) -> Any:
        return super().save(commit)
