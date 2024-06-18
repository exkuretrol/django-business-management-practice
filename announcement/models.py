from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    author = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    effective_start_date = models.DateField(default=timezone.now)
    effective_end_date = models.DateField(default=timezone.datetime.max)
    attachments = models.ManyToManyField("AnnouncementAttachment", blank=True)
    branchs = models.ManyToManyField("branch.Branch", blank=True)


class AnnouncementAttachment(models.Model):
    name = models.CharField(max_length=100)
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d/")
    create_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.create_datetime:%Y-%m-%d} - {self.name}"
