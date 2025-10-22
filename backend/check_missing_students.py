#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para identificar estudiantes que no se procesaron por no estar en la BD.
"""
import os
import sys
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from authentication.models import UserProfile

def check_missing_students():
    """Verificar qué estudiantes no se encontraron en la BD"""
    print("=" * 80)
    print("ESTUDIANTES NO ENCONTRADOS EN LA BASE DE DATOS")
    print("=" * 80)
    print()

    # Leer ambos archivos Excel
    print("Leyendo archivos Excel...")
    print()

    # Archivo 1: Asistencias_Procesadas.xlsx
    df1 = pd.read_excel("/app/Asistencias_Procesadas.xlsx")
    print(f"[ARCHIVO 1] Asistencias_Procesadas.xlsx")
    print(f"Total de registros: {len(df1)}")
    print()

    missing_students_1 = []

    for idx, row in df1.iterrows():
        account_number_raw = str(row['account_number']).strip()
        name_in_excel = str(row['full_name']).strip()

        # Normalizar número de cuenta: quitar espacios y tomar solo los primeros 8 dígitos
        account_number = account_number_raw.replace(' ', '').replace('-', '')[:8]

        # Buscar el estudiante en la BD
        try:
            student_profile = UserProfile.objects.get(
                account_number=account_number,
                user_type='student'
            )
        except UserProfile.DoesNotExist:
            missing_students_1.append({
                'account_number_original': account_number_raw,
                'account_number_normalized': account_number,
                'name': name_in_excel
            })

    print(f"Estudiantes NO encontrados en BD (Conferencia IIoT): {len(missing_students_1)}")
    if missing_students_1:
        for student in missing_students_1:
            print(f"  ❌ {student['account_number_normalized']} (original: {student['account_number_original']})")
            print(f"     Nombre: {student['name']}")
    else:
        print("  ✓ Todos los estudiantes fueron encontrados")
    print()
    print("-" * 80)
    print()

    # Archivo 2: Book7.xlsx
    df2 = pd.read_excel("/app/Book7.xlsx")
    print(f"[ARCHIVO 2] Book7.xlsx")
    print(f"Total de registros: {len(df2)}")
    print()

    missing_students_2 = []

    for idx, row in df2.iterrows():
        account_number_raw = str(row['account_number']).strip()

        # Obtener el nombre si existe en la columna
        name_in_excel = str(row.get('full_name', 'N/A')).strip() if 'full_name' in row else 'N/A'

        # Normalizar número de cuenta
        account_number = account_number_raw.replace(' ', '').replace('-', '').replace('.0', '').replace('.', '')[:8]

        # Buscar el estudiante en la BD
        try:
            student_profile = UserProfile.objects.get(
                account_number=account_number,
                user_type='student'
            )
        except UserProfile.DoesNotExist:
            missing_students_2.append({
                'account_number_original': account_number_raw,
                'account_number_normalized': account_number,
                'name': name_in_excel
            })

    print(f"Estudiantes NO encontrados en BD (Conferencia Matemáticas): {len(missing_students_2)}")
    if missing_students_2:
        for student in missing_students_2:
            print(f"  ❌ {student['account_number_normalized']} (original: {student['account_number_original']})")
            print(f"     Nombre: {student['name']}")
    else:
        print("  ✓ Todos los estudiantes fueron encontrados")
    print()

    print("=" * 80)
    print("RESUMEN TOTAL")
    print("=" * 80)
    print(f"Total estudiantes no encontrados en Archivo 1: {len(missing_students_1)}")
    print(f"Total estudiantes no encontrados en Archivo 2: {len(missing_students_2)}")
    print(f"Total general de estudiantes NO procesados: {len(missing_students_1) + len(missing_students_2)}")
    print()

    # Ver si hay estudiantes que faltan en ambos archivos
    accounts_1 = set([s['account_number_normalized'] for s in missing_students_1])
    accounts_2 = set([s['account_number_normalized'] for s in missing_students_2])
    both = accounts_1.intersection(accounts_2)

    if both:
        print(f"Estudiantes que aparecen en AMBOS archivos pero no están en BD: {len(both)}")
        for acc in both:
            student_1 = next(s for s in missing_students_1 if s['account_number_normalized'] == acc)
            print(f"  ⚠ {acc}")
            print(f"     Nombre en Archivo 1: {student_1['name']}")
            if acc in accounts_2:
                student_2 = next((s for s in missing_students_2 if s['account_number_normalized'] == acc), None)
                if student_2:
                    print(f"     Nombre en Archivo 2: {student_2['name']}")
    else:
        print("No hay estudiantes que aparezcan en ambos archivos")
    print()

    print("=" * 80)
    print("✓ Verificación completada")
    print("=" * 80)

if __name__ == "__main__":
    check_missing_students()
