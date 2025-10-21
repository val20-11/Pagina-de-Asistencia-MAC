#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para exportar fixtures de la base de datos actual.
Usalo cuando quieras compartir tu base de datos con colaboradores.
"""
import subprocess
import os
import sys

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    print("=" * 50)
    print("Exportando datos de la base de datos")
    print("=" * 50)
    print()

    # Verificar que los contenedores esten corriendo
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )

    if "pagina-de-asistencia-mac-backend-1" not in result.stdout:
        print("[ERROR] El contenedor backend no esta corriendo")
        print("Ejecuta: docker-compose -f docker-compose.dev.yml up -d")
        sys.exit(1)

    # Crear directorio de fixtures
    fixtures_dir = os.path.join("backend", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)
    print(f"[DIR] Directorio de fixtures: {fixtures_dir}")
    print()

    # Exportar datos de usuarios y perfiles
    print("[EXPORT] Exportando usuarios y perfiles...")
    cmd = [
        "docker", "exec", "pagina-de-asistencia-mac-backend-1",
        "python", "manage.py", "dumpdata",
        "--indent", "2",
        "auth.user",
        "authentication.userprofile"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] Error al exportar: {result.stderr}")
        sys.exit(1)

    # Guardar en archivo
    output_file = os.path.join(fixtures_dir, "initial_users.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.stdout)

    file_size = os.path.getsize(output_file) / 1024  # KB
    print(f"[OK] Usuarios exportados: {output_file} ({file_size:.2f} KB)")
    print()

    # Exportar eventos y asistencias (si existen)
    print("[EXPORT] Exportando eventos y asistencias...")
    cmd = [
        "docker", "exec", "pagina-de-asistencia-mac-backend-1",
        "python", "manage.py", "dumpdata",
        "--indent", "2",
        "events.event",
        "attendance.attendance"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip() != "[]":
        output_file = os.path.join(fixtures_dir, "initial_events.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"[OK] Eventos exportados: {output_file} ({file_size:.2f} KB)")
    else:
        print("[INFO] No hay eventos para exportar")

    print()
    print("=" * 50)
    print("[OK] Exportacion completada!")
    print("=" * 50)
    print()
    print("Ahora puedes compartir estos archivos:")
    print("  1. Sube a GitHub:")
    print("     git add backend/fixtures/")
    print("     git commit -m 'Agregar fixtures iniciales'")
    print("     git push origin main")
    print()
    print("  2. O comparte por otro medio (Google Drive, etc.)")
    print()

if __name__ == "__main__":
    main()
