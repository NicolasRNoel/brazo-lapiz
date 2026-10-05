# Subir a GitHub

El repositorio ya está inicializado y con un commit. Solo falta conectarlo al
remoto y subirlo.

## Qué se sube

4 archivos de código y 3 de documentación, 42 KB en total:

| Qué | Por qué |
|---|---|
| `brazo_lapiz.py` (34 KB) | El programa entero. El URDF va embebido dentro, así que es un archivo único |
| `teclado_esp32.ino` | El sketch de la ESP32 (teclado matricial + LCD) |
| `pruebas/prueba_serial.py` (4 KB) | Test del lector de la ESP32. Corre **sin hardware** con un puerto falso, y cubre los 10 casos que rompen la lectura del puerto. Se sube porque cualquiera que clone el repo puede ejecutarlo |
| `README.md` | La documentación, con los números medidos y las trampas de PyBullet |
| `requirements.txt`, `.gitignore`, `LICENSE` | Lo de siempre |

## Qué NO se sube

| Qué | Por qué |
|---|---|
| `_diagnostico/` (11 archivos) | Todo el trabajo de diagnóstico: scripts de barrido del espacio de trabajo, ajustes de `lam_postura`, depuración de la física. Fue necesario para encontrar los bugs, pero no hace falta para ejecutar el proyecto y estorba para leerlo |
| `ajustar_vertical.py`, `explorar_vertical.py` | Búsquedas en rejilla de dónde se puede dibujar. El resultado está en el código, no hace falta el search |
| `render_prueba.py`, `verificar_orientacion.py` | Comprueban el encuadre de la cámara. Útiles durante el desarrollo, no para usar el programa |
| `panel_vertical.png` | Un render de comprobación. Los `.png` están en el `.gitignore` |
| Los `*.txt` sueltos | Salidas de las pruebas |
| `__pycache__/` | Caché de Python |

Todo eso sigue en tu carpeta de trabajo, en
`D:\Documents\Proyecto predeterminado\brazo_diagnostico\`. **No se borró nada:**
este repositorio es una copia limpia, el original sigue intacto.

La decisión de no subir el URDF aparte es consciente. Podría ir como
`brazo_lapiz.urdf` en el repositorio, pero entonces el script tendría que buscarlo
en disco y alguien que copie solo el `.py` se quedaría sin robot. Embebido, el
archivo no se puede separar del programa.

---

## Paso 1 — Crear el repositorio en GitHub

En el navegador, en <https://github.com/new>:

- **Nombre**: `brazo-lapiz`
- **Descripción**: `Brazo con lápiz en PyBullet que dibuja el dígito de un teclado matricial conectado a una ESP32`
- **Visibilidad**: pública o privada, lo que prefieras
- **No marques** "Add to README" ni "Add .gitignore": ya tienes archivos locales y GitHub no debe crear un `.gitignore` que los borre

Dale a **Create repository**.

## Paso 2 — Conectar y subir

Copia la URL del repositorio que acabas de crear (algo como
`https://github.com/TU_USUARIO/brazo-lapiz.git`) y ejecuta **dentro de la carpeta
`brazo_lapiz`**:

```bash
git remote add origin https://github.com/TU_USUARIO/brazo-lapiz.git
git branch -M main
git push -u origin main
```

En PowerShell, con las rutas de tu máquina:

```powershell
cd "D:\Documents\Proyecto predeterminado\brazo_lapiz"
git remote add origin https://github.com/TU_USUARIO/brazo-lapiz.git
git branch -M main
git push -u origin main
```

Si Git pide usuario y contraseña:

- **Usuario**: tu nombre de usuario de GitHub
- **Contraseña**: **no** es tu contraseña de GitHub. GitHub ya no la acepta.

En su lugar, usa un **token personal**:

1. En GitHub: *Settings* → *Developer settings* → *Personal access tokens* → *Tokens (classic)*
2. *Generate new token*, marca el alcance `repo`
3. Copia el token (sale una sola vez)
4. Cuando `git push` pida contraseña, pega el token ahí

O, más cómodo, configura SSH una vez y no vuelves a escribir nada:

```powershell
ssh-keygen -t ed25519 -C "tu@email.com"
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

Copias lo que sale en <https://github.com/settings/keys> (*New SSH key*), y luego:

```powershell
git remote set-url origin git@github.com:TU_USUARIO/brazo-lapiz.git
git push -u origin main
```

## Comprobar que funciona

```bash
git status
```

Debe decir `nothing to commit, working tree clean` y `Your branch is up to
with 'origin/main'`.

## Si quieres que otra persona lo clone y lo ejecute

Eso ya funciona con lo que hay subido. En una máquina nueva:

```bash
git clone https://github.com/TU_USUARIO/brazo-lapiz.git
cd brazo-lapiz
pip install -r requirements.txt
python brazo_lapiz.py
```

No hace falta nada más: ni ESP32, ni teclado, ni cables. El URDF se genera solo.

---

## Nota

Dejé el repositorio git inicializado y con un commit hecho, pero **sin remoto**:
no sé tu nombre de usuario de GitHub y no quiero adivinarlo ni tocar tus
credenciales. El paso 2 es lo único que falta.

Si prefieres que lo haga yo, dime tu nombre de usuario de GitHub y el nombre que
le pusiste al repositorio, y lo conecto. Para el push necesitarías que
configures tú un token o una clave SSH, que eso sí es cosa tuya.
