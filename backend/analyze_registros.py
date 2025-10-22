#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analizar la estructura del archivo Registros_Asistencia.
"""
import pandas as pd

def analyze_file():
    """Analizar estructura del archivo"""
    print("=" * 80)
    print("ANALIZANDO REGISTROS_ASISTENCIA.XLSX")
    print("=" * 80)
    print()

    # Leer todas las hojas
    excel_file = pd.ExcelFile("/app/Registros_Asistencia.xlsx")

    print(f"Hojas en el archivo: {excel_file.sheet_names}")
    print()

    # Leer cada hoja
    for sheet_name in excel_file.sheet_names:
        print("=" * 80)
        print(f"HOJA: {sheet_name}")
        print("=" * 80)

        df = pd.read_excel("/app/Registros_Asistencia.xlsx", sheet_name=sheet_name)

        print(f"Total de registros: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        print()

        # Mostrar primeros 5 registros
        print("Primeros 5 registros:")
        for idx, row in df.head(5).iterrows():
            print(f"\nRegistro {idx + 1}:")
            for col in df.columns:
                value = row[col]
                print(f"  {col}: {value}")

        print()

        # Si hay columna de evento, mostrar eventos únicos
        if 'event' in df.columns or 'evento' in df.columns or 'event_title' in df.columns:
            event_col = None
            for col in df.columns:
                if 'event' in col.lower() or 'evento' in col.lower():
                    event_col = col
                    break

            if event_col:
                print(f"Eventos únicos en columna '{event_col}':")
                unique_events = df[event_col].unique()
                for event in unique_events:
                    count = len(df[df[event_col] == event])
                    print(f"  - {event}: {count} asistencias")
                print()

    print("=" * 80)

if __name__ == "__main__":
    analyze_file()
