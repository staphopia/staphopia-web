from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def site_env():
    return getattr(settings, 'SITE_ENV', "")
