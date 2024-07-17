from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.management.jobs import DailyJob

from checklist.models import Checklist, PriorityChoices, StatusChoices


class Job(DailyJob):
    help = _("封存待做清單")

    def execute(self):
        start_date = timezone.localdate()
        end_date = start_date
        previous_day = end_date - timezone.timedelta(days=1)

        Checklist.objects.filter(
            template_id__priority=PriorityChoices.ABNORMAL,
            effective_start_date__lte=start_date,
            effective_end_date__gte=end_date,
            # checklist is finished
            status=StatusChoices.DONE,
        ).update(is_archived=True)

        Checklist.objects.filter(
            template_id__priority=PriorityChoices.TEMPORARY,
            effective_end_date=previous_day,
        ).update(is_archived=True)
