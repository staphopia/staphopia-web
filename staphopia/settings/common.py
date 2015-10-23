'''
Django settings for staphopia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
'''
import os

from staphopia.settings.private import *

'''----------------------------------------------------------------------------
Common
----------------------------------------------------------------------------'''
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

'''----------------------------------------------------------------------------
Applications
----------------------------------------------------------------------------'''
INSTALLED_APPS = (
    'rest_framework',

    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'registration',
    'crispy_forms',
    'django_email_changer',
    'django_extensions',
    'django_datatables_view',

    # Staphopia Related
    'staphopia',
    'autofill',
    'sample',
    'ena',
    'assembly',
    'gene',
    'mlst',
    'sequence',
    'variant',
    'kmer',
    'resistance',
    'sccmec'
)

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# django_email_changer
EMAIL_CHANGE_NOTIFICATION_SUBJECT = ('[Email Update] - Please verify '
                                     'Staphopia email update')
EMAIL_CHANGE_NOTIFICATION_FROM = ("Staphopia's Friendly Robot "
                                  "<usa300@staphopia.com>")


'''----------------------------------------------------------------------------
REST API
----------------------------------------------------------------------------'''
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGINATE_BY': 25
}

'''----------------------------------------------------------------------------
Middleware
----------------------------------------------------------------------------'''
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'staphopia.middleware.LoginRequiredMiddleware',
)

'''----------------------------------------------------------------------------
Static
----------------------------------------------------------------------------'''
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

'''----------------------------------------------------------------------------
Template
----------------------------------------------------------------------------'''
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

'''----------------------------------------------------------------------------
Staphopia
----------------------------------------------------------------------------'''
ROOT_URLCONF = 'staphopia.urls'
WSGI_APPLICATION = 'staphopia.wsgi.application'
DEFAULT_FROM_EMAIL = "Staphopia's Friendly Robot <usa300@staphopia.com>"
LOGIN_URL = '/accounts/login/'
LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^samples/',
    r'^top10/',
    r'^contact/',
    r'^accounts/login/',
    r'^accounts/register/',
    r'^accounts/activate/',
    r'^admin/',
)

'''----------------------------------------------------------------------------
Internationalization
https://docs.djangoproject.com/en/1.6/topics/i18n/
----------------------------------------------------------------------------'''
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
