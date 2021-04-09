"""
Django settings for staphopia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
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
    'rest_framework.authtoken',

    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',

    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'crispy_forms',
    'django_extensions',

    # Staphopia Related
    'staphopia',
    'annotation',
    'assembly',
    'cgmlst',
    'ena',
    'gene',
    'kmer',
    'metadata',
    'mlst',
    'plasmid',
    'publication',
    'resistance',
    'sample',
    'sccmec',
    'search',
    'sequence',
    'tag',
    'variant',
    'version',
    'virulence'
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'
ORGS_SLUGFIELD = 'django_extensions.db.fields.AutoSlugField'
ADMINS = [
    ('Robert Petit', 'rpetit@emory.edu')
]
'''----------------------------------------------------------------------------
REST API
----------------------------------------------------------------------------'''
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
        'user': '100000000000/day'
    },
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.PageNumberPagination'
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'PAGE_SIZE': 100
}
MAX_IDS_PER_QUERY = 5000

'''----------------------------------------------------------------------------
Middleware
----------------------------------------------------------------------------'''
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'staphopia.middleware.LoginRequiredMiddleware'
]
APPEND_SLASH = True

'''----------------------------------------------------------------------------
Static
----------------------------------------------------------------------------'''
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

'''----------------------------------------------------------------------------
Template
----------------------------------------------------------------------------'''
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
            'loaders':[
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

'''----------------------------------------------------------------------------
Staphopia
----------------------------------------------------------------------------'''
ROOT_URLCONF = 'staphopia.urls'
WSGI_APPLICATION = 'staphopia.wsgi.application'

'''----------------------------------------------------------------------------
Internationalization
https://docs.djangoproject.com/en/1.6/topics/i18n/
----------------------------------------------------------------------------'''
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
