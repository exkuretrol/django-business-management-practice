import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def now_plus_7_days() -> timezone.datetime:
    return timezone.now() + timezone.timedelta(days=7)


class PriorityChoices(models.IntegerChoices):
    ABNORMAL = 1, _("異常")
    TEMPORARY = 2, _("臨時")
    ROUTINE = 3, _("例行")


class Checklist(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("UUID")
    )
    template_id = models.ForeignKey(
        to="checklist.ChecklistTemplate",
        verbose_name=_("待做清單模板 ID"),
        on_delete=models.CASCADE,
    )
    branch = models.ForeignKey(
        to="branch.Branch",
        verbose_name=_("門市"),
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(verbose_name=_("狀態"), default=False)
    order = models.IntegerField(verbose_name=_("排序"), default=0)
    effective_start_date = models.DateField(
        verbose_name=_("生效起日"), default=timezone.now
    )
    effective_end_date = models.DateField(
        verbose_name=_("生效迄日"), default=now_plus_7_days
    )
    created_at = models.DateTimeField(verbose_name=_("建立時間"), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_("最後更新時間"), auto_now=True)
    last_modified_by = models.ForeignKey(
        verbose_name=_("最後更新者"),
        to="core.User",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )

    def __str__(self) -> str:
        return f"{self.branch} - {self.template_id.content}"


class ChecklistTemplate(models.Model):
    branchs = models.ManyToManyField(
        "branch.Branch", blank=True, verbose_name=_("門市")
    )
    content = models.TextField(verbose_name=_("內容"))
    order = models.IntegerField(verbose_name=_("排序"), default=0)
    priority = models.IntegerField(
        verbose_name=_("優先度"),
        default=0,
        choices=PriorityChoices.choices,
    )
    effective_start_date = models.DateField(
        verbose_name=_("生效起日"), default=timezone.now
    )
    effective_end_date = models.DateField(
        verbose_name=_("生效迄日"), default=now_plus_7_days
    )
    last_modified = models.DateTimeField(verbose_name=_("最後更新時間"), auto_now=True)
    last_modified_by = models.ForeignKey(
        verbose_name=_("最後更新者"),
        to="core.User",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )

    def __str__(self) -> str:
        return f"{self.pk} - ({PriorityChoices(self.priority).label}) {self.content}"
