from typing import Any

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Column, Div, Layout, Row, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from branch.models import Branch
from core.widgets import Bootstrap5TagsSelectMultiple, LitePickerDateInput

from .models import Checklist, PriorityChoices


class ChecklistCreateForm(forms.Form):
    # manually add a choice for all branches
    all_branches = (0, _("所有門市"))
    branch_choices = list(Branch.objects.values_list("pk", "name"))
    branch_choices.insert(0, all_branches)

    branch = forms.MultipleChoiceField(
        label=_("門市"),
        choices=branch_choices,
        widget=Bootstrap5TagsSelectMultiple(),
    )
    content = forms.CharField(widget=forms.TextInput, label=_("內容"))
    priority = forms.ChoiceField(
        label=_("種類"),
        choices=PriorityChoices.choices,
        widget=forms.RadioSelect(),
    )
    effective_end_date = forms.DateField(label="有效日期", widget=LitePickerDateInput)

    def clean_branch(self):
        if "0" in self.cleaned_data["branch"]:
            if len(self.cleaned_data["branch"]) > 1:
                self.add_error("branch", _("不能同時選擇所有門市與其他門市"))

    def save(self, commit: bool = True) -> Any:
        branchs = self.cleaned_data["branch"]
        if branchs is None:
            branchs = Branch.objects.all()

        Checklist.objects.bulk_create(
            [
                Checklist(
                    branch=branch,
                    content=self.cleaned_data["content"],
                    priority=self.cleaned_data["priority"],
                    effective_end_date=self.cleaned_data["effective_end_date"],
                )
                for branch in branchs
            ],
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.layout = Layout(
            InlineRadios("priority", template="bootstrap5/radioselect_inline.html"),
            "branch",
            "effective_end_date",
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


class ChecklistUpdateForm(forms.ModelForm):
    priority = forms.ChoiceField(
        label=_("種類"),
        choices=PriorityChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
    )

    class Meta:
        model = Checklist
        fields = ["content", "priority", "effective_start_date", "effective_end_date"]
        widgets = {
            "effective_end_date": LitePickerDateInput,
            "effective_start_date": LitePickerDateInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.layout = Layout(
            InlineRadios("priority", template="bootstrap5/radioselect_inline.html"),
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
