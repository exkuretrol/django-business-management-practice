"""
Django settings for django_project project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

APP_NAME = env.str("APP_NAME", default="*")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    f"{APP_NAME}.fly.dev",
]
INTERNAL_IPS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = [f"https://{APP_NAME}.fly.dev"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # using whitenoise to serve static files
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # 3rd party apps
    "crispy_forms",
    "crispy_bootstrap5",
    "webpack_loader",
    "django_quill",
    "django_tables2",
    "django_filters",
    "debug_toolbar",
    "django_extensions",
    # local apps
    "core",
    "branch",
    "announcement",
    "checklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # whitenoise middleware should be placed directly after the Django SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 3rd party middleware
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {"default": env.dj_db_url("POSTGRE_URL", default="sqlite:///db.sqlite3")}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "core.User"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGES = [
    ("zh-hant", "Traditional Chinese"),
    ("en-us", "English"),
]

LANGUAGE_CODE = "zh-Hant"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

ENVIRONMENT = env.str("ENVIRONMENT", default="Development")
if ENVIRONMENT == "Development":
    MEDIA_ROOT = BASE_DIR / "media"
elif ENVIRONMENT == "Production":
    MEDIA_ROOT = "/data/media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "webpack_bundles/",
        "CACHE": not DEBUG,
        "STATS_FILE": BASE_DIR / "webpack-stats.json",
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 3rd party apps settings
# Quill settings
QUILL_CONFIGS = {
    "default": {
        "theme": "snow",
        "modules": {
            "syntax": False,
            "toolbar": [
                ["bold", "italic", "underline"],
                ["link"],
                ["clean"],
            ],
        },
    }
}

# Django-tables2 settings
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5-responsive.html"
