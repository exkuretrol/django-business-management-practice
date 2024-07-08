from django.utils.translation import gettext_lazy as _

from .models import Branch


def get_all_branch_choices():
    all_branches = (0, _("所有門市"))
    branch_choices = list(Branch.objects.values_list("pk", "name"))
    branch_choices.insert(0, all_branches)
    return branch_choices


class CleanBranchsMixin:
    def clean_branchs(self):
        branchs = self.cleaned_data["branchs"]
        if "0" in branchs:
            if len(branchs) > 1:
                self.add_error("branchs", _("不能同時選擇所有門市與其他門市"))
            return Branch.objects.none()
        branchs = Branch.objects.filter(pk__in=branchs)
        return branchs
