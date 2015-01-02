from staphopia.settings.common import *

'''----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production
----------------------------------------------------------------------------'''
DEBUG = True
TEMPLATE_DEBUG = True
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
        'PASSWORD': 'ca1e0a1ac201e4',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


'''----------------------------------------------------------------------------
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
----------------------------------------------------------------------------'''
STATIC_URL = '/static/'
