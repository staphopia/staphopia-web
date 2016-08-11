from django.contrib import admin
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ('user',)

admin.site.register(Token, TokenAdmin)
