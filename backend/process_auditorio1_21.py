#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar asistencias del auditorio1_21.xlsx
Conferencia: Matemáticas Aplicadas a Medicina a través del Procesamiento Digital de Imágenes
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
    EXCEL_FILE = "/app/auditorio1_21.xlsx"
    EVENT_TITLE = "Matemáticas Aplicadas a Medicina a través del Procesamiento Digital de Imágenes"
    ASSISTANT_USERNAME = "asst_11111111"  # Asistente1

    process_attendance_file(EXCEL_FILE, EVENT_TITLE, ASSISTANT_USERNAME)
