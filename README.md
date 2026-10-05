# 🖊️ Brazo con lápiz que dibuja el dígito que teclees

Un brazo robótico simulado en **PyBullet** que escribe sobre un panel vertical
el número que pulsas en un **teclado matricial 4×4** conectado a una **ESP32**.
La ESP32 manda la tecla por el puerto serie y el brazo la dibuja con un lápiz.

Integrantes:
Nicolas Robayo Gomez
Camilo Molano
Jordan ALejandro Rodriguez



---

## Índice

- [Qué hace](#qué-hace)
- [Controles](#controles)
- [Cómo está hecho](#cómo-está-hecho)
- [Los números que salen](#los-números-que-salen)

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

---

## Controles

| Tecla | Qué hace |
|---|---|
| `0` – `9` | dibuja el dígito (también desde la ESP32) |
| `ESPACIO` | borra el dibujo |
| `R` | vuelve a la postura inicial y reencuadra |
| `C` | reencuadra la cámara |
| `ESC` o `Q` | salir |



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


<img width="557" height="580" alt="image" src="https://github.com/user-attachments/assets/25eb699f-3f16-4ccd-8ecb-110c383eaf9d" />

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

