#!/bin/sh
# Script para generar certificados SSL autofirmados dentro del contenedor
# Se ejecuta automáticamente al iniciar nginx

set -e

# Directorio donde se almacenarán los certificados (volumen persistente)
SSL_DIR="/etc/nginx/certs"
CERT_FILE="${SSL_DIR}/cert.pem"
KEY_FILE="${SSL_DIR}/key.pem"

echo "🔐 Verificando certificados SSL..."

# Crear directorio si no existe
if [ ! -d "$SSL_DIR" ]; then
    echo "📁 Creando directorio ${SSL_DIR}..."
    mkdir -p "$SSL_DIR"
fi

# Verificar permisos de escritura
if [ ! -w "$SSL_DIR" ]; then
    echo "❌ ERROR: No hay permisos de escritura en ${SSL_DIR}"
    exit 1
fi

# Verificar si los certificados ya existen
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "✅ Certificados SSL ya existen:"
    echo "   - Certificado: ${CERT_FILE}"
    echo "   - Clave privada: ${KEY_FILE}"

    # Verificar fecha de expiración
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
    echo "   - Válido hasta: ${EXPIRY_DATE}"
else
    echo "📝 Generando certificados SSL autofirmados..."

    # Generar certificado autofirmado
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/C=MX/ST=CDMX/L=Ciudad de Mexico/O=MAC Attendance/OU=IT/CN=localhost" \
        2>/dev/null

    # Verificar que se crearon correctamente
    if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
        echo "✅ Certificados SSL generados exitosamente:"
        echo "   - Certificado: ${CERT_FILE}"
        echo "   - Clave privada: ${KEY_FILE}"

        # Establecer permisos apropiados
        chmod 644 "$CERT_FILE"
        chmod 600 "$KEY_FILE"

        echo "   - Permisos configurados correctamente"
    else
        echo "❌ ERROR: No se pudieron generar los certificados"
        exit 1
    fi
fi

echo ""
echo "⚠️  IMPORTANTE: Estos son certificados autofirmados para DESARROLLO"
echo "   Para PRODUCCIÓN, usa certificados de Let's Encrypt o una CA confiable"
echo ""
