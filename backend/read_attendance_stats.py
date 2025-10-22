#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para leer la estructura del archivo AttendanceStats.
"""
import pandas as pd

def read_structure():
    """Leer estructura del archivo"""
    print("=" * 80)
    print("LEYENDO ESTRUCTURA DE ATTENDANCESTATS")
    print("=" * 80)
    print()

    # Leer archivo
    df = pd.read_excel("/app/attendanceStats.xlsx")

    print(f"Total de registros: {len(df)}")
    print()
    print(f"Columnas: {list(df.columns)}")
    print()

    # Mostrar primeros registros
    print("Primeros 10 registros:")
    print()
    for idx, row in df.head(10).iterrows():
        print(f"Registro {idx + 1}:")
        for col in df.columns:
            print(f"  {col}: {row[col]}")
        print()

    print("=" * 80)

if __name__ == "__main__":
    read_structure()
