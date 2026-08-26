import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security: Use environment variables with secure defaults
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CHANGE-ME-IN-PRODUCTION')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,raspberrypi").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'casa.inventory',
    'django_filters',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'casa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]},
    },
]

WSGI_APPLICATION = 'casa.wsgi.application'

database_engine = os.getenv("DB_ENGINE", "django.db.backends.mysql")
if "pytest" in sys.modules:
    database_engine = os.getenv("TEST_DB_ENGINE", "django.db.backends.sqlite3")

if database_engine == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": database_engine,
            "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": database_engine,
            "NAME": os.getenv("DB_NAME", "casa_inventory"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "3306"),
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

LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
SERVE_STATIC = os.getenv("SERVE_STATIC", "true").lower() == "true"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ]
}

configured_csrf_origins = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,https://localhost:8000'
).split(',')
https_allowed_hosts = [
    f'https://{host}' for host in ALLOWED_HOSTS if host not in {'*', 'localhost', '127.0.0.1'}
]
# Um host público permitido também deve aceitar formulários enviados pela sua
# própria origem HTTPS (por exemplo, https://192.168.1.78).
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(origin.strip() for origin in [*configured_csrf_origins, *https_allowed_hosts] if origin.strip())
)

# Security Headers
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "style-src": (
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://fonts.googleapis.com",
    ),
    "font-src": ("'self'", "https://fonts.gstatic.com"),
    "script-src": ("'self'", "https://cdn.jsdelivr.net", "https://unpkg.com"),
    "connect-src": (
        "'self'",
        "https://world.openproductsfacts.org",
        "https://world.openbeautyfacts.org",
        "https://world.openpetfoodfacts.org",
        "https://world.openfoodfacts.org",
    ),
}

# Only in production
if not DEBUG and "pytest" not in sys.modules:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Logging Configuration
import logging.config

from casa.logging_config import LOGGING

logging.config.dictConfig(LOGGING)

# REST Framework Authentication
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}
