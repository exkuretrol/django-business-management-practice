from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    取得可索引物件的第 i 個元素。
    """
    return indexable[i]


@register.filter
def is_announcement_category(url_name: str) -> bool:
    """
    過濾是否為公告的分類。
    """
    return url_name in [
        "announcement:index",
        "announcement:create",
        "announcement:branchs_list",
        "announcement:list",
        "announcement:detail",
        "announcement:update",
    ]


@register.filter
def is_checklist_category(url_name: str):
    """
    過濾是否為待做清單的分類。
    """
    return url_name in [
        "checklist:index",
        "checklist:create",
        "checklist:branchs_list",
        "checklist:list",
        "checklist:export",
        "checklist:temporary_export",
    ]
