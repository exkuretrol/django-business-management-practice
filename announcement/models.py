import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_quill.fields import QuillField


class StatusChoices(models.IntegerChoices):
    DRAFT = 0, _("草稿")
    PUBLISHED = 1, _("已發佈")
    UNAVAILABLE = 9, _("已下架")


class Announcement(models.Model):
    """
    公告。公告的附件儲存於 :model:`core.File`。
    """

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("UUID")
    )
    author = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, verbose_name=_("標題"))
    content = QuillField(verbose_name=_("內容"))
    effective_start_date = models.DateField(
        default=timezone.now, verbose_name=_("生效起日")
    )
    effective_end_date = models.DateField(
        default=timezone.datetime.max, verbose_name=_("生效迄日")
    )
    attachments = models.ManyToManyField(
        "core.File", blank=True, verbose_name=_("附件")
    )
    branchs = models.ManyToManyField(
        "branch.Branch", blank=True, verbose_name=_("門市")
    )
    status = models.PositiveSmallIntegerField(
        verbose_name=_("狀態"),
        default=StatusChoices.DRAFT,
        choices=StatusChoices.choices,
    )
    created_at = models.DateTimeField(verbose_name=_("建立時間"), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_("最後更新時間"), auto_now=True)
    last_modified_by = models.ForeignKey(
        related_name="last_modified_announcements",
        verbose_name=_("最後更新者"),
        to="auth.User",
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
    )

    def get_absolute_url(self):
        return reverse("announcement:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.effective_start_date:%Y-%m-%d} - {self.title}"

    class Meta:
        verbose_name = _("公告")
        verbose_name_plural = _("公告")
