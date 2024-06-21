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
    author = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, verbose_name=_("標題"))
    content = QuillField(verbose_name=_("內容"))
    effective_start_date = models.DateField(
        default=timezone.now, verbose_name=_("生效起日")
    )
    effective_end_date = models.DateField(
        default=timezone.datetime.max, verbose_name=_("生效迄日")
    )
    attachments = models.ManyToManyField(
        "AnnouncementAttachment", blank=True, verbose_name=_("附件")
    )
    branchs = models.ManyToManyField(
        "branch.Branch", blank=True, verbose_name=_("門市")
    )
    status = models.PositiveSmallIntegerField(
        verbose_name=_("狀態"), default=StatusChoices.DRAFT
    )

    def get_absolute_url(self):
        return reverse("announcement_detail", kwargs={"pk": self.pk})


class AnnouncementAttachment(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("名稱"))
    attachment = models.FileField(
        upload_to="attachments/%Y/%m/%d/", verbose_name=_("附件")
    )
    create_datetime = models.DateTimeField(
        default=timezone.now, verbose_name=_("創建時間")
    )

    def __str__(self):
        return f"{self.create_datetime:%Y-%m-%d} - {self.name}"
