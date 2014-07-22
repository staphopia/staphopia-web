from staphopia.settings.common import *

'''-----------------------------------------------------------------------------
SECURITY WARNING: don't run with debug turned on in production!
-----------------------------------------------------------------------------'''
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['0.0.0.0:80']



'''-----------------------------------------------------------------------------
Database
https://docs.djangoproject.com/en/1.6/ref/settings/#databases
-----------------------------------------------------------------------------'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/1.6/howto/static-files/
-----------------------------------------------------------------------------'''
STATIC_URL = '/static/'
