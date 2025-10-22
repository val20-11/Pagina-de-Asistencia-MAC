#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar asistencias desde Book7.xlsx para la conferencia de Matemáticas.
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
    EXCEL_FILE = "/app/Book7.xlsx"
    EVENT_TITLE = "Matemáticas Aplicadas y Computación: Una fábrica mexicana de conocimiento y soluciones"
    ASSISTANT_USERNAME = "asst_11111111"  # El único asistente que hay

    process_attendance_file(EXCEL_FILE, EVENT_TITLE, ASSISTANT_USERNAME)
