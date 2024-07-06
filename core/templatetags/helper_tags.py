from django import template
from django.core import serializers

register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def is_announcement_category(url_name):
    return url_name in [
        "announcement_home",
        "announcement_create",
        "announcement_list",
        "announcement_detail",
        "announcement_update",
    ]


@register.filter
def is_checklist_category(url_name):
    return url_name in [
        "checklist_home",
        "checklist_create",
        "checklist_list",
        "checklist_export",
        "checklist_temporary_export",
    ]


@register.filter
def json(data):
    return serializers.serialize("json", data)
