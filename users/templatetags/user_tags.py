from django import template

register = template.Library()

@register.filter
def has_attr(value, arg):
    return hasattr(value, arg)
