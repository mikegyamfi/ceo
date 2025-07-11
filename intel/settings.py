"""
Django settings for intel project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'intel_app/templates'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
# SECRET_KEY = "DGFYUGEUGFEFE"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'www.bestpluggh.com',
    'bestplug-ceoofwealth-lsnoo.ondigitalocean.app',
    'bestplug-2adzs.ondigitalocean.app',
    '127.0.0.1',
    'localhost'
]


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'intel_app',
    'storages',
]

# CACHES = {
#     # … default cache config and others
#     "select2": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/2",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
#
# # Tell select2 which cache configuration to use:
# SELECT2_CACHE_BACKEND = "select2"

JAZZMIN_SETTINGS = {
    # Basic branding
    "site_title": "BestPlug",
    "site_header": "BestPlug",
    "site_brand": "BestPlug",
    "welcome_sign": "Welcome to the BestPlug Admin",
    "copyright": "Bestplug-CEOofWealth",
    "custom_css": 'css/admin.css',
    "user_avatar": 'user',

    # Sidebar order and grouping
"order_with_respect_to": [
        # First, keep Django’s built-in auth section
        "auth",

        # Then list every intel_app model in the order you want:
        "intel_app.CustomUser",
        "intel_app.AdminInfo",
        "intel_app.Announcement",

        "intel_app.Brand",
        "intel_app.Category",
        "intel_app.Size",
        "intel_app.Color",
        "intel_app.Product",
        "intel_app.ProductImage",
        "intel_app.Cart",

        "intel_app.Order",
        "intel_app.OrderItem",

        "intel_app.Payment",
        "intel_app.TopUpRequest",
        "intel_app.WalletTransaction",

        "intel_app.AgentIshareBundlePrice",
        "intel_app.SuperAgentIshareBundlePrice",
        "intel_app.IshareBundlePrice",
        "intel_app.AgentBigTimeBundlePrice",
        "intel_app.SuperAgentBigTimeBundlePrice",
        "intel_app.BigTimeBundlePrice",
        "intel_app.AgentTelecelBundlePrice",
        "intel_app.SuperAgentTelecelBundlePrice",
        "intel_app.TelecelBundlePrice",
        "intel_app.MTNBundlePrice",
        "intel_app.AgentMTNBundlePrice",
        "intel_app.SuperAgentMTNBundlePrice",

        "intel_app.AFARegistration",

        "intel_app.IShareBundleTransaction",
        "intel_app.BigTimeTransaction",
        "intel_app.MTNTransaction",
        "intel_app.TelecelTransaction",

        "intel_app.CheckerType",
        "intel_app.ResultChecker",
        "intel_app.ResultCheckerTransaction",

        "intel_app.Currency",
        "intel_app.CurrencyRateHistory",
        "intel_app.CurrencyTransaction",
    ],

    # (Optional) icons for each group
    "icons": {
        "intel_app.CustomUser": "fas fa-user",
        "intel_app.Product": "fas fa-box",
        "intel_app.Order": "fas fa-shopping-cart",
        "intel_app.Payment": "fas fa-credit-card",
        "intel_app.Currency": "fas fa-dollar-sign",
        # …
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'intel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'intel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': config("DATABASE_HOST"),
        'PORT': config("DATABASE_PORT"),
        'NAME': 'db',
        'USER': config("DATABASE_USERNAME"),
        'PASSWORD': config("DATABASE_PASSWORD"),
        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'assets/'
STATICFILES_DIRS = [BASE_DIR / 'intel_app/static']

MEDIA_ROOT = os.path.join(BASE_DIR, 'intel_app/media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
AUTH_USER_MODEL = 'intel_app.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")

AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")

AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_DEFAULT_ACL = 'public-read'

AWS_LOCATION = config("AWS_LOCATION")

MEDIA_LOCATION = 'media'
MEDIA_URL = 'https://%s/%s/' % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# MEDIA_URL = '/media/'
