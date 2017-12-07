from django import template
from django.conf import settings
from rest_framework.authtoken.models import Token

register = template.Library()


# settings value
@register.simple_tag
def site_env():
    return getattr(settings, 'SITE_ENV', "")


@register.simple_tag
def get_token(user):
    return Token.objects.get(user=user)
