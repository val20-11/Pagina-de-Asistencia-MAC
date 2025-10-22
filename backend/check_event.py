#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar eventos en la base de datos.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from events.models import Event

def check_events():
    """Listar todos los eventos para encontrar el correcto"""
    print("=" * 80)
    print("EVENTOS EN LA BASE DE DATOS")
    print("=" * 80)
    print()

    events = Event.objects.all().order_by('-date')

    for event in events:
        print(f"ID: {event.id}")
        print(f"Título: {event.title}")
        print(f"Fecha: {event.date}")
        print(f"Tipo: {event.event_type}")
        print(f"Activo: {event.is_active}")
        print("-" * 80)

    print()
    print(f"Total de eventos: {events.count()}")
    print()

    # Buscar eventos que contengan "Matemáticas"
    math_events = Event.objects.filter(title__icontains='Matemáticas')
    if math_events.exists():
        print("\n=== Eventos relacionados con Matemáticas ===")
        for event in math_events:
            print(f"  - [{event.id}] {event.title} ({event.date})")

    # Buscar eventos que contengan "Computación"
    comp_events = Event.objects.filter(title__icontains='Computación')
    if comp_events.exists():
        print("\n=== Eventos relacionados con Computación ===")
        for event in comp_events:
            print(f"  - [{event.id}] {event.title} ({event.date})")

if __name__ == "__main__":
    check_events()
