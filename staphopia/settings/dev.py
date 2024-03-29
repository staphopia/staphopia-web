from staphopia.settings.common import *
from staphopia.settings.private import DEV_PASS

'''----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production
----------------------------------------------------------------------------'''
DEBUG = True
ALLOWED_HOSTS = ['*']
VIEW_ALL_SAMPLES = True
USE_API = True

INSTALLED_APPS = (
    'rest_framework',
    'rest_framework.authtoken',

    'django.contrib.sites',
    'django.contrib.admin',
    'registration',
    'django.contrib.auth',
    # 'django_email_changer',

    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'crispy_forms',
    'django_extensions',
    'django_datatables_view',

    # Staphopia Related
    'staphopia',
    'autofill',
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

'''----------------------------------------------------------------------------
Database
https://docs.djangoproject.com/en/1.6/ref/settings/#databases
----------------------------------------------------------------------------'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'staphopia',
        'USER': 'staphopia',
        'PASSWORD': DEV_PASS,
        'HOST': 'chlamy.genetics.emory.edu',
        'PORT': '29466',
    }
}


'''----------------------------------------------------------------------------
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
----------------------------------------------------------------------------'''
STATIC_URL = '/static/'

SITE_ID = 2
SITE_ENV = 'dev'

LOGIN_URL = '/accounts/login/'
LOGIN_EXEMPT_URLS = (
    r'^accounts/login/',
    r'^api/*',
    r'^',
)
