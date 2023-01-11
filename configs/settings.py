"""
Django settings for configs project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os.path
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = bool(os.getenv("DEBUG"))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split()
# ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGIN = ["https://durak-roll.itec.by"]#, "https://durak-roll.itec.by", "0.0.0.0:8888", ]
# CSRF_TRUSTED_ORIGIN = os.getenv("CSRF_TRUSTED_ORIGIN")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "daphne",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'django_celery_beat',
    'django_celery_results',
    'ckeditor',
    'ckeditor_uploader',
    'social_django',

    "ws_chat",
    'accaunts',
    'start_all_template',
    'content_manager',
    'support_chat',
    'api_router',
    'caseapp',
    'bot_payment',

    'pay',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware',
    "configs.middleware.check_add_ip_au.BanIPandAgentMiddleware",
]

ROOT_URLCONF = 'configs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'configs.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        # 'PORT': os.getenv('DB_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'start_all_template/static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accaunts.CustomUser'

AUTHENTICATION_BACKENDS = [
    # 'social_core.backends.vk.VKOAuth2', # выключен в пользу кастомного
    'accaunts.backends.CustomVKOAuth2',
    # 'social_core.backends.google.GoogleOAuth2', # выключен в пользу кастомного
    'accaunts.backends.CustomGoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = os.getenv("SOCIAL_AUTH_LOGIN_REDIRECT_URL")
SOCIAL_AUTH_JSONFIELD_ENABLED = os.getenv("SOCIAL_AUTH_JSONFIELD_ENABLED")
SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_VK_OAUTH2_KEY")
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_VK_OAUTH2_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
LOGIN_ERROR_URL = "/profil"
LOGOUT_REDIRECT_URL = "/profil"

CKEDITOR_UPLOAD_PATH = ''
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            [
                'Styles', 'Format', 'Font', 'FontSize', 'BGColor', 'TextColor', "-",
                'Bold', 'Italic', 'Underline', "SpecialChar", 'RemoveFormat', "Undo", "Redo", "NumberedList", "-",
                "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock", "-",
            ],
        ]
    }
}
# Channels
ASGI_APPLICATION = "configs.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("durak_redis_stack", 6379)],
        },
    },
}

# REDIS
REDIS_URL_STACK = os.getenv("REDIS_URL_STACK")
# CELERY
REDIS_URL = os.getenv("REDIS_URL")
BROKER_URL = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = True

"""freekassa"""
MERCHANT_ID = os.getenv('MERCHANT_ID')  # ID Вашего магазина
SECRET_WORD = os.getenv('SECRET_WORD')  # Секретное слово

# bot payment
HOST_URL = os.getenv('HOST_URL')
ID_SHIFT = int(os.getenv('ID_SHIFT'))
