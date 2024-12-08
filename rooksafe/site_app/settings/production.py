import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Load the .env file
load_dotenv()

schema = os.environ.get('DB_SCHEMA', "public") # si no encuentra el schema enviado por el .env, es publico por defecto

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'OPTIONS': {
             'options': f'-c search_path={schema}'  # Usar un schema diferente
         },
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': int(os.environ['DB_PORT']),
    }
}
