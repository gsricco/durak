from django import template

register = template.Library()


@register.filter(name="div")
def div(value, arg):
    return round(int(value) / int(arg))
