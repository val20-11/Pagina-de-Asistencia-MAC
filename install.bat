@echo off
chcp 65001 >nul
echo ========================================
echo Sistema de Asistencia MAC - Instalador
echo ========================================
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker no está instalado.
    echo.
    echo Por favor instala Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Verificar si Docker Compose está disponible
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker Compose no está disponible.
    echo.
    pause
    exit /b 1
)

echo ✅ [1/5] Docker encontrado correctamente
docker --version
echo.

echo 🔨 [2/5] Deteniendo contenedores previos (si existen)...
docker-compose down >nul 2>&1
echo.

echo 🏗️  [3/5] Construyendo imágenes Docker...
echo (Esto puede tomar 5-10 minutos la primera vez)
echo.
docker-compose build
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Falló la construcción de imágenes
    pause
    exit /b 1
)

echo.
echo 🚀 [4/5] Iniciando contenedores...
docker-compose up -d
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Falló al iniciar contenedores
    pause
    exit /b 1
)

echo.
echo ⏳ [5/5] Esperando que los servicios estén listos...
timeout /t 8 >nul

echo.
echo 📊 Estado de los contenedores:
docker-compose ps

echo.
echo ========================================
echo ✅ ¡Instalación completada exitosamente!
echo ========================================
echo.
echo 🌐 La aplicación está disponible en:
echo    http://localhost
echo.
echo 🔐 Panel de administración:
echo    http://localhost/admin
echo.
echo 👤 Usuario de prueba:
echo    Número de cuenta: 3123123
echo.
echo 📚 Comandos útiles:
echo    Detener:    docker-compose down
echo    Ver logs:   docker-compose logs -f
echo    Reiniciar:  docker-compose restart
echo.
echo 📖 Para más información, consulta README.md
echo.
pause
