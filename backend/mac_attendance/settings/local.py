"""
Django settings for mac_attendance project - LOCAL/DEVELOPMENT configuration.

Configuración específica para entorno de desarrollo local.
Hereda de base.py y sobreescribe/agrega configuraciones de desarrollo.
"""

from .base import *  # noqa
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts en desarrollo
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,nginx,backend'
).split(',')

# CORS Settings - Desarrollo (permitir localhost)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost,http://127.0.0.1,http://localhost:80,https://localhost,https://127.0.0.1'
).split(',')

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost,http://127.0.0.1,https://localhost,https://127.0.0.1'
).split(',')

# Security Settings - Relajadas para desarrollo
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Rate Limiting - Desactivado en desarrollo
RATELIMIT_ENABLE = False
RATELIMIT_USE_CACHE = 'default'

# Cache Configuration - LocMem para desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ratelimit-cache',
    }
}

# Logging Configuration - Solo consola en desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'audit': {
            'format': '[AUDIT] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'authentication.audit': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_ratelimit': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Email backend - Console para desarrollo (imprime en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Mostrar toolbar de debug si está instalada (opcional)
# if 'debug_toolbar' not in INSTALLED_APPS:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
#     INTERNAL_IPS = ['127.0.0.1']
