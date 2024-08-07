from typing import Any

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Div, Layout, Row, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from announcement.forms import EffectiveDateCleanMixin
from core.forms import (
    ALL_BRANCHS,
    BranchsCleanMixin,
    BranchsNoneCleanMixin,
    get_all_branch_choices,
)
from core.widgets import LitePickerDateInput, Tagify
from member.models import Organization

from .models import Checklist, ChecklistTemplate, PriorityChoices


class CheckListBranchForm(BranchsCleanMixin, forms.Form):
    pass


class ChecklistTemplateCreateForm(
    EffectiveDateCleanMixin, BranchsNoneCleanMixin, forms.ModelForm
):
    priority_choices = (
        (PriorityChoices.TEMPORARY, PriorityChoices(PriorityChoices.TEMPORARY).label),
        (PriorityChoices.ROUTINE, PriorityChoices(PriorityChoices.ROUTINE).label),
    )

    priority = forms.ChoiceField(
        label=_("種類"),
        choices=priority_choices,
        widget=forms.RadioSelect,
        initial=PriorityChoices.TEMPORARY,
    )

    branchs = forms.MultipleChoiceField(
        label=_("門市"),
        choices=get_all_branch_choices,
        widget=Tagify(config={"placeholder": _("請選擇門市")}),
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
            "content": forms.TextInput(attrs={"placeholder": _("請輸入待做事項")}),
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
        if branchs.count() == 0:
            branchs = Organization.objects.filter(is_store=True)
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
        widget=Tagify(),
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
            "branchs",
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

        # convert branchs to str, because multiple choices instance isn't queryset
        branchs_initial = self.initial["branchs"]
        if len(branchs_initial) == 0:
            branchs_initial = [ALL_BRANCHS]
        else:
            branchs_initial = [str(b.pk) for b in branchs_initial]

        self.initial["branchs"] = branchs_initial

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
