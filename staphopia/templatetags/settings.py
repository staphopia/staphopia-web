from django import template
from django.conf import settings
from rest_framework.authtoken.models import Token

register = template.Library()


# settings value
@register.assignment_tag
def site_env():
    return getattr(settings, 'SITE_ENV', "")

@register.assignment_tag
def get_token(user):
    return Token.objects.get(user=user)
