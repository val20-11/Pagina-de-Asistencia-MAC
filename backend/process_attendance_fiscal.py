#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar asistencias de attendanceStats.xlsx
Conferencia: La presión fiscal como oportunidad en el entorno profesional

NOTA: Este evento es simultáneo con "Matemáticas Aplicadas y Computación" (12:00-13:00)
El sistema validará y rechazará estudiantes que ya tengan asistencia en el evento simultáneo.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from process_attendance import process_attendance_file

if __name__ == "__main__":
    # Parámetros
    EXCEL_FILE = "/app/attendanceStats.xlsx"
    EVENT_TITLE = "La presión fiscal como oportunidad en el entorno profesional"
    ASSISTANT_USERNAME = "asst_11111111"  # Asistente1

    print("=" * 80)
    print("AVISO IMPORTANTE")
    print("=" * 80)
    print()
    print("Este evento es simultáneo con:")
    print("  'Matemáticas Aplicadas y Computación: Una fábrica mexicana...'")
    print()
    print("El sistema RECHAZARÁ estudiantes que ya tengan asistencia")
    print("en el evento simultáneo para evitar conflictos.")
    print()
    print("=" * 80)
    print()

    process_attendance_file(EXCEL_FILE, EVENT_TITLE, ASSISTANT_USERNAME)
