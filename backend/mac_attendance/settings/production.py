"""
Django settings for mac_attendance project - PRODUCTION configuration.

Configuración específica para entorno de producción.
Hereda de base.py y sobreescribe/agrega configuraciones de producción.
"""

from .base import *  # noqa
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts - PRODUCCIÓN (NO permitir localhost)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError(
        "⚠️  ERROR: ALLOWED_HOSTS debe configurarse en producción (DEBUG=False). "
        "Ejemplo: ALLOWED_HOSTS=132.248.80.77,tudominio.com,www.tudominio.com"
    )

# CORS Settings - PRODUCCIÓN (solo HTTPS, NO localhost)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

# Validar que se hayan configurado orígenes en producción
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == ['']:
    raise ValueError(
        "⚠️  ERROR: CORS_ALLOWED_ORIGINS debe configurarse en producción. "
        "Ejemplo: CORS_ALLOWED_ORIGINS=https://132.248.80.77,https://tudominio.com"
    )

# Validar que TODOS los orígenes usen HTTPS
for origin in CORS_ALLOWED_ORIGINS:
    if not origin.startswith('https://'):
        raise ValueError(
            f"⚠️  ERROR: En producción, todos los orígenes deben usar HTTPS. "
            f"Origen inválido: {origin}"
        )

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Proxy Settings (para uso detrás de nginx/apache)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Rate Limiting - ACTIVADO en producción
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'

# Cache Configuration - Puede usar Redis/Memcached en producción
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ratelimit-cache',
    }
}
# TODO: Para mejor rendimiento en producción, considerar Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Logging Configuration - Archivos en producción
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
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',  # noqa
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',  # noqa
            'formatter': 'audit',
        },
        'audit_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'audit.log',  # noqa
            'formatter': 'audit',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'authentication.audit': {
            'handlers': ['console', 'audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_ratelimit': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Email backend - Real en producción (requiere configuración SMTP)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@mac-fes.unam.mx')

# Admins - Para recibir emails de errores 500
# ADMINS = [
#     ('Admin MAC', 'admin@mac-fes.unam.mx'),
# ]
# MANAGERS = ADMINS
