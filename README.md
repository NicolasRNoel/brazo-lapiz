# 🖊️ Brazo con lápiz que dibuja el dígito que teclees

Un brazo robótico simulado en **PyBullet** que escribe sobre un panel vertical
el número que pulsas en un **teclado matricial 4×4** conectado a una **ESP32**.
La ESP32 manda la tecla por el puerto serie y el brazo la dibuja con un lápiz.

Todo corre en software. Para probarlo **no hace falta ESP32, ni teclado, ni
cables**: con el script abierto, tecleas `0`-`9` en la ventana de PyBullet.

```bash
pip install -r requirements.txt
python brazo_lapiz.py
```

---

## Índice

- [Qué hace](#qué-hace)
- [Empezar en 1 minuto](#empezar-en-1-minuto)
- [Controles](#controles)
- [Verificar que funciona](#verificar-que-funciona)
- [Cómo está hecho](#cómo-está-hecho)
- [Los números que salen](#los-números-que-salen)
- [Los errores que costaron tiempo](#los-errores-que-costaron-tiempo)
- [Limitaciones, dichas de frente](#limitaciones-dichas-de-frente)
- [Estructura de archivos](#estructura-de-archivos)
- [Licencia](#licencia)

---

## Qué hace

Pulsas `5` en el teclado. La ESP32 envía `"5\r\n"` por el puerto serie. El PC lo
lee, calcula la cinemática inversa y el brazo baja el lápiz hasta el panel,
recorre los cinco segmentos del `5` y lo levanta. El trazo aparece en rojo.

| | |
|---|---|
| **Simulador** | PyBullet 3.2.7 |
| **Microcontrolador** | ESP32, teclado matricial 4×4 + LCD 16×2 I2C |
| **Enlace** | UART a 115200 baud |
| **Dígitos** | 0 a 9, en segmentos de 7 |
| **Error de la punta** | 0,100 mm sobre un dígito de 200 × 300 mm |

El URDF va **embebido dentro del `.py`** como texto. Al arrancar el script lo
escribe en la carpeta temporal del sistema y lo carga desde ahí, así que es un
archivo único: no hay que crear ni gestionar ningún `.urdf` aparte.

---

## Empezar en 1 minuto

```bash
git clone https://github.com/TU_USUARIO/brazo-lapiz.git
cd brazo-lapiz
pip install -r requirements.txt
python brazo_lapiz.py
```

Se abre la ventana de PyBullet con el brazo. **Haz clic dentro de la ventana
negra** antes de teclear, que si no el teclado no llega.

Sin ESP32 el script lo detecta, avisa y sigue funcionando con el teclado de la
PC:

```
Puertos encontrados: COM3
ESP32 conectada en COM3 @ 115200 baud
```

---

## Controles

| Tecla | Qué hace |
|---|---|
| `0` – `9` | dibuja el dígito (también desde la ESP32) |
| `ESPACIO` | borra el dibujo |
| `R` | vuelve a la postura inicial y reencuadra |
| `C` | reencuadra la cámara |
| `ESC` o `Q` | salir |

En la ventana de PyBullet, el ratón y el **teclado numérico** mueven la cámara
como en cualquier escena de PyBullet.

### Para montar el hardware

`teclado_esp32.ino` va en la ESP32 con la librería `Keypad4x4` y
`LiquidCrystal_I2C`. Los pines están documentados en la cabecera del sketch.

**Ojo con un detalle que rompe placas:** el sketch **no** usa el GPIO 12. Es un
*strapping pin* (MTDI) y la librería `Keypad` lo configura como `INPUT_PULLUP`,
o sea que queda en alto durante el reset, y en varias placas eso impide que
bootee. La versión original del sketch lo usaba y no arrancaba.

---

## Verificar que funciona

```bash
python brazo_lapiz.py --verificar
```

Abre y cierra PyBullet en modo invisible, recorre los diez dígitos punto a
punto e imprime una tabla. No necesita ventana ni ESP32.

```
digito       error punta        salto
  0             0.100 mm     0.036 rad
  1             0.100 mm     0.030 rad
  ...
  ERROR MAXIMO DE LA PUNTA : 0.100 mm
  SALTO MAXIMO PINTANDO    : 0.036 rad
  AUTO-COLISION: ninguna
  CORRECTO
```

Y el lector de la ESP32 se puede probar **sin hardware**, con un puerto falso:

```bash
python pruebas/prueba_serial.py
```

Cubre los diez casos que en la vida real rompen la lectura del puerto: el `"\r"`
y el `"\n"` partidos en dos `read()`, dos teclas en una sola lectura, la letra
`#` de arranque, las letras `A`-`D` de la matriz, basura binaria y rebote del
teclado.

---

## Cómo está hecho

### El robot

`brazo_lapiz.py` lleva dentro un URDF con **8 articulaciones**, de las que 7 son
motorizadas:

| idx | articulación | tipo | giro |
|---|---|---|---|
| 0 | `joint_1` | revoluta | azimut de la base |
| 1 | `joint_hombro` | revoluta | inclinación del brazo superior |
| 2 | `joint_2` | revoluta | inclinación del antebrazo |
| 3 | `joint_muneca` | revoluta | muñeca |
| 4 | `joint_advance` | prismática | telescopio, 0 a 260 mm |
| 5 | `joint_dedo_izq` | prismática | dedo izquierdo de la pinza |
| 6 | `joint_dedo_der` | prismática | dedo derecho |
| 7 | `joint_lapiz` | **fija** | une la pinza con el lápiz |

El lápiz está unido por una articulación **fija** cuyo marco queda
**exactamente en la punta**. Así `getLinkState(...)[4]` devuelve el punto de
contacto y no hace falta corregir ningún offset.

### El panel está en el plano YZ, y tiene que estar

El panel es **vertical**, en el plano **YZ** (normal en ±X). No es una choice
estética: los tres joints de inclinación giran todos sobre el eje Y, así que la
dirección del lápiz siempre está contenida en el plano XZ. Medido:

```
apuntando abajo (-Z)       -> (+0.000, +0.000, -1.000)
panel YZ, apuntando a -X   -> (+1.000, +0.000, -0.000)
```

La componente Y da siempre `0.000`. **Un panel con la normal en ±Y sería
invisible para el lápiz.**

Como el lápiz es además **colineal con el brazo**, la punta está siempre a
distancia `0,53 + avance` del hombro, o sea dentro de una **corona de 26 cm de
grosor**. Por eso el panel está a 0,55 m del eje, y no más lejos.

### La cinemática inversa es propia

`calculateInverseKinematics` de PyBullet se quedó clavado, así que aquí la IK es
**mínimos cuadrados amortiguados (DLS)** sobre el Jacobiano real, con dos
detalles que importan:

**Semilla caliente.** El DLS parte de la postura anterior, y el primer objetivo
se resuelve con una búsqueda en rejilla. Sin esto, sembrado desde el origen, el
solver devuelve **todo ceros**: con la punta sobre el eje del brazo, `joint_1`
(azimut) no tiene autoridad sobre ella y su columna del Jacobiano es `[0,0,0]`.
Eso sí es un bug: el origen es exactamente el centro del eje.

**Sesgo de postura.** Como el lápiz es colineal con el antebrazo, lo natural es
que apunte **hacia el objetivo**, y eso se consigue llevando codo y muñeca a
cero. Es un objetivo blando: mandar es llegar la punta. Desvío final medido:
**0,18°**.

### El dibujo

Cada dígito es un conjunto de **segmentos de 7** (`a`…`g`), con el orden de
trazos elegido para minimizar los viajes con el lápiz levantado. Cada segmento se
interpola en pasos de 2 cm, porque el segmento superior de un `8` mide 200 mm
enteros y recorrerlo de un tirón hacía girar el hombro 20° entre dos puntos.

---

## Los números que salen

| | valor | cómo se midió |
|---|---|---|
| error de la punta | **0,100 mm** | los 10 dígitos, punto a punto |
| salto de articulación al pintar | **0,036 rad** (2°) | dentro de cada trazo |
| traslado con el lápiz levantado | 0,395 rad | entre segmentos; no afecta el trazo |
| inclinación del lápiz | **0,18°** | respecto a hombro→punta |
| auto-colisión | **ninguna** | `getContactPoints` en todo el recorrido |
| tamaño en pantalla | 207 × 301 px | de un lienzo de 900 × 700 |

---

## Los errores que costaron tiempo

Todo lo de aquí se midió ejecutando PyBullet, no de memoria. Casi todo son
trampas de la API de PyBullet 3.2.7.

### 1. `getLinkState` devuelve 6 elementos, no 14

```
[0] linkWorldPosition        -> CENTRO DE MASA del link
[1] linkWorldOrientation
[2] localInertialFrameWorldPosition
[3] localInertialFrameWorldOrientation
[4] worldLinkFramePosition   -> ORIGEN DEL MARCO DEL LINK   <-- el bueno
[5] worldLinkFrameOrientation
```

El código original usaba `[0]`. Con `<inertial>` en el URDF, `[0]` **deja de
coincidir con `[4]`**: en este robot `[0]` da 0,835 y el marco está en 0,72.

### 2. `getNumJoints` cuenta las fijas; `calculateJacobian` no

Este URDF tiene 8 articulaciones y una es fija, o sea 7 grados de libertad.
Medido:

```
len=5 -> todos los links OK
len=6 -> todos los links FALLAN   "numDof needs to be positive"
```

Los **tres** argumentos tienen que medir lo mismo, y medir el número de
motorizadas. La misma causa raíz produce el clásico `IndexError` al hacer
`range(num_joints)` sobre la solución de la IK.

### 3. Kwargs rotos en 3.2.7

| kwargs | qué pasa |
|---|---|
| `numIterations` | `TypeError`, no existe |
| `rangeOfMotion` | `TypeError`, no existe |
| `maxNumIterations` | **cuelga el proceso entero** |
| `jointDamping` | `SystemError` |

Ninguno sirve. Y sin ellos **no hay reinicios internos** del solver, lo que
obliga a buscar la semilla a mano.

### 4. Otros que también fallan

- `p.KEY_IS_TRIGGERED` **no existe** en 3.2.7. Solo hay `KEY_WAS_TRIGGERED`,
  `KEY_IS_DOWN` y `KEY_WAS_RELEASED`.
- `addUserDebugText(replaceItemUniqueId=...)` exige un **entero**. Pasarle un
  string tumba el proceso con `TypeError`, y como la ventana está atada al
  proceso, **se cierra sin decir nada**.
- `p.getSimulationTime()` no existe.
- `import serial` **no** expone `serial.tools`. Hay que importar el submódulo
  aparte o revienta con `AttributeError`.

### 5. El URDF original no podía dibujar

El primer URDF (`robot_con_pinza`, una pinza) **es geométricamente incapaz de
escribir en una mesa**, y no era cosa del software:

- el poste de 0,35 m **no se inclinaba**, porque `joint_1` es azimut. El codo
  quedaba clavado en z = 0,65 m.
- un lápiz de 0,30 m **cancelaba exactamente** el boom de 0,30 m, así que
  `punta = codo + q_gripper · dirección`, y la punta vivía dentro de una
  **esfera de 15 cm de radio** clavada a 0,65 m.

Medido, buscando dónde puede escribir el lápiz:

```
radio 0.06 -> z escribible [0.630, 0.780]
radio 0.15 -> nada alcanzable
```

La solución fue estructural: añadir `joint_hombro` para que el brazo superior sí
se incline.

### 6. El error de aritmética que costó una búsqueda entera

Al ampliar el telescopio busqué el panel entre 0,80 y 1,10 m y no encontré nada.
El cálculo del alcance estaba mal:

```
mal:     0.32 + 0.28 + 0.05 + 0.12 + avance   ->  0.77 .. 1.03 m
bien:    0.32 + 0.28 + 0.05 - 0.12 + avance   ->  0.53 .. 0.79 m
```

El lápiz cuelga en **−0,12**, así que **resta** alcance, no lo suma. media hora
de búsquedas porque la fórmula daba un rango donde no había nada.

### 7. Un falso positivo de 451 mm

Una prueba dio errores de 276 a 451 mm y parecía un bug grave. No lo era: el
arnés de prueba cargaba un **segundo robot en el origen**, que chocaba con el
primero y lo empujaba. El script nunca tuvo ese problema. Merece la pena
mencionarlo porque es la clase de error que hace perder más tiempo cuando se
toma por real.

---

## Limitaciones, dichas de frente

**El lápiz tapa el centro del dígito.** La pinza está 120 mm por delante del
panel, así que desde la cámara ocupa entre un 25 % y un 45 % del ancho del
número. Es inevitable: es un lápiz sobre un panel, la mano siempre está delante.
Se palió adelgazando la pinza (de 70 mm a 26 mm) y los eslabones. **Al terminar
de dibujar, el lápiz queda en el último segmento**, así que el resto del número
se ve entero.

**El panel tiene que estar en el plano YZ.** Por la razón geométrica del punto 5
de arriba. Si quieres un panel frontal o una mesa horizontal, hay que añadir una
articulación de balanceo (roll) al final de la cadena.

**El URDF es una pinza con el lápiz atado.** Para hardware real, un brazo de
escritura de verdad tiene 5 o 6 revolutas y el lápiz como eslabón articulado, no
fijo. Lo que hay aquí está pensado y medido para simulación.

**No se ha probado en hardware.** Todo lo de este README se midió en simulación.
El sketch de la ESP32 está escrito y es lo bastante directo para que probablemente funcione,
pero **nunca se ha ejecutado en una placa real**. Los pines se eligieron
siguiendo la tabla de strapping pins del ESP32, no probados.

**Un solo dígito a la vez.** Cada pulsación borra el anterior. No hay memoria de
lo escrito.

---

## Estructura de archivos

```
brazo-lapiz/
├── brazo_lapiz.py            El programa. Un solo archivo: el URDF va dentro
├── teclado_esp32.ino         Sketch de la ESP32 (teclado + LCD)
├── pruebas/
│   └── prueba_serial.py      Test del lector de la ESP32, sin hardware
├── requirements.txt
├── README.md
├── SUBIR-A-GITHUB.md
├── LICENSE
└── .gitignore
```

---

## Licencia

MIT. Ver [LICENSE](LICENSE).
