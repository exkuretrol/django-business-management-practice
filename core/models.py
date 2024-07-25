import hashlib
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    def __str__(self):
        return self.username


def hash_file_name(instance, filename):
    return f"attachments/{uuid.uuid4().hex}"


class File(models.Model):
    """
    系統的檔案。被使用於 :model:`announcement.Announcement`。
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("名稱"))
    hash = models.CharField(
        max_length=64, verbose_name=_("雜湊"), null=True, editable=False
    )
    file = models.FileField(upload_to=hash_file_name, verbose_name=_("檔案"))
    extension = models.CharField(max_length=16, verbose_name=_("副檔名"), null=True)
    create_datetime = models.DateTimeField(
        default=timezone.now, verbose_name=_("創建時間")
    )

    def save(self, *args, **kwargs):
        sha256_hash = hashlib.sha256()
        with self.file.open("rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            self.hash = sha256_hash.hexdigest()

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.create_datetime:%Y-%m-%d} - {self.name}"

    class Meta:
        verbose_name = _("檔案")
        verbose_name_plural = _("檔案")
