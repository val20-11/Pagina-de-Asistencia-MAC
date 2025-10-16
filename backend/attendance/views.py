from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from authentication.models import UserProfile, ExternalUser
from events.models import Event
from .models import Attendance, AttendanceStats

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='POST', block=True)
def register_attendance(request):
    """Registrar asistencia - Solo asistentes: 60 registros por minuto"""
    if request.method == 'GET':
        return Response({
            'message': 'API de registro de asistencia activa',
            'methods': ['POST'],
            'required_fields': ['event_id', 'account_number']
        })

    # Verificar que el usuario autenticado sea asistente
    try:
        registrar_profile = request.user.userprofile
        if registrar_profile.user_type != 'assistant':
            return Response({
                'error': 'Solo los asistentes pueden registrar asistencias'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    event_id = request.data.get('event_id')
    account_number = request.data.get('account_number')
    
    if not event_id or not account_number:
        return Response({
            'error': 'Se requiere event_id y account_number'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar evento
    try:
        event = Event.objects.get(id=event_id, is_active=True)
    except Event.DoesNotExist:
        return Response({
            'error': 'Evento no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Buscar estudiante regular o usuario externo
    student_profile = None
    external_user = None
    attendee_name = None

    # Primero buscar en estudiantes regulares
    try:
        student_profile = UserProfile.objects.get(
            account_number=account_number,
            user_type='student'
        )
        attendee_name = student_profile.full_name
    except UserProfile.DoesNotExist:
        # Si no es estudiante, buscar en usuarios externos
        try:
            external_user = ExternalUser.objects.get(
                account_number=account_number,
                status='approved'
            )
            attendee_name = external_user.full_name
        except ExternalUser.DoesNotExist:
            return Response({
                'error': f'Usuario con número de cuenta {account_number} no encontrado o no aprobado'
            }, status=status.HTTP_404_NOT_FOUND)

    # Usar el asistente autenticado como registrador
    assistant_profile = registrar_profile

    # Verificar si ya tiene asistencia
    if student_profile:
        if Attendance.objects.filter(student=student_profile, event=event, is_valid=True).exists():
            return Response({
                'error': 'El estudiante ya tiene asistencia registrada para este evento'
            }, status=status.HTTP_400_BAD_REQUEST)
    elif external_user:
        if Attendance.objects.filter(external_user=external_user, event=event, is_valid=True).exists():
            return Response({
                'error': 'El usuario externo ya tiene asistencia registrada para este evento'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Crear asistencia
    try:
        attendance = Attendance.objects.create(
            student=student_profile,
            external_user=external_user,
            event=event,
            registered_by=assistant_profile,
            registration_method='manual'
        )

        return Response({
            'message': f'Asistencia registrada para {attendee_name}',
            'attendance_id': attendance.id,
            'event': event.title,
            'registered_by': assistant_profile.full_name,
            'attendee_type': 'student' if student_profile else 'external'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Error al crear asistencia: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='GET', block=True)
def get_student_stats(request):
    """Obtener estadísticas de estudiante: 30 consultas por minuto"""
    account_number = request.GET.get('account_number')

    if not account_number:
        return Response({'error': 'Se requiere account_number'}, status=400)

    # Verificar permisos: estudiantes solo pueden ver sus propias estadísticas
    try:
        requester_profile = request.user.userprofile

        # Si es estudiante, solo puede consultar sus propias estadísticas
        if requester_profile.user_type == 'student':
            if requester_profile.account_number != account_number:
                return Response({
                    'error': 'Solo puedes consultar tus propias estadísticas'
                }, status=status.HTTP_403_FORBIDDEN)
        # Asistentes pueden ver estadísticas de cualquier estudiante
        elif requester_profile.user_type != 'assistant':
            return Response({
                'error': 'No tienes permisos para consultar estadísticas'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        student_profile = UserProfile.objects.get(
            account_number=account_number,
            user_type='student'
        )
        stats, created = AttendanceStats.objects.get_or_create(
            student=student_profile
        )
        stats.update_stats()

        return Response({
            'total_events': stats.total_events,
            'attended_events': stats.attended_events,
            'attendance_percentage': stats.attendance_percentage
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def get_recent_attendances(request):
    """Obtener asistencias recientes - Solo asistentes: 60 consultas por minuto"""
    # Solo asistentes pueden ver asistencias recientes
    try:
        requester_profile = request.user.userprofile
        if requester_profile.user_type != 'assistant':
            return Response({
                'error': 'Solo los asistentes pueden consultar asistencias recientes'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    recent = Attendance.objects.select_related('student', 'event').order_by('-timestamp')[:5]

    data = []
    for attendance in recent:
        data.append({
            'attendee_name': attendance.attendee_name,
            'event_title': attendance.event.title,
            'timestamp': attendance.timestamp.strftime('%H:%M')
        })

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def get_my_attendances(request):
    """Obtener mis asistencias - Estudiantes pueden ver sus propias asistencias: 60 consultas por minuto"""
    account_number = request.GET.get('account_number')

    if not account_number:
        return Response({'error': 'Se requiere account_number'}, status=400)

    # Verificar permisos: estudiantes solo pueden ver sus propias asistencias
    try:
        requester_profile = request.user.userprofile

        # Si es estudiante, solo puede consultar sus propias asistencias
        if requester_profile.user_type == 'student':
            if requester_profile.account_number != account_number:
                return Response({
                    'error': 'Solo puedes consultar tus propias asistencias'
                }, status=status.HTTP_403_FORBIDDEN)
        # Asistentes pueden ver asistencias de cualquier estudiante
        elif requester_profile.user_type != 'assistant':
            return Response({
                'error': 'No tienes permisos para consultar asistencias'
            }, status=status.HTTP_403_FORBIDDEN)
    except:
        return Response({
            'error': 'Usuario sin perfil válido'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        student_profile = UserProfile.objects.get(
            account_number=account_number,
            user_type='student'
        )

        # Obtener todas las asistencias válidas del estudiante
        attendances = Attendance.objects.filter(
            student=student_profile,
            is_valid=True
        ).select_related('event').order_by('-timestamp')

        data = []
        for attendance in attendances:
            data.append({
                'id': attendance.id,
                'event': attendance.event.id,
                'event_title': attendance.event.title,
                'event_date': attendance.event.date.strftime('%Y-%m-%d'),
                'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response(data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Estudiante no encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='60/m', method='GET', block=True)
def get_external_user_attendances(request):
    """Obtener asistencias de usuario externo: 60 consultas por minuto"""
    account_number = request.GET.get('account_number')

    if not account_number:
        return Response({'error': 'Se requiere account_number'}, status=400)

    # Normalizar el username para comparar (eliminar prefijo "ext_")
    user_account = request.user.username.replace('ext_', '')

    # Verificar que el usuario externo solo pueda ver sus propias asistencias
    if user_account != account_number:
        # Verificar si es asistente (pueden ver todas)
        try:
            requester_profile = request.user.userprofile
            if requester_profile.user_type != 'assistant':
                return Response({
                    'error': 'Solo puedes consultar tus propias asistencias'
                }, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({
                'error': 'Solo puedes consultar tus propias asistencias'
            }, status=status.HTTP_403_FORBIDDEN)

    try:
        external_user = ExternalUser.objects.get(
            account_number=account_number,
            status='approved'
        )

        # Obtener todas las asistencias válidas del usuario externo
        attendances = Attendance.objects.filter(
            external_user=external_user,
            is_valid=True
        ).select_related('event').order_by('-timestamp')

        data = []
        for attendance in attendances:
            data.append({
                'id': attendance.id,
                'event': attendance.event.id,
                'event_title': attendance.event.title,
                'event_date': attendance.event.date.strftime('%Y-%m-%d'),
                'timestamp': attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response(data)
    except ExternalUser.DoesNotExist:
        return Response({'error': 'Usuario externo no encontrado o no aprobado'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='GET', block=True)
def get_external_user_stats(request):
    """Obtener estadísticas de usuario externo: 30 consultas por minuto"""
    account_number = request.GET.get('account_number')

    if not account_number:
        return Response({'error': 'Se requiere account_number'}, status=400)

    # Normalizar el username para comparar (eliminar prefijo "ext_")
    user_account = request.user.username.replace('ext_', '')

    # Verificar que el usuario externo solo pueda ver sus propias estadísticas
    if user_account != account_number:
        # Verificar si es asistente (pueden ver todas)
        try:
            requester_profile = request.user.userprofile
            if requester_profile.user_type != 'assistant':
                return Response({
                    'error': 'Solo puedes consultar tus propias estadísticas'
                }, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({
                'error': 'Solo puedes consultar tus propias estadísticas'
            }, status=status.HTTP_403_FORBIDDEN)

    try:
        external_user = ExternalUser.objects.get(
            account_number=account_number,
            status='approved'
        )

        # Obtener todos los eventos activos
        all_events = Event.objects.filter(is_active=True).order_by('date', 'start_time')

        # Agrupar eventos por bloques de horario (misma fecha y horarios que se solapan)
        # Usar la misma lógica que AttendanceStats.update_stats()
        event_slots = {}  # {(fecha, hora_inicio, hora_fin): [lista de eventos]}

        for event in all_events:
            # Crear una clave única para el bloque horario
            slot_key = (event.date, event.start_time, event.end_time)

            # Buscar si hay un slot existente que se solape con este evento
            found_slot = False
            for existing_slot in list(event_slots.keys()):
                existing_date, existing_start, existing_end = existing_slot

                # Verificar si es el mismo día y hay solapamiento de horarios
                if event.date == existing_date:
                    # Hay solapamiento si el inicio de uno es menor al fin del otro
                    if (event.start_time < existing_end and event.end_time > existing_start):
                        event_slots[existing_slot].append(event)
                        found_slot = True
                        break

            # Si no encontramos un slot existente, crear uno nuevo
            if not found_slot:
                event_slots[slot_key] = [event]

        # El total de "bloques" es la cantidad de slots únicos
        total_slots = len(event_slots)

        # Obtener asistencias del usuario externo
        user_attendances = Attendance.objects.filter(
            external_user=external_user,
            is_valid=True
        ).values_list('event_id', flat=True)

        # Contar cuántos bloques tiene asistencia
        attended_slots = 0
        for slot_events in event_slots.values():
            # Si asistió a al menos uno de los eventos del bloque, cuenta
            event_ids = [e.id for e in slot_events]
            if any(event_id in user_attendances for event_id in event_ids):
                attended_slots += 1

        # Calcular porcentaje
        attendance_percentage = round((attended_slots / total_slots) * 100, 2) if total_slots > 0 else 0.0

        return Response({
            'total_events': total_slots,
            'attended_events': attended_slots,
            'attendance_percentage': attendance_percentage
        })
    except ExternalUser.DoesNotExist:
        return Response({'error': 'Usuario externo no encontrado o no aprobado'}, status=404)
