from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile
import re

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['account_number', 'user_type', 'full_name']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_staff', 'is_superuser']

class LoginSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=20)

    def validate_account_number(self, value):
        # Validar formato para números de cuenta (8 dígitos)
        if not re.match(r'^\d{8}$', value):
            raise serializers.ValidationError('El número de cuenta debe tener exactamente 8 dígitos.')
        return value

    def validate(self, data):
        account_number = data.get('account_number')

        if not account_number:
            raise serializers.ValidationError('Debe incluir número de cuenta.')

        # Primero buscar en usuarios regulares (estudiantes/asistentes)
        try:
            profile = UserProfile.objects.get(account_number=account_number)
            user = profile.user

            # Si el perfil no tiene usuario asociado (estudiantes sin cuenta Django)
            if user is None:
                # Crear usuario de Django automáticamente para estudiantes
                if profile.user_type == 'student':
                    user, created = User.objects.get_or_create(
                        username=account_number,
                        defaults={
                            'first_name': profile.full_name,
                            'is_active': True
                        }
                    )
                    profile.user = user
                    profile.save()
                else:
                    raise serializers.ValidationError('Esta cuenta no tiene acceso al sistema.')

            if not user.is_active:
                raise serializers.ValidationError('Esta cuenta está desactivada.')

            data['user'] = user
            data['profile'] = profile
            return data
        except UserProfile.DoesNotExist:
            pass

        # Si no es usuario regular, buscar en usuarios externos
        from authentication.models import ExternalUser
        try:
            external_user = ExternalUser.objects.get(account_number=account_number)
            if external_user.status != 'approved':
                raise serializers.ValidationError('Usuario externo no aprobado.')

            # Crear o buscar usuario de Django asociado
            user, created = User.objects.get_or_create(
                username=f'ext_{account_number}',
                defaults={'first_name': external_user.full_name}
            )
            data['user'] = user
            data['external_user'] = external_user
            return data

        except ExternalUser.DoesNotExist:
            raise serializers.ValidationError('Número de cuenta no encontrado.')

        return data