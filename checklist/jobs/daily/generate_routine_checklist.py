from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.management.jobs import DailyJob

from checklist.models import Checklist, ChecklistTemplate, PriorityChoices
from member.models import Organization


class Job(DailyJob):
    help = _("產生例行待做清單")

    def execute(self):
        # start date and end date will be today
        start_date = timezone.localdate()
        end_date = start_date

        # filter valid checklist template
        checklist_valid = ChecklistTemplate.objects.filter(
            effective_start_date__lte=start_date,
            effective_end_date__gte=end_date,
            priority=PriorityChoices.ROUTINE,
        )

        # filter checklist for all branchs
        checklist_for_all = checklist_valid.filter(branchs__isnull=True)
        checklist_objects_list = []
        checklist_objects_list += [
            Checklist(
                template_id=template,
                branch=branch,
                effective_start_date=start_date,
                effective_end_date=end_date,
            )
            for branch in Organization.objects.filter(is_store=True)
            for template in checklist_for_all
        ]

        # filter checklist for specific branchs
        checklist_specific_branchs = checklist_valid.exclude(branchs__isnull=True)
        checklist_objects_list += [
            Checklist(
                template_id=template,
                branch=branch,
                effective_start_date=start_date,
                effective_end_date=end_date,
            )
            for template in checklist_specific_branchs
            for branch in template.branchs.all()
        ]

        # bulk create checklist
        Checklist.objects.bulk_create(checklist_objects_list)
