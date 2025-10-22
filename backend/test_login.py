#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar el login de estudiantes.
"""
import requests
import json

def test_student_login():
    """Probar login de estudiante"""
    print("=" * 80)
    print("PROBANDO LOGIN DE ESTUDIANTE")
    print("=" * 80)
    print()

    # URL del backend
    url = "http://localhost:8000/api/auth/login/"

    # Número de cuenta de prueba (un estudiante que sabemos existe)
    test_accounts = [
        "32114471",  # Lopez Martinez Valeria
        "32116578",  # Barrera Sanchez Alem Isaias
        "31732062",  # Villanueva Rubio Brandon Luis
    ]

    for account_number in test_accounts:
        print(f"Probando login con cuenta: {account_number}")
        print()

        # Datos de login
        data = {
            "account_number": account_number
        }

        try:
            # Hacer petición POST
            response = requests.post(url, json=data, timeout=10)

            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

            if response.status_code == 200:
                print("✓ LOGIN EXITOSO")
            else:
                print("✗ LOGIN FALLIDO")

        except requests.exceptions.RequestException as e:
            print(f"✗ ERROR DE CONEXIÓN: {e}")

        print()
        print("-" * 80)
        print()

    print("=" * 80)
    print("✓ Prueba completada")
    print("=" * 80)

if __name__ == "__main__":
    test_student_login()
