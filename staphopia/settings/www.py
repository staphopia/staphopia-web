from staphopia.settings.common import *
from staphopia.settings.private import DEV_PASS

'''----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production!
----------------------------------------------------------------------------'''
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['*']


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
        'HOST': 'staphopia.cpphjf4vstco.us-east-1.rds.amazonaws.com',
        'PORT': '30022',
    }
}


'''----------------------------------------------------------------------------
Static files via Amazon S3 (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
----------------------------------------------------------------------------'''
#INSTALLED_APPS += ('storages',)
#AWS_STORAGE_BUCKET_NAME = "staphopia-django"
#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
#STATIC_URL = S3_URL
STATIC_URL = '/static/'
SITE_ID = 1
SITE_ENV = 'www'
