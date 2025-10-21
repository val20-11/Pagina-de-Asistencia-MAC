"""
Vistas del proyecto principal MAC Attendance
"""
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request):
    """API root endpoint - Returns comprehensive API information (Protected)"""
    return JsonResponse({
        'name': 'Sistema de Asistencia MAC - API',
        'version': '1.0.0',
        'description': 'API REST para el Sistema de Asistencia MAC - FES Acatlán UNAM',
        'documentation': {
            'main': '/api/docs/',
            'swagger': '/api/swagger/',
            'redoc': '/api/redoc/',
        },
        'endpoints': {
            'authentication': {
                'login': {
                    'url': '/api/auth/login/',
                    'method': 'POST',
                    'description': 'Iniciar sesión con número de cuenta',
                    'auth_required': False,
                },
                'logout': {
                    'url': '/api/auth/logout/',
                    'method': 'POST',
                    'description': 'Cerrar sesión',
                    'auth_required': True,
                },
                'profile': {
                    'url': '/api/auth/profile/',
                    'method': 'GET',
                    'description': 'Obtener perfil de usuario',
                    'auth_required': True,
                },
                'check_auth': {
                    'url': '/api/auth/check-auth/',
                    'method': 'GET',
                    'description': 'Verificar estado de autenticación',
                    'auth_required': False,
                },
                'token_refresh': {
                    'url': '/api/auth/token/refresh/',
                    'method': 'POST',
                    'description': 'Refrescar access token',
                    'auth_required': False,
                },
                'system_config': {
                    'url': '/api/auth/system-config/',
                    'method': 'GET',
                    'description': 'Obtener configuración del sistema',
                    'auth_required': True,
                },
            },
            'events': {
                'list': {
                    'url': '/api/events/',
                    'method': 'GET',
                    'description': 'Listar todos los eventos',
                    'auth_required': False,
                },
                'register_external': {
                    'url': '/api/events/external/register/',
                    'method': 'POST',
                    'description': 'Registrar usuario externo',
                    'auth_required': True,
                },
                'search_external': {
                    'url': '/api/events/external/search/',
                    'method': 'GET',
                    'description': 'Buscar usuarios externos',
                    'auth_required': True,
                },
                'approve_external': {
                    'url': '/api/events/external/<user_id>/approve/',
                    'method': 'POST',
                    'description': 'Aprobar usuario externo',
                    'auth_required': True,
                },
            },
            'attendance': {
                'register': {
                    'url': '/api/attendance/',
                    'method': 'POST',
                    'description': 'Registrar asistencia a evento',
                    'auth_required': True,
                },
                'stats': {
                    'url': '/api/attendance/stats/',
                    'method': 'GET',
                    'description': 'Obtener estadísticas de asistencia',
                    'auth_required': True,
                },
                'recent': {
                    'url': '/api/attendance/recent/',
                    'method': 'GET',
                    'description': 'Obtener asistencias recientes',
                    'auth_required': True,
                },
                'my_attendances': {
                    'url': '/api/attendance/my/',
                    'method': 'GET',
                    'description': 'Obtener mis asistencias',
                    'auth_required': True,
                },
            },
        },
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'token_lifetime': '1 hour',
            'refresh_token_lifetime': '7 days',
        },
        'status': 'operational',
        'server_time': request.build_absolute_uri(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_docs(request):
    """API documentation endpoint (Protected)"""
    return render(request, 'api_docs.html')
