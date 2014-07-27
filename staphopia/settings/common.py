'''
Django settings for staphopia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
'''
import os
import re

from staphopia.settings.private import *

'''-----------------------------------------------------------------------------
Common 
-----------------------------------------------------------------------------'''
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



'''-----------------------------------------------------------------------------
Applications 
-----------------------------------------------------------------------------'''
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'south',
    'registration',
    'crispy_forms',
    
    'database',
    'autofill',
    'samples',
)

# django-registration
ACCOUNT_ACTIVATION_DAYS=7
CRISPY_TEMPLATE_PACK = 'bootstrap3'

'''-----------------------------------------------------------------------------
Database 
-----------------------------------------------------------------------------'''
DATABASE_ROUTERS = ('database.routers.StaphopiaRouter',)



'''-----------------------------------------------------------------------------
Middleware 
-----------------------------------------------------------------------------'''
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'staphopia.middleware.LoginRequiredMiddleware',
)



'''-----------------------------------------------------------------------------
Static 
-----------------------------------------------------------------------------'''
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = ( 
    'django.contrib.staticfiles.finders.FileSystemFinder', 
    'django.contrib.staticfiles.finders.AppDirectoriesFinder', 
) 



'''-----------------------------------------------------------------------------
Template 
-----------------------------------------------------------------------------'''
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

AUTOLOAD_TEMPLATETAGS = (
    'staphopia.templatetags.navbar',
    'database.templatetags.top10',
)



'''-----------------------------------------------------------------------------
Staphopia 
-----------------------------------------------------------------------------'''
ROOT_URLCONF = 'staphopia.urls'
WSGI_APPLICATION = 'staphopia.wsgi.application'
DEFAULT_FROM_EMAIL = "Staphopia's Friendly Robot <usa300@staphopia.com>"
LOGIN_URL = '/accounts/login/'
LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^genomes/',
    r'^top10/', 
    r'^contact/',
    r'^accounts/login/',
    r'^accounts/register/',
)

'''-----------------------------------------------------------------------------
Internationalization
https://docs.djangoproject.com/en/1.6/topics/i18n/
-----------------------------------------------------------------------------'''
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

