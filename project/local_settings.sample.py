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


COUNTERPARTY = '0xb4214d064518eed303d966f9ca0fc62ac8df20ee'
NODE_DOWNLOAD = 1
NODE_UPLOAD = 1
NODE_EXPOSE_PORT = 8080