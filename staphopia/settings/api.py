from staphopia.settings.common import *
from staphopia.settings.private import DEV_PASS

'''----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production!
----------------------------------------------------------------------------'''
DEBUG = False
ALLOWED_HOSTS = ['*']
VIEW_ALL_SAMPLES = False
USE_API = True

'''----------------------------------------------------------------------------
Applications
----------------------------------------------------------------------------'''
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
REST API
----------------------------------------------------------------------------'''
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ],
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
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
----------------------------------------------------------------------------'''
STATIC_URL = '/static/'

SITE_ID = 3
SITE_ENV = 'www'

LOGIN_URL = '/accounts/login/'
LOGIN_EXEMPT_URLS = (
    r'^accounts/login/',
    r'^api/*',
    r'^sample/*',
    r'^',
)
