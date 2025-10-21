#!/bin/bash
# Script para generar certificados SSL autofirmados para desarrollo

# Crear directorio para certificados
mkdir -p ssl

# Generar certificado autofirmado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=MX/ST=Estado/L=Ciudad/O=MAC/OU=IT/CN=localhost"

echo "✅ Certificados SSL generados en docker/ssl/"
echo "   - Certificado: docker/ssl/cert.pem"
echo "   - Clave privada: docker/ssl/key.pem"
echo ""
echo "⚠️  IMPORTANTE: Estos son certificados autofirmados para DESARROLLO"
echo "    Para PRODUCCIÓN, usa certificados de Let's Encrypt o una CA confiable"
