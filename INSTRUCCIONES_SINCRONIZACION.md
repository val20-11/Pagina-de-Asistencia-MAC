# Instrucciones para Sincronizar el Proyecto entre Computadoras

## Problema común
Si los cambios no se reflejan en la otra computadora, sigue estos pasos:

## En la computadora ORIGEN (donde haces cambios):

### 1. Verificar estado
```bash
git status
```

### 2. Agregar cambios
```bash
git add .
```

### 3. Hacer commit
```bash
git commit -m "Descripción de los cambios"
```

### 4. Subir a GitHub
```bash
git push origin main
```

### 5. Verificar que se subió correctamente
- Ve a: https://github.com/val20-11/Pagina-de-Asistencia-MAC
- Verifica que los cambios aparezcan en GitHub

---

## En la computadora DESTINO (donde quieres los cambios):

### Opción A: Si YA clonaste el repositorio antes

1. **Abre la terminal en la carpeta del proyecto**

2. **Verifica que estás en el repositorio correcto:**
   ```bash
   git remote -v
   ```
   Debe mostrar: `https://github.com/val20-11/Pagina-de-Asistencia-MAC.git`

3. **Descarta cambios locales si los hay (CUIDADO: esto borra cambios no guardados):**
   ```bash
   git reset --hard HEAD
   ```

4. **Actualizar desde GitHub:**
   ```bash
   git pull origin main
   ```

5. **Si hay conflictos, forzar actualización (CUIDADO: sobrescribe todo):**
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

### Opción B: Primera vez (clonar desde cero)

1. **Elimina la carpeta vieja del proyecto si existe**

2. **Clona el repositorio:**
   ```bash
   git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
   cd Pagina-de-Asistencia-MAC
   ```

3. **Instala dependencias (si es necesario):**
   ```bash
   pip install -r requirements.txt
   ```

---

## Problemas comunes y soluciones

### Error: "Your branch is behind 'origin/main'"
**Solución:**
```bash
git pull origin main
```

### Error: "fatal: not a git repository"
**Solución:** Estás en la carpeta incorrecta. Navega a la carpeta del proyecto o clónalo de nuevo.

### Los archivos no se actualizan después de `git pull`
**Posibles causas:**
1. No hiciste `git push` en la computadora origen
2. Estás en una rama diferente
3. Tienes cambios locales que causan conflicto

**Solución:**
```bash
git fetch origin
git status
git reset --hard origin/main
```

### Quiero empezar de cero en la computadora destino
**Solución:**
1. Elimina la carpeta del proyecto completamente
2. Clona de nuevo:
   ```bash
   git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
   ```

---

## Flujo de trabajo recomendado

### Computadora A (Principal):
1. Haces cambios → `git add .` → `git commit -m "..."` → `git push origin main`
2. Verifica en GitHub que se subió

### Computadora B (Secundaria):
1. Abres el proyecto → `git pull origin main`
2. Trabajas con los archivos actualizados

**IMPORTANTE:** Siempre haz `git pull` antes de empezar a trabajar en cualquier computadora.

---

## Verificar que todo funciona

En cualquier computadora, ejecuta:
```bash
git log --oneline -3
```

Ambas computadoras deben mostrar los mismos commits más recientes.
