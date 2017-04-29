import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def jsonify(data, safe=True):
    data = json.dumps(data, indent=2)
    if safe:
        data = mark_safe(data)
    return data


@register.filter
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return None
    return