# Quick Start - Inicio Rápido ⚡

## Para Colaboradores (Ya tienes el repo clonado)

```bash
# 1. Copiar variables de entorno
cp .env.development.example .env.development

# 2. Iniciar Docker
docker-compose -f docker-compose.dev.yml up -d

# 3. Abrir navegador
# http://localhost
```

**¡Listo!** El sistema ya tiene:
- ✅ Base de datos configurada
- ✅ Superusuario creado (usuario: `Admin`)
- ✅ Datos de ejemplo cargados
- ✅ Todo funcionando automáticamente

## Primera vez clonando el proyecto

```bash
# 1. Clonar
git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
cd Pagina-de-Asistencia-MAC

# 2. Configurar
cp .env.development.example .env.development

# 3. Iniciar
docker-compose -f docker-compose.dev.yml up -d
```

## Acceso Rápido

- **App:** http://localhost
- **Admin:** http://localhost/admin
- **Usuario:** Admin (con la contraseña del superusuario original)

## Comandos Útiles

```bash
# Ver logs
docker-compose -f docker-compose.dev.yml logs -f

# Reiniciar
docker-compose -f docker-compose.dev.yml restart

# Detener
docker-compose -f docker-compose.dev.yml down

# Resetear BD completa
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

## Más Información

- **Colaboradores:** Ver [SETUP_COLABORADORES.md](SETUP_COLABORADORES.md)
- **Producción:** Ver [GUIA_PRODUCCION.md](GUIA_PRODUCCION.md)
- **Completo:** Ver [README.md](README.md)

---

**Problema? Ejecuta:** `docker-compose -f docker-compose.dev.yml logs backend`
