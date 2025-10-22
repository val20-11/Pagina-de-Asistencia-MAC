#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para encontrar eventos que sean realmente simultáneos.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from events.models import Event

def find_simultaneous_events():
    """Encontrar eventos simultáneos"""
    print("=" * 80)
    print("BUSCANDO EVENTOS SIMULTÁNEOS")
    print("=" * 80)
    print()

    all_events = Event.objects.filter(is_active=True).order_by('date', 'start_time')

    simultaneous_pairs = []

    for i in range(len(all_events)):
        for j in range(i + 1, len(all_events)):
            event1 = all_events[i]
            event2 = all_events[j]

            # Verificar si son el mismo día
            if event1.date == event2.date:
                # Verificar si los horarios se solapan
                if event1.start_time < event2.end_time and event1.end_time > event2.start_time:
                    simultaneous_pairs.append((event1, event2))

    print(f"Se encontraron {len(simultaneous_pairs)} pares de eventos simultáneos:")
    print()

    for idx, (event1, event2) in enumerate(simultaneous_pairs, 1):
        print(f"[PAR {idx}]")
        print(f"  Fecha: {event1.date}")
        print()
        print(f"  Evento 1 (ID: {event1.id}): {event1.title}")
        print(f"    Horario: {event1.start_time} - {event1.end_time}")
        print()
        print(f"  Evento 2 (ID: {event2.id}): {event2.title}")
        print(f"    Horario: {event2.start_time} - {event2.end_time}")
        print()
        print("-" * 80)
        print()

    print("=" * 80)
    print("✓ Búsqueda completada")
    print("=" * 80)

if __name__ == "__main__":
    find_simultaneous_events()
