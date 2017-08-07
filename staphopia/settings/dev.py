from staphopia.settings.common import *
from staphopia.settings.private import DEV_PASS

'''----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production
----------------------------------------------------------------------------'''
DEBUG = True
ALLOWED_HOSTS = ['0.0.0.0:80']


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
        'HOST': 'staphopia.genetics.emory.edu',
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
    r'^',
)
