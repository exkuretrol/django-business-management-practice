from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    BaseInput,
    Button,
    Column,
    Div,
    Hidden,
    Layout,
    Reset,
    Row,
    Submit,
)
from django import forms
from django.db import transaction
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import (
    ALL_BRANCHS,
    BranchsCleanMixin,
    BranchsNoneCleanMixin,
    get_all_branch_choices,
)
from core.models import File, SourceChoices
from core.widgets import (
    Bootstrap5TagsSelectMultiple,
    LitePickerDateInput,
    MyQuillWidget,
    Tagify,
)
from member.models import Organization

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False

    class Meta:
        model = Announcement.attachments.through
        # auto add id field if formset located at update view
        fields = "__all__"
        labels = {
            "file": _("附件"),
        }

    def save(self, commit=True):
        f = super().save(commit=False)
        f.source = SourceChoices.ANNOUNCEMENT
        f.save()


class FormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_media = False
        self.form_tag = False
        self.template = "bootstrap5/file_formset.html"


class AttachmentFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.fields.get("file").queryset = File.objects.filter(
                source=SourceChoices.ANNOUNCEMENT
            )


class AnnouncementCreateForm(
    EffectiveDateCleanMixin, BranchsNoneCleanMixin, forms.ModelForm
):
    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Tagify(config={"placeholder": _("請選擇門市")}),
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
            "title": forms.TextInput(attrs={"placeholder": _("請輸入公告標題")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = MyQuillWidget()
        FormSet = inlineformset_factory(
            Announcement,
            Announcement.attachments.through,
            form=AnnouncementAttachmentForm,
            formset=AttachmentFormSet,
            extra=1,
            # create form should not appear delete checkbox
            can_delete=False,
            max_num=5,
        )

        self.attachment_formset = FormSet(
            data=kwargs.get("data"),
            instance=self.instance,
        )

        helper = FormHelper()
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
                    Hidden("status", value="0"),
                    Div(
                        Div(
                            Submit(
                                "publish", _("直接發佈"), css_class="btn btn-primary"
                            ),
                            Reset("clear", _("清除"), css_class="btn btn-secondary"),
                            css_class="d-flex gap-2",
                        ),
                        Button("draft", _("儲存草稿"), css_class="btn btn-light"),
                        css_class="d-flex justify-content-between",
                    ),
                    css_class="card-body",
                ),
                css_class="card mb-4",
            ),
        )

        self.helper = helper

    def save(self, user=None):
        with transaction.atomic():
            announcement = super().save()
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


class AnnouncementUpdateForm(
    EffectiveDateCleanMixin, BranchsNoneCleanMixin, forms.ModelForm
):
    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Tagify(),
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
            "effective_start_date": LitePickerDateInput,
            "effective_end_date": forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = MyQuillWidget()

        # convert branchs queryset to list of uuid string,
        # because the choices of MultipleChoiceField is queryset
        branchs_initial = self.initial["branchs"]
        if len(branchs_initial) == 0:
            branchs_initial = [ALL_BRANCHS]
        else:
            branchs_initial = [str(b.pk) for b in branchs_initial]

        self.initial["branchs"] = branchs_initial
        is_no_end_date = (
            self.initial["effective_end_date"].year == timezone.datetime.max.year
        )

        FormSet = inlineformset_factory(
            Announcement,
            Announcement.attachments.through,
            form=AnnouncementAttachmentForm,
            formset=AttachmentFormSet,
            extra=1,
            # update form should delete attachment
            can_delete=True,
            max_num=5,
        )

        self.attachment_formset = FormSet(
            data=kwargs.get("data"), instance=self.instance
        )
        helper = FormHelper()
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
                                checked=is_no_end_date,
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
                    Hidden("status", value="0"),
                    Div(
                        Submit("publish", _("更新並發佈"), css_class="btn btn-primary"),
                        Button("draft", _("存為草稿"), css_class="btn btn-light"),
                        css_class="d-flex justify-content-between",
                    ),
                    css_class="card-body",
                ),
                css_class="card mb-4",
            ),
        )
        self.helper = helper

    def save(self, user=None):
        with transaction.atomic():
            announcement = super().save(False)
            announcement.last_modified_by = user
            # manully save m2m field
            self.save_m2m()
            announcement.save()
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


class AnnouncementFilterForm(BranchsCleanMixin, forms.Form):
    pass
