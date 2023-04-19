from django import template
from django.utils.timezone import now
from datetime import datetime

register = template.Library()

@register.filter
def timediff(value):
    return value.strftime("%H:%M")
    # diff = now() - value
    # if diff.days >= 1:
    #     return f"{diff.days} days ago"
    # else:
    #     return f"{diff.seconds//3600}:{diff.seconds//60}"#diff.time().strftime('%H:%M')


@register.filter
def sliceUUID(uuid):
    return str(uuid)[:8]


@register.filter
def drop_region_code(lang):
    return lang.split("-")[0]