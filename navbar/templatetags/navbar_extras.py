from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """Check if the value starts with the given argument"""
    return value.startswith(arg) 