from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.management.jobs import DailyJob

from announcement.models import Announcement, StatusChoices


class Job(DailyJob):
    help = _("封存已過期公告")

    def execute(self):
        today = timezone.localdate()
        previous_day = today - timezone.timedelta(days=1)

        Announcement.objects.filter(
            effective_end_date__lte=previous_day,
        ).update(status=StatusChoices.UNAVAILABLE)
