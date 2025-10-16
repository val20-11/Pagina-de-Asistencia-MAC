"""
URL configuration for mac_attendance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
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
    from django.http import HttpResponse
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Documentation - Sistema MAC</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .endpoint {
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                margin-right: 10px;
            }
            .GET { background: #28a745; color: white; }
            .POST { background: #007bff; color: white; }
            .PUT { background: #ffc107; color: black; }
            .DELETE { background: #dc3545; color: white; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .auth-badge {
                display: inline-block;
                padding: 4px 10px;
                background: #ff6b6b;
                color: white;
                border-radius: 4px;
                font-size: 11px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 API Documentation</h1>
            <p>Sistema de Asistencia MAC - FES Acatlán UNAM</p>
            <p><strong>Version:</strong> 1.0.0 | <strong>Base URL:</strong> /api/</p>
        </div>

        <div class="endpoint">
            <h2>🔐 Authentication Endpoints</h2>

            <h3><span class="method POST">POST</span> /api/auth/login/</h3>
            <p>Iniciar sesión con número de cuenta</p>
            <pre><code>{
  "account_number": "1234567"
}</code></pre>

            <h3><span class="method GET">GET</span> /api/auth/profile/ <span class="auth-badge">AUTH</span></h3>
            <p>Obtener perfil del usuario autenticado</p>

            <h3><span class="method POST">POST</span> /api/auth/token/refresh/</h3>
            <p>Refrescar access token</p>
        </div>

        <div class="endpoint">
            <h2>📅 Events Endpoints</h2>

            <h3><span class="method GET">GET</span> /api/events/</h3>
            <p>Listar todos los eventos activos</p>

            <h3><span class="method POST">POST</span> /api/events/external/register/ <span class="auth-badge">AUTH</span></h3>
            <p>Registrar un usuario externo para eventos</p>
        </div>

        <div class="endpoint">
            <h2>✅ Attendance Endpoints</h2>

            <h3><span class="method POST">POST</span> /api/attendance/ <span class="auth-badge">AUTH</span></h3>
            <p>Registrar asistencia a un evento</p>

            <h3><span class="method GET">GET</span> /api/attendance/stats/ <span class="auth-badge">AUTH</span></h3>
            <p>Obtener estadísticas de asistencia del usuario</p>

            <h3><span class="method GET">GET</span> /api/attendance/my/ <span class="auth-badge">AUTH</span></h3>
            <p>Obtener mis asistencias registradas</p>
        </div>

        <div class="endpoint">
            <h2>🔑 Authentication</h2>
            <p>La API utiliza <strong>JWT (JSON Web Tokens)</strong> para autenticación.</p>
            <p>Para endpoints que requieren autenticación, incluye el header:</p>
            <pre><code>Authorization: Bearer &lt;your_access_token&gt;</code></pre>
        </div>

        <div class="endpoint">
            <h2>📖 Quick Links</h2>
            <ul>
                <li><a href="/api/">API Root (JSON)</a></li>
                <li><a href="/admin/">Admin Panel</a></li>
                <li><a href="/">Frontend Application</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('', api_root, name='api_root'),
    path('api/', api_root, name='api_root_alt'),
    path('api/docs/', api_docs, name='api_docs'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/events/', include('events.urls')),
    path('api/attendance/', include('attendance.urls')),
]