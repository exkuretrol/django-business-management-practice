from os.path import splitext

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    def __str__(self):
        return self.username


class File(models.Model):
    """
    系統的檔案。被使用於 :model:`announcement.Announcement`。
    """

    name = models.CharField(max_length=100, verbose_name=_("名稱"))
    file_hash = models.CharField(max_length=64, verbose_name=_("檔案雜湊"), null=True)
    file_path = models.FileField(
        upload_to="attachments/%Y/%m/%d", verbose_name=_("檔案")
    )
    create_datetime = models.DateTimeField(
        default=timezone.now, verbose_name=_("創建時間")
    )

    def __str__(self):
        return f"{self.create_datetime:%Y-%m-%d} - {self.name}"

    class Meta:
        verbose_name = _("檔案")
        verbose_name_plural = _("檔案")
