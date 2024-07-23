from crispy_forms.helper import FormHelper
from crispy_forms.layout import BaseInput, Column, Div, Layout, Reset, Row, Submit
from django import forms
from django.db import transaction
from django.forms import formset_factory, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from branch.forms import CleanBranchsMixin, get_all_branch_choices
from core.models import File
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


class EffectiveDateCleanMixin:
    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        start_date = cleaned_data.get("effective_start_date")
        end_date = cleaned_data.get("effective_end_date")
        if start_date and end_date and start_date > end_date:
            self.add_error(
                "effective_end_date",
                _("結束日期不可早於開始日期"),
            )
        return cleaned_data


class CheckBoxInput(BaseInput):
    # template = ""
    input_type = "checkbox"
    field_classes = " ".join(["form-check-input"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = {"type": self.input_type}


class AnnouncementAttachmentForm(forms.ModelForm):

    class Meta:
        model = Announcement.attachments.through
        fields = ["file"]
        # widgets = {"file": Bootstrap5TagsSelect}
        labels = {"file": _("附件")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False
        self.fields["file"].empty_label = _("請選擇一個檔案")
        helper = FormHelper()
        helper.disable_csrf = True
        helper.form_tag = False
        helper.layout = Layout(
            Row(
                Column("file", css_class="col-10"),
                Div(css_class="col-2"),
                css_id="Announcement_attachments-0",
            )
        )
        self.helper = helper


AttachmentInlineFormSet = inlineformset_factory(
    Announcement,
    Announcement.attachments.through,
    form=AnnouncementAttachmentForm,
    extra=1,
    can_delete=False,
    max_num=5,
)


class AnnouncementCreateForm(CleanBranchsMixin, forms.ModelForm):
    # TODO: let user change the file name
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
            "effective_end_date": forms.TextInput,
            "status": Bootstrap5TagsSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attachment_formset = AttachmentInlineFormSet(
            data=kwargs.get("data"), instance=self.instance
        )

        helper = FormHelper()
        helper.include_media = False
        helper.form_tag = False
        helper.disable_csrf = True
        helper.layout = Layout(
            Div(
                Div(
                    Row(
                        Column("effective_start_date", css_class="col-6 col-lg-5"),
                        Column("effective_end_date", css_class="col-6 col-lg-5"),
                        Column(
                            CheckBoxInput(
                                name="is_no_end_date",
                                value=None,
                                template="bootstrap5/checkbox.html",
                                checked=True,
                                css_class="d-block",
                            ),
                            css_class="col-12 col-lg-2",
                        ),
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
                    "status",
                    Div(
                        Submit("submit", _("送出"), css_class="btn btn-primary"),
                        Reset("clear", _("清除"), css_class="btn btn-secondary"),
                        css_class="d-flex gap-2",
                    ),
                    css_class="card-body",
                ),
                css_class="card mb-4",
            ),
        )

        self.helper = helper

    def save(self, **kwargs):
        with transaction.atomic():
            announcement = super().save(**kwargs)
            self.attachment_formset.instance = announcement
            self.attachment_formset.save()

            return announcement

    def clean(self):
        super().clean()
        self.attachment_formset.clean()
        return self.cleaned_data

    def is_valid(self):
        return super().is_valid() and self.attachment_formset.is_valid()

    def has_changed(self):
        return super().has_changed() or self.attachment_formset.has_changed()


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

    def save(self, user):
        instance = super().save(commit=False)
        instance.last_modified_by = user
        instance.save()
        return instance


class AnnouncementFilterForm(CleanBranchsMixin, forms.Form):
    pass
