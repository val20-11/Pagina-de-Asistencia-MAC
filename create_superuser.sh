#!/bin/bash

# Script para crear un superusuario de Django en el contenedor

echo "==================================="
echo "Creando superusuario de Django"
echo "==================================="
echo ""

# Ejecutar el comando createsuperuser en el contenedor backend
docker-compose exec backend python manage.py createsuperuser

echo ""
echo "==================================="
echo "Superusuario creado exitosamente!"
echo "==================================="
echo ""
echo "Puedes acceder al panel de administración en:"
echo "  http://localhost/admin/"
echo ""
