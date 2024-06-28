from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.management.jobs import DailyJob

from branch.models import Branch
from checklist.models import Checklist, ChecklistTemplate, PriorityChoices


class Job(DailyJob):
    help = _("產生例行待做清單")

    def execute(self):
        checklist_valid = ChecklistTemplate.objects.filter(
            effective_start_date__lte=timezone.now(),
            effective_end_date__gte=timezone.now(),
        )

        # create checklist for all branchs
        checklist_for_all = checklist_valid.filter(branchs__isnull=True)
        Checklist.objects.bulk_create(
            [
                Checklist(
                    branch=branch,
                    content=template.content,
                    priority=PriorityChoices.ROUTINE,
                    effective_start_date=template.effective_start_date,
                    effective_end_date=template.effective_end_date,
                )
                for template in checklist_for_all
                for branch in Branch.objects.all()
            ]
        )

        # create checklist for specific branchs
        checklist_specific_branchs = checklist_valid.exclude(branchs__isnull=True)
        Checklist.objects.bulk_create(
            [
                Checklist(
                    branch=branch,
                    content=template.content,
                    priority=PriorityChoices.ROUTINE,
                    effective_start_date=template.effective_start_date,
                    effective_end_date=template.effective_end_date,
                )
                for template in checklist_specific_branchs
                for branch in template.branchs.all()
            ]
        )
