# Cómo Instalar Git en Windows

## Paso 1: Descargar Git

1. Ve a: https://git-scm.com/download/windows
2. La descarga comenzará automáticamente
3. Espera a que termine (es un archivo pequeño, ~50MB)

## Paso 2: Instalar Git

1. **Ejecuta el instalador** que descargaste
2. **Acepta la licencia** (clic en "Next")
3. **Ruta de instalación:** Deja la predeterminada (clic en "Next")
4. **Componentes:** Deja las opciones por defecto (clic en "Next")
5. **Menú de inicio:** Deja por defecto (clic en "Next")
6. **Editor:** Selecciona cualquiera (recomendado: "Use Visual Studio Code" o "Use Notepad") → "Next"
7. **Configuraciones siguientes:**
   - Deja todo por defecto
   - Solo haz clic en "Next" en todas las pantallas
8. **Clic en "Install"**
9. **Espera a que termine** y haz clic en "Finish"

## Paso 3: Verificar la instalación

1. Abre **CMD** o **PowerShell** (o Git Bash)
2. Escribe:
   ```bash
   git --version
   ```
3. Debe mostrar algo como: `git version 2.45.0`

## Paso 4: Configurar Git (primera vez)

Abre la terminal y ejecuta (cambia el nombre y email):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

## Paso 5: Clonar el proyecto

1. Abre la terminal
2. Navega a donde quieres guardar el proyecto:
   ```bash
   cd C:\Users\TuUsuario\Documents
   ```

3. Clona el repositorio:
   ```bash
   git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
   ```

4. Entra a la carpeta:
   ```bash
   cd Pagina-de-Asistencia-MAC
   ```

¡Listo! Ya tienes el proyecto.

---

## Actualizar el proyecto después

Cada vez que quieras traer los cambios más recientes:

```bash
cd Pagina-de-Asistencia-MAC
git pull origin main
```

---

## Alternativa: GitHub Desktop (más fácil, con interfaz gráfica)

Si prefieres no usar la terminal:

1. Descarga **GitHub Desktop**: https://desktop.github.com/
2. Instálalo
3. Inicia sesión con tu cuenta de GitHub
4. Clic en **"Clone a repository"**
5. Busca: `val20-11/Pagina-de-Asistencia-MAC`
6. Selecciona dónde guardarlo
7. Clic en **"Clone"**

### Para actualizar con GitHub Desktop:
- Solo haz clic en **"Fetch origin"** y luego **"Pull origin"**

---

## Comparación

| Característica | ZIP | Git CLI | GitHub Desktop |
|----------------|-----|---------|----------------|
| Instalación necesaria | No | Sí (ligera) | Sí (ligera) |
| Facilidad de uso | 😐 Manual | 🤓 Terminal | 😊 Visual |
| Sincronización | ❌ Manual | ✅ Automática | ✅ Un clic |
| Control de versiones | ❌ No | ✅ Sí | ✅ Sí |
| Ver historial | ❌ No | ✅ Sí | ✅ Sí |
| Recomendado | Solo emergencias | Usuarios técnicos | Principiantes |

---

## Mi recomendación

1. **Si solo necesitas el código UNA vez:** Descarga ZIP
2. **Si vas a trabajar en ambas computadoras regularmente:** Instala Git o GitHub Desktop
3. **Lo más fácil para ti:** GitHub Desktop (interfaz gráfica, sin comandos)

---

## Enlaces rápidos

- **Git para Windows:** https://git-scm.com/download/windows
- **GitHub Desktop:** https://desktop.github.com/
- **Tu repositorio:** https://github.com/val20-11/Pagina-de-Asistencia-MAC
