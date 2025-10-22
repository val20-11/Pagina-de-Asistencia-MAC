"""
Middleware personalizado para autenticación y auditoría
"""
from django.utils.deprecation import MiddlewareMixin
from .audit import AuditLog


class DisableCSRFOnAPIMiddleware(MiddlewareMixin):
    """
    Middleware para deshabilitar CSRF en endpoints de API que usan JWT.
    Los endpoints que comienzan con /api/ están exentos de CSRF ya que usan JWT.
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditar eventos de seguridad importantes.
    """
    def process_response(self, request, response):
        # Auditar intentos de login fallidos
        if request.path == '/api/token/' and response.status_code == 401:
            AuditLog.log(
                category='AUTH',
                action='LOGIN_FAILED',
                message='Intento de login fallido',
                request=request,
                severity='WARNING',
                success=False,
                status_code=response.status_code
            )

        # Auditar accesos no autorizados
        if response.status_code == 403:
            AuditLog.log(
                category='SECURITY',
                action='ACCESS_DENIED',
                message='Acceso denegado',
                request=request,
                severity='WARNING',
                success=False,
                status_code=response.status_code
            )

        return response
