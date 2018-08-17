#DEBUG = False
DEBUG = True

SECRET_KEY = '123'

ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/db.sqlite3',
    }
}
