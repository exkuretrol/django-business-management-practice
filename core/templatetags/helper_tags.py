from django import template

register = template.Library()


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
    return url_name in []
