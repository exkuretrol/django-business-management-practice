from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    取得可索引物件的第 i 個元素。
    """
    return indexable[i]
