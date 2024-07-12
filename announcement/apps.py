from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnnouncementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "announcement"
    verbose_name = _("公告")
