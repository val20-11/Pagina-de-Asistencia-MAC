#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para identificar evento del 21 de octubre a las 11am.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from events.models import Event
from datetime import date, time

def find_event():
    """Encontrar evento del 21 de octubre de 2025 a las 11am"""
    print("=" * 80)
    print("BUSCANDO EVENTO: 21 de Octubre 2025 - 11:00 AM")
    print("=" * 80)
    print()

    # Buscar eventos del 21 de octubre
    target_date = date(2025, 10, 21)
    events_oct21 = Event.objects.filter(date=target_date).order_by('start_time')

    print(f"Eventos del 21 de octubre de 2025:")
    print()

    for event in events_oct21:
        marker = "<<<" if event.start_time.hour == 11 else ""
        print(f"[ID: {event.id}] {event.title}")
        print(f"  Horario: {event.start_time} - {event.end_time} {marker}")
        print(f"  Tipo: {event.event_type}")
        print(f"  Ubicación: {event.location}")
        print()

    # Buscar específicamente eventos a las 11am
    target_time = time(11, 0, 0)
    events_11am = Event.objects.filter(
        date=target_date,
        start_time=target_time
    )

    if events_11am.exists():
        print("=" * 80)
        print("EVENTOS A LAS 11:00 AM:")
        print("=" * 80)
        for event in events_11am:
            print(f"  ID: {event.id}")
            print(f"  Título: {event.title}")
            print(f"  Horario: {event.start_time} - {event.end_time}")
            print()
    else:
        print("⚠ No se encontraron eventos exactamente a las 11:00 AM")

    print("=" * 80)

if __name__ == "__main__":
    find_event()
