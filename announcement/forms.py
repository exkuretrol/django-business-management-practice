from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Reset, Row, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from branch.forms import CleanBranchsMixin, get_all_branch_choices
from core.widgets import (
    Bootstrap5TagsSelect,
    Bootstrap5TagsSelectMultiple,
    LitePickerDateInput,
)

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


class AnnouncementCreateForm(CleanBranchsMixin, forms.ModelForm):
    # TODO: let user change the file name
    attachments = MultipleFileField(label=_("附件"), required=False)
    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Bootstrap5TagsSelectMultiple(
            config={"placeholder": "請選擇門市", "allowClear": True}
        ),
    )

    class Meta:
        model = Announcement
        fields = [
            "title",
            "content",
            "effective_start_date",
            "effective_end_date",
            "branchs",
            "status",
        ]

        widgets = {
            "branchs": Bootstrap5TagsSelectMultiple,
            "effective_start_date": LitePickerDateInput,
            "effective_end_date": LitePickerDateInput,
            "status": Bootstrap5TagsSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.include_media = False
        helper.layout = Layout(
            Div(
                Div(
                    Row(
                        Column("effective_start_date", css_class="col-6"),
                        Column("effective_end_date", css_class="col-6"),
                    ),
                    "branchs",
                    css_class="card-body",
                ),
                css_class="card mb-4",
            ),
            Div(
                Div(
                    "title",
                    "content",
                    "attachments",
                    "status",
                    Div(
                        Submit("submit", _("送出"), css_class="btn btn-primary"),
                        Reset("clear", _("清除"), css_class="btn btn-secondary"),
                        css_class="d-flex gap-2",
                    ),
                    css_class="card-body",
                ),
                css_class="card",
            ),
        )

        self.helper = helper


class AnnouncementUpdateForm(AnnouncementCreateForm):
    attachments = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        branchs = self.instance.branchs.all()
        self.fields["branchs"].widget.config.update(
            {
                "selected": (
                    ["0"] if branchs.count() == 0 else [str(b.pk) for b in branchs]
                )
            }
        )


class AnnouncementFilterForm(CleanBranchsMixin, forms.Form):
    pass
