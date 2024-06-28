import logging
from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from branch.models import Branch

from .models import Checklist, PriorityChoices


class ChecklistCreateForm(forms.Form):
    # manually add a choice for all branches
    all_branches = (0, _("所有門市"))
    branch_choices = list(Branch.objects.values_list("pk", "name"))
    branch_choices.insert(0, all_branches)

    branch = forms.MultipleChoiceField(choices=branch_choices)
    content = forms.CharField(widget=forms.TextInput)
    priority = forms.ChoiceField(choices=PriorityChoices.choices)
    effective_start_date = forms.DateField(widget=forms.SelectDateWidget)
    effective_end_date = forms.DateField(widget=forms.SelectDateWidget)

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
                    effective_start_date=self.cleaned_data["effective_start_date"],
                    effective_end_date=self.cleaned_data["effective_end_date"],
                )
                for branch in branchs
            ],
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.add_input(Submit("submit", _("新增")))
        self.helper = helper
