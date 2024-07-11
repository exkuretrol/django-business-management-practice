from typing import Any

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Div, Layout, Row, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from announcement.forms import EffectiveDateCleanMixin
from branch.forms import CleanBranchsMixin, get_all_branch_choices
from branch.models import Branch
from core.widgets import Bootstrap5TagsSelectMultiple, LitePickerDateInput

from .models import Checklist, ChecklistTemplate, PriorityChoices


class CheckListBranchForm(CleanBranchsMixin, forms.Form):
    pass


class ChecklistTemplateCreateForm(
    EffectiveDateCleanMixin, CleanBranchsMixin, forms.ModelForm
):
    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Bootstrap5TagsSelectMultiple(
            config={"placeholder": "請選擇門市", "allowClear": True}
        ),
    )

    class Meta:
        model = ChecklistTemplate
        fields = [
            "content",
            "priority",
            "effective_start_date",
            "effective_end_date",
            "branchs",
        ]

        widgets = {
            "content": forms.TextInput,
            "priority": forms.RadioSelect,
        }

        labels = {
            "priority": "分類",
            "effective_start_date": "生效開始日期",
            "effective_end_date": "生效結束日期",
        }

    def save(self, user) -> Any:
        obj = super().save(commit=False)
        obj.last_modified_by = user
        obj.save()
        self.save_m2m()

        branchs = self.cleaned_data["branchs"]
        if not branchs.exists():
            branchs = Branch.objects.all()
        if self.cleaned_data["priority"] == PriorityChoices.ROUTINE:
            Checklist.objects.bulk_create(
                [
                    Checklist(
                        template_id=self.instance,
                        branch=branch,
                        effective_start_date=timezone.localdate(),
                        effective_end_date=timezone.localdate(),
                    )
                    for branch in branchs
                ]
            )
        else:
            Checklist.objects.bulk_create(
                [
                    Checklist(
                        template_id=self.instance,
                        branch=branch,
                        effective_start_date=self.cleaned_data["effective_start_date"],
                        effective_end_date=self.cleaned_data["effective_end_date"],
                    )
                    for branch in branchs
                ]
            )

        return obj

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.layout = Layout(
            Row(
                Column(
                    "branchs",
                    css_class="col-lg-8",
                ),
                Column(
                    InlineRadios(
                        "priority",
                        template="bootstrap5/radioselect_inline.html",
                    ),
                    css_class="col-lg-4",
                ),
            ),
            Row(
                Column("effective_start_date"),
                Column("effective_end_date"),
            ),
            "content",
            Div(
                Submit("submit", _("新增")),
                Button(
                    "cancel", _("取消"), css_class="btn-light", onclick="history.back()"
                ),
                css_class="d-flex gap-2",
            ),
        )
        self.helper = helper


class ChecklistTemplateUpdateForm(forms.ModelForm):
    priority = forms.ChoiceField(
        label=_("種類"),
        choices=PriorityChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )

    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Bootstrap5TagsSelectMultiple(config={"placeholder": "請選擇門市"}),
    )

    def save(self, user):
        obj = super().save(commit=False)
        obj.last_modified_by = user
        obj.save()
        return obj

    class Meta:
        form = CheckListBranchForm
        model = ChecklistTemplate
        fields = [
            "content",
            "priority",
            "effective_start_date",
            "effective_end_date",
        ]
        widgets = {
            "content": forms.TextInput,
            "effective_end_date": LitePickerDateInput,
            "effective_start_date": LitePickerDateInput,
        }

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

        form_fields = self.fields
        for field_name in form_fields.keys():
            if field_name in [
                "priority",
                "effective_start_date",
                "effective_end_date",
                "branchs",
            ]:
                form_fields[field_name].disabled = True
                form_fields[field_name].required = False

        helper = FormHelper()
        helper.layout = Layout(
            InlineRadios("priority", template="bootstrap5/radioselect_inline.html"),
            "branchs",
            Row(
                Column("effective_start_date"),
                Column("effective_end_date"),
            ),
            "content",
            Div(
                Submit("submit", _("更新")),
                Button(
                    "cancel", _("取消"), css_class="btn-light", onclick="history.back()"
                ),
                css_class="d-flex gap-2",
            ),
        )

        self.helper = helper
