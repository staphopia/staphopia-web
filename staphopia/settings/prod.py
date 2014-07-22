from staphopia.settings.common import *
from staphopia.settings.aws import *

'''-----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production!
-----------------------------------------------------------------------------'''
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']



'''-----------------------------------------------------------------------------
Database
https://docs.djangoproject.com/en/1.6/ref/settings/#databases
-----------------------------------------------------------------------------'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'staphopia_django',
        'USER' : 'django',
        'PASSWORD' : 'ca1e0a1ac201e4',
        'HOST' : 'staphopia-django.cpphjf4vstco.us-east-1.rds.amazonaws.com',
        'PORT' : '5432',
    },
    'staphopia': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'staphopia',
        'USER' : 'DeepThought',
        'PASSWORD' : 'da208f6115574ef429684fa388b04fc958da12c7d2bd2c4d',
        'HOST' : 'staphopiadev.cpphjf4vstco.us-east-1.rds.amazonaws.com',
        'PORT' : '29466',
    }
}



'''-----------------------------------------------------------------------------
Static files via Amazon S3 (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
-----------------------------------------------------------------------------'''
INSTALLED_APPS += ('storages',)
AWS_STORAGE_BUCKET_NAME = "staphopia-django"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
