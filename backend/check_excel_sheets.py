#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar todas las hojas y columnas del archivo AttendanceStats.
"""
import pandas as pd

def check_excel():
    """Verificar hojas y columnas del Excel"""
    print("=" * 80)
    print("VERIFICANDO ARCHIVO ATTENDANCESTATS.XLSX")
    print("=" * 80)
    print()

    # Leer todas las hojas
    excel_file = pd.ExcelFile("/app/attendanceStats.xlsx")

    print(f"Hojas en el archivo: {excel_file.sheet_names}")
    print()

    # Leer cada hoja
    for sheet_name in excel_file.sheet_names:
        print("=" * 80)
        print(f"HOJA: {sheet_name}")
        print("=" * 80)

        df = pd.read_excel("/app/attendanceStats.xlsx", sheet_name=sheet_name)

        print(f"Total de registros: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        print()

        # Mostrar primeros 3 registros
        print("Primeros 3 registros:")
        for idx, row in df.head(3).iterrows():
            print(f"\nRegistro {idx + 1}:")
            for col in df.columns:
                print(f"  {col}: {row[col]}")

        print()

    print("=" * 80)

if __name__ == "__main__":
    check_excel()
