from django import template

register = template.Library()

@register.filter
def previous_page(pageNum):
    return int(pageNum) - 1


@register.filter
def next_page(pageNum):
    return int(pageNum) + 1

@register.filter
def is_active_page(pageNum, page):
    if int(pageNum) == int(page):
        return True
    else :
        return False

@register.filter
def is_exits_previous_page(pageNum, page):
    if int(pageNum) <= int(page):
        return True
    else :
        return False

@register.filter
def is_exits_next_page(pageNum, count):
    if int(pageNum) >= int(count):
        return True
    else :
        return False

@register.filter
def index(List, i):
    return List[int(i)]
