#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicialización de base de datos.
Carga automáticamente los fixtures si la BD está vacía.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command


def main():
    print("=" * 60)
    print("Inicializando Base de Datos")
    print("=" * 60)
    print()

    # Verificar si ya hay usuarios
    user_count = User.objects.count()

    if user_count > 0:
        print(f"[INFO] La base de datos ya tiene {user_count} usuario(s)")
        print("[INFO] No se cargarán fixtures")
        print()
        print("Si quieres resetear la BD, ejecuta:")
        print("  1. docker-compose -f docker-compose.dev.yml down -v")
        print("  2. docker-compose -f docker-compose.dev.yml up -d")
        print("  3. Espera a que este script se ejecute automáticamente")
        return

    print("[INFO] Base de datos vacía, cargando datos iniciales...")
    print()

    # Buscar archivos de fixtures
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

    if not os.path.exists(fixtures_dir):
        print(f"[WARNING] No se encontró directorio de fixtures: {fixtures_dir}")
        print("[INFO] Creando superusuario por defecto...")
        create_default_superuser()
        return

    # Buscar archivos JSON en fixtures
    fixture_files = [f for f in os.listdir(fixtures_dir) if f.endswith('.json')]

    if not fixture_files:
        print(f"[WARNING] No se encontraron fixtures en: {fixtures_dir}")
        print("[INFO] Creando superusuario por defecto...")
        create_default_superuser()
        return

    # Cargar cada fixture
    for fixture_file in sorted(fixture_files):
        fixture_path = os.path.join(fixtures_dir, fixture_file)
        print(f"[LOADING] Cargando {fixture_file}...")

        try:
            call_command('loaddata', fixture_path, verbosity=0)
            print(f"[OK] {fixture_file} cargado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error al cargar {fixture_file}: {str(e)}")

    print()
    print("=" * 60)
    print("[OK] Inicialización completada!")
    print("=" * 60)
    print()

    # Mostrar información de usuarios creados
    users = User.objects.all()
    print(f"Usuarios creados: {users.count()}")
    for user in users:
        role = "Superusuario" if user.is_superuser else "Usuario"
        print(f"  - {user.username} ({role})")
    print()


def create_default_superuser():
    """Crear un superusuario por defecto si no hay fixtures"""
    print("[CREATE] Creando superusuario por defecto...")
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@mac.com',
            password='admin123'  # CAMBIAR EN PRODUCCIÓN
        )
        print("[OK] Superusuario creado:")
        print("  Usuario: admin")
        print("  Password: admin123")
        print()
        print("[WARNING] IMPORTANTE: Cambia esta contraseña en producción!")
    except Exception as e:
        print(f"[ERROR] No se pudo crear el superusuario: {str(e)}")


if __name__ == "__main__":
    main()
