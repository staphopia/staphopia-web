from django import template
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def current_domain():
    return Site.objects.get_current().domain
