"""
Settings module for mac_attendance project.

Este módulo carga automáticamente la configuración correcta basándose
en la variable de entorno DJANGO_SETTINGS_MODULE.

Estructura:
- base.py: Configuración común para todos los entornos
- local.py: Configuración para desarrollo local
- production.py: Configuración para producción

Uso:
- Desarrollo: DJANGO_SETTINGS_MODULE=mac_attendance.settings.local
- Producción: DJANGO_SETTINGS_MODULE=mac_attendance.settings.production
"""

import os

# Determinar qué configuración cargar basándose en la variable de entorno
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'production')

if DJANGO_ENV == 'local':
    from .local import *  # noqa
elif DJANGO_ENV == 'production':
    from .production import *  # noqa
else:
    # Por defecto, usar producción (más seguro)
    from .production import *  # noqa
