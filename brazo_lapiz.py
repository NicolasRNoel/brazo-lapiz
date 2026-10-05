"""
BRAZO CON LAPIZ QUE DIBUJA DIGITOS
=====================================

import os
import sys
import tempfile
import time
from contextlib import nullcontext

import numpy as np
import pybullet as p
import pybullet_data

# =============================================================================
# 1. EL URDF EMBEBIDO
# =============================================================================

URDF = """<?xml version="1.0"?>
<robot name="brazo_lapiz">

  <material name="base_material"><color rgba="0.25 0.25 0.28 1"/></material>
  <material name="hombro_material"><color rgba="0.35 0.35 0.40 1"/></material>
  <material name="brazo1_material"><color rgba="0.20 0.60 0.80 1"/></material>
  <material name="brazo2_material"><color rgba="0.90 0.50 0.10 1"/></material>
  <material name="muneca_material"><color rgba="0.55 0.55 0.60 1"/></material>
  <material name="pinza_material"><color rgba="0.80 0.20 0.20 1"/></material>
  <material name="dedo_material"><color rgba="0.90 0.90 0.90 1"/></material>
  <material name="lapiz_material"><color rgba="0.95 0.78 0.10 1"/></material>
  <material name="punta_material"><color rgba="0.12 0.12 0.12 1"/></material>

  <link name="base_link">
    <visual>
      <geometry><cylinder length="0.15" radius="0.25"/></geometry>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
      <material name="base_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.15" radius="0.25"/></geometry>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.075" rpy="0 0 0"/>
      <mass value="8.0"/>
      <inertia ixx="0.26" ixy="0" ixz="0" iyy="0.26" iyz="0" izz="0.50"/>
    </inertial>
  </link>

  <joint name="joint_1" type="revolute">
    <parent link="base_link"/>
    <child link="hombro_link"/>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.0" upper="3.0" effort="120" velocity="2.0"/>
    <dynamics damping="0.5" friction="0.1"/>
  </joint>

  <link name="hombro_link">
    <visual>
      <geometry><cylinder length="0.12" radius="0.09"/></geometry>
      <origin xyz="0 0 0.06" rpy="0 0 0"/>
      <material name="hombro_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.12" radius="0.09"/></geometry>
      <origin xyz="0 0 0.06" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.06" rpy="0 0 0"/>
      <mass value="1.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.012"/>
    </inertial>
  </link>

  <joint name="joint_hombro" type="revolute">
    <parent link="hombro_link"/>
    <child link="brazo1_link"/>
    <origin xyz="0 0 0.12" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.6" upper="1.6" effort="140" velocity="2.0"/>
    <dynamics damping="0.5" friction="0.1"/>
  </joint>

  <link name="brazo1_link">
    <visual>
      <geometry><cylinder length="0.32" radius="0.035"/></geometry>
      <origin xyz="0 0 0.16" rpy="0 0 0"/>
      <material name="brazo1_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.32" radius="0.035"/></geometry>
      <origin xyz="0 0 0.16" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.16" rpy="0 0 0"/>
      <mass value="1.2"/>
      <inertia ixx="0.013" ixy="0" ixz="0" iyy="0.013" iyz="0" izz="0.0006"/>
    </inertial>
  </link>

  <joint name="joint_2" type="revolute">
    <parent link="brazo1_link"/>
    <child link="brazo2_link"/>
    <origin xyz="0 0 0.32" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.4" upper="2.4" effort="100" velocity="2.0"/>
    <dynamics damping="0.4" friction="0.1"/>
  </joint>

  <link name="brazo2_link">
    <visual>
      <geometry><cylinder length="0.28" radius="0.030"/></geometry>
      <origin xyz="0 0 0.14" rpy="0 0 0"/>
      <material name="brazo2_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.28" radius="0.030"/></geometry>
      <origin xyz="0 0 0.14" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.14" rpy="0 0 0"/>
      <mass value="0.9"/>
      <inertia ixx="0.007" ixy="0" ixz="0" iyy="0.007" iyz="0" izz="0.0004"/>
    </inertial>
  </link>

  <joint name="joint_muneca" type="revolute">
    <parent link="brazo2_link"/>
    <child link="muneca_link"/>
    <origin xyz="0 0 0.28" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.6" upper="2.6" effort="60" velocity="2.5"/>
    <dynamics damping="0.2" friction="0.05"/>
  </joint>

  <link name="muneca_link">
    <visual>
      <geometry><cylinder length="0.05" radius="0.028"/></geometry>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <material name="muneca_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.05" radius="0.028"/></geometry>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <mass value="0.4"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="joint_advance" type="prismatic">
    <parent link="muneca_link"/>
    <child link="gripper_base"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="0.0" upper="0.26" effort="120" velocity="0.4"/>
    <dynamics damping="1.0" friction="0.2"/>
  </joint>

  <link name="gripper_base">
    <visual>
      <geometry><box size="0.026 0.034 0.022"/></geometry>
      <origin xyz="0 0 0.011" rpy="0 0 0"/>
      <material name="pinza_material"/>
    </visual>
    <collision>
      <geometry><box size="0.026 0.034 0.022"/></geometry>
      <origin xyz="0 0 0.011" rpy="0 0 0"/>
    </collision>
    <!-- tubo telescopico: tapa visualmente el hueco del recorrido -->
    <visual>
      <geometry><cylinder length="0.26" radius="0.010"/></geometry>
      <origin xyz="0 0 0.14" rpy="0 0 0"/>
      <material name="muneca_material"/>
    </visual>
    <inertial>
      <origin xyz="0 0 0.011" rpy="0 0 0"/>
      <mass value="0.2"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <link name="dedo_izquierdo">
    <visual>
      <geometry><box size="0.011 0.030 0.050"/></geometry>
      <origin xyz="-0.021 0 0.025" rpy="0 0 0"/>
      <material name="dedo_material"/>
    </visual>
    <collision>
      <geometry><box size="0.011 0.030 0.050"/></geometry>
      <origin xyz="-0.021 0 0.025" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="-0.021 0 0.025" rpy="0 0 0"/>
      <mass value="0.04"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.00005"/>
    </inertial>
  </link>

  <joint name="joint_dedo_izq" type="prismatic">
    <parent link="gripper_base"/>
    <child link="dedo_izquierdo"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="-1 0 0"/>
    <limit lower="0.0" upper="0.04" effort="15" velocity="0.3"/>
    <dynamics damping="0.3" friction="0.1"/>
  </joint>

  <link name="dedo_derecho">
    <visual>
      <geometry><box size="0.011 0.030 0.050"/></geometry>
      <origin xyz="0.021 0 0.025" rpy="0 0 0"/>
      <material name="dedo_material"/>
    </visual>
    <collision>
      <geometry><box size="0.011 0.030 0.050"/></geometry>
      <origin xyz="0.021 0 0.025" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0.021 0 0.025" rpy="0 0 0"/>
      <mass value="0.04"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.00005"/>
    </inertial>
  </link>

  <joint name="joint_dedo_der" type="prismatic">
    <parent link="gripper_base"/>
    <child link="dedo_derecho"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0.0" upper="0.04" effort="15" velocity="0.3"/>
    <dynamics damping="0.3" friction="0.1"/>
  </joint>

  <joint name="joint_lapiz" type="fixed">
    <parent link="gripper_base"/>
    <child link="lapiz_link"/>
    <origin xyz="0 0 -0.12" rpy="0 0 0"/>
  </joint>

  <link name="lapiz_link">
    <visual>
      <geometry><cylinder length="0.10" radius="0.0060"/></geometry>
      <origin xyz="0 0 0.065" rpy="0 0 0"/>
      <material name="lapiz_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.10" radius="0.0060"/></geometry>
      <origin xyz="0 0 0.065" rpy="0 0 0"/>
    </collision>
    <visual>
      <geometry><cylinder length="0.02" radius="0.0035"/></geometry>
      <origin xyz="0 0 0.01" rpy="0 0 0"/>
      <material name="punta_material"/>
    </visual>
    <collision>
      <geometry><cylinder length="0.02" radius="0.0035"/></geometry>
      <origin xyz="0 0 0.01" rpy="0 0 0"/>
    </collision>
    <inertial>
      <origin xyz="0 0 0.06" rpy="0 0 0"/>
      <mass value="0.015"/>
      <inertia ixx="0.00005" ixy="0" ixz="0" iyy="0.00005" iyz="0" izz="0.000004"/>
    </inertial>
  </link>

</robot>
"""

# =============================================================================
# 2. PARAMETROS  (cambia lo que necesites aqui)
# =============================================================================
VERIFICAR = "--verificar" in sys.argv


X_PANEL = 0.55          # m, plano del panel
Z_PANEL = 0.60          # m, altura del centro del digito
ALTURA_LAPIZ = 0.05     # m, cuanto se separa el lapiz del panel entre trazos
DIG_ANCHO = 0.200       # m, ancho del digito (a lo largo de +Y)
DIG_ALTO = 0.300        # m, alto del digito (a lo largo de +Z)
NORMAL_PANEL = np.array([1.0, 0.0, 0.0])   # direccion en que apunta el lapiz

APERTURA_DEDOS = 0.008  # m
DT = 1.0 / 240.0        # paso de simulacion
TIEMPO_POR_MOV = 0.16   # s de SIMULACION por waypoint

# --- Camara -----------------------------------------------------------------

CAM_YAW = 90.0
CAM_PITCH = -8.0
CAM_DIST = 0.90
CAM_OBJETIVO = [X_PANEL, 0.0, Z_PANEL]


PUERTO_SERIAL = COM3       
BAUD_SERIAL = 115200       


SEG = {
    "a": [(-1, +1), (+1, +1)],      # superior
    "b": [(+1, +1), (+1, 0)],       # superior derecho
    "c": [(+1, 0), (+1, -1)],       # inferior derecho
    "d": [(-1, -1), (+1, -1)],      # inferior
    "e": [(-1, -1), (-1, 0)],       # inferior izquierdo
    "f": [(-1, 0), (-1, +1)],       # superior izquierdo
    "g": [(-1, 0), (+1, 0)],        # central
}
DIGITOS = {
    "0": "abcdef", "1": "bc",     "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc",   "8": "abcdefg", "9": "fagbcd",
}

TRAYECTORIAS = {d: [SEG[s] for s in segs] for d, segs in DIGITOS.items()}

# =============================================================================
# 3. ESCENA
# =============================================================================
RUTA_URDF = os.path.join(tempfile.gettempdir(), "brazo_lapiz_generado.urdf")
with open(RUTA_URDF, "w", encoding="utf-8") as f:
    f.write(URDF)

p.connect(p.DIRECT if VERIFICAR else p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.setTimeStep(DT)
p.loadURDF("plane.urdf")
robot = p.loadURDF(RUTA_URDF, [0, 0, 0], useFixedBase=True)

# --- Descubrimiento de articulaciones -----------------------------------------
N_JOINTS = p.getNumJoints(robot)


def nombre(j):
    v = p.getJointInfo(robot, j)[1]
    return v.decode() if isinstance(v, (bytes, bytearray)) else str(v)


def hijo(j):
    v = p.getJointInfo(robot, j)[12]
    return v.decode() if isinstance(v, (bytes, bytearray)) else str(v)


MOTORES = [j for j in range(N_JOINTS)
           if p.getJointInfo(robot, j)[2] != p.JOINT_FIXED]
NDOF = len(MOTORES)                                   # 7
LO = np.array([p.getJointInfo(robot, j)[8] for j in MOTORES], float)
HI = np.array([p.getJointInfo(robot, j)[9] for j in MOTORES], float)
REVOLUTAS = [k for k, j in enumerate(MOTORES)
             if p.getJointInfo(robot, j)[2] == p.JOINT_REVOLUTE]
DEDOS = [k for k, j in enumerate(MOTORES) if "dedo" in nombre(j).lower()]

# Eje de escritura: el link del lapiz (su marco esta en la punta).
EE = next(j for j in range(N_JOINTS) if "lapiz" in hijo(j).lower())


def idx(texto):
    return next((k for k, j in enumerate(MOTORES) if texto in nombre(j).lower()),
                None)


K_AZIMUT = next((k for k in MOTORES if "joint_1" in nombre(MOTORES[k])), None)
K_HOMBRO = idx("hombro")
K_CODO = idx("joint_2")
K_MUNECA = idx("muneca") or idx("muñeca")
K_AVANCE = idx("advance") or idx("gripper")

# --- Marco del panel: u = derecha (+Y), v = arriba (+Z), salida = +X --------
ORIGEN = np.array([X_PANEL, 0.0, Z_PANEL])
EJE_U = np.array([0.0, DIG_ANCHO / 2, 0.0])
EJE_V = np.array([0.0, 0.0, DIG_ALTO / 2])


def a_mundo(uv, elevacion):
    """(u, v) en [-1, 1] del digito -> coordenada 3D del mundo.

    elevacion > 0 aleja la punta del panel a lo largo de su normal, que es
    como se 'levanta' el lapiz en un panel vertical.
    """
    u, v = uv
    punto = ORIGEN + u * EJE_U + v * EJE_V + elevacion * NORMAL_PANEL
    return tuple(punto)


# =============================================================================
# 4. CINEMATICA INVERSA
# =============================================================================
def punta():
    """Posicion de la punta del lapiz.

    getLinkState(...)[4] es worldLinkFramePosition, el origen del marco.
    El [0] es el CENTRO DE MASA y con <inertial> NO coincide con la punta.
    """
    return np.array(p.getLinkState(robot, EE)[4])


def aplicar(q):
    for k, j in enumerate(MOTORES):
        p.resetJointState(robot, j, float(q[k]))


def error_punta(objetivo):
    return float(np.linalg.norm(punta() - np.array(objetivo, float)))


class sin_render:
    """Apaga el render mientras dura el bloque.

    buscar_postura() hace n^2 teletransportes seguidos para barrer la rejilla.
    Con el render encendido se ve al brazo dar vueltas frenetico antes de
    que aparezca la ventana en condiciones, asi que se oculta.
    """

    def __enter__(self):
        p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 0)

    def __exit__(self, *exc):
        p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 1)
        return False


def dls(objetivo, q, iters=60, lam=0.01, lam_postura=0.08, tol=1e-4,
        refinando=True):
   
    objetivo = np.array(objetivo, float)
    ceros = [0.0] * NDOF
    q = np.array(q, float)
    ctx = nullcontext() if refinando else sin_render()
    with ctx:
        for _ in range(iters):
            e = objetivo - punta()
            if np.linalg.norm(e) < tol:
                break
            J = np.array(p.calculateJacobian(robot, EE, [0, 0, 0],
                                             list(q), ceros,
                                             ceros)[0])[:, MOTORES]
            dq0 = np.zeros(NDOF)
            if None not in (K_MUNECA, K_HOMBRO, K_CODO):
                dq0[K_CODO] = -q[K_CODO]
                dq0[K_MUNECA] = -q[K_MUNECA]
            dq = J.T @ np.linalg.solve(J @ J.T + lam * np.eye(3), e)
            dq += lam_postura * dq0
            q = np.clip(q + dq, LO, HI)      # nunca salirse de los limites
            aplicar(q)
    return q, error_punta(objetivo) * 1000.0


def buscar_postura(objetivo, n=31):
  
    import itertools

    objetivo = np.array(objetivo, float)
    libre = [k for k in (K_HOMBRO, K_CODO, K_AVANCE) if k is not None]
    base = np.zeros(NDOF)
    if K_AZIMUT is not None:
        base[K_AZIMUT] = np.clip(np.arctan2(objetivo[1], objetivo[0]),
                                 LO[K_AZIMUT], HI[K_AZIMUT])
    mejor, mejor_e = None, 1e9
    with sin_render():
        for combo in itertools.product(*[np.linspace(LO[k], HI[k], n)
                                          for k in libre]):
            q = base.copy()
            for k, v in zip(libre, combo):
                q[k] = v
            aplicar(q)
            e = error_punta(objetivo)
            if e < mejor_e:
                mejor_e, mejor = e, q.copy()
    return dls(objetivo, mejor, refinando=False)


# =============================================================================
# 5. CONTROL
# =============================================================================
Q_ACTUAL = np.zeros(NDOF)


def mantener(q, objetivo=None):
   
    pasos = max(1, int(TIEMPO_POR_MOV / DT))
    for _ in range(pasos):
        for k in REVOLUTAS:
            p.setJointMotorControl2(robot, MOTORES[k], p.POSITION_CONTROL,
                                    float(q[k]), targetVelocity=0,
                                    positionGain=0.4, velocityGain=1.0,
                                    force=250)
        for k in DEDOS:
            p.setJointMotorControl2(robot, MOTORES[k], p.POSITION_CONTROL,
                                    APERTURA_DEDOS, force=30)
        p.stepSimulation()
    return error_punta(objetivo) * 1000.0 if objetivo is not None else 0.0


def mover_a(objetivo):
    global Q_ACTUAL
    Q_ACTUAL, _ = dls(objetivo, Q_ACTUAL)
    return mantener(Q_ACTUAL, objetivo)


def dibujar_papel():
  
    y0, y1 = -DIG_ANCHO / 2, DIG_ANCHO / 2
    z0, z1 = -DIG_ALTO / 2, DIG_ALTO / 2
    for x in (X_PANEL, X_PANEL + ALTURA_LAPIZ):
        esquinas = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
        for a, b in zip(esquinas, esquinas[1:] + esquinas[:1]):
            p.addUserDebugLine(a, b, lineColorRGB=[0.55, 0.55, 0.55],
                               lineWidth=1, lifeTime=0)
    
    p.addUserDebugLine((X_PANEL, 0, z0 - 0.04), (X_PANEL, 0, z1 + 0.04),
                       lineColorRGB=[0.75, 0.75, 0.75], lineWidth=1,
                       lifeTime=0)


def puntos_segmento(uv_a, uv_b, paso=0.02):
   
    a, b = np.array(uv_a, float), np.array(uv_b, float)
    largo = np.linalg.norm((b - a) * np.array([DIG_ANCHO, DIG_ALTO]) / 2.0)
    n = max(2, int(np.ceil(largo / paso)) + 1)
    return [tuple(a + (b - a) * t) for t in np.linspace(0.0, 1.0, n)]


def dibujar(numero):
    
    global Q_ACTUAL
    trazos = TRAYECTORIAS.get(numero)
    if not trazos:
        return None
    p.removeAllUserDebugItems()
    peor = 0.0
    for seg in trazos:
        mover_a(a_mundo(seg[0], ALTURA_LAPIZ))   # separarse del panel
        mover_a(a_mundo(seg[0], 0.0))             # poner la punta
        anterior = punta()
        camino = puntos_segmento(seg[0], seg[1])
        for uv in camino[1:]:
            objetivo = a_mundo(uv, 0.0)
            peor = max(peor, mover_a(objetivo))
            actual = punta()
            p.addUserDebugLine(anterior, actual, lineColorRGB=[1, 0, 0],
                               lineWidth=6, lifeTime=0)
            anterior = actual
        mover_a(a_mundo(seg[-1], ALTURA_LAPIZ))  # volver a separarse
    return peor


def conectar_serial(puerto=None, baud=BAUD_SERIAL):
    """Abre el puerto de la ESP32. Devuelve un LectorTeclado o None."""
    import serial
    # OJO: 'import serial' NO expone serial.tools. Hay que importar el
    # submodulo explicitamente o revienta con
    #   AttributeError: module 'serial' has no attribute 'tools'
    import serial.tools.list_ports

    if puerto:
        candidatos = [puerto]
    else:
        enumeration = sorted(serial.tools.list_ports.comports(),
                             key=lambda d: d.device)
        if not enumeration:
            print("No se encontro ningun puerto serial.")
            return None
        candidatos = [d.device for d in enumeration]
        print("Puertos encontrados: " + ", ".join(candidatos))

    for dev in candidatos:
        try:
            s = serial.Serial(dev, baud, timeout=0.05)
            print(f"ESP32 conectada en {dev} @ {baud} baud")
            return LectorTeclado(s)
        except Exception as e:
            print(f"  {dev}: no se pudo abrir ({e})")
    return None


class LectorTeclado:
    

    def __init__(self, stream):
        self.stream = stream
        self.bufer = b""
        self.descartados = []

    def digitos(self):
        """Devuelve (lista_de_digitos, lista_de_caracteres_ignorados)."""
        pendientes = self.stream.in_waiting
        if pendientes:
            self.bufer += self.stream.read(pendientes)

        digitos, ignorados = [], []
        while b"\n" in self.bufer:
            linea, self.bufer = self.bufer.split(b"\n", 1)
            for ch in linea.decode("utf-8", errors="ignore"):
                if ch in TRAYECTORIAS:
                    digitos.append(ch)
                elif ch not in "\r\t ":
                    ignorados.append(ch)
        return digitos, ignorados


# =============================================================================
# 6. VERIFICACION
# =============================================================================
def verificar():
    global Q_ACTUAL
    print("=" * 70)
    print("VERIFICACION: los 10 digitos")
    print("=" * 70)
    print(f"URDF temporal: {RUTA_URDF}")
    print(f"joints={N_JOINTS}  motorizados={NDOF}  "
          f"eje de escritura=j{EE} ({hijo(EE)})")
    print(f"hombro={K_HOMBRO} codo={K_CODO} muneca={K_MUNECA} "
          f"avance={K_AVANCE} dedos={DEDOS}\n")

    Q_ACTUAL, e0 = buscar_postura(a_mundo((0, 0), 0.0))
    ang = np.degrees(Q_ACTUAL[[K_HOMBRO, K_CODO, K_MUNECA]])
    print(f"Postura inicial (centro del digito): error {e0:.3f} mm")
    print(f"  hombro / codo / muneca = {np.round(ang, 1)} deg  "
          f"(codo y muneca ~0 => lapiz alineado con el objetivo)\n")

    filas, peor_g, salto_g, inclin, salto_via = [], 0.0, 0.0, [], 0.0
    for d in "0123456789":
        Q_ACTUAL, _ = buscar_postura(a_mundo((0, 0), 0.0))
        p.removeAllUserDebugItems()
        peor, salto, prev = 0.0, 0.0, None
        for seg in TRAYECTORIAS[d]:
            mover_a(a_mundo(seg[0], ALTURA_LAPIZ))
            mover_a(a_mundo(seg[0], 0.0))
            prev = None          # el salto se mide solo DENTRO del trazo
            for uv in puntos_segmento(seg[0], seg[1])[1:]:
                Q_ACTUAL, e = dls(a_mundo(uv, 0.0), Q_ACTUAL)
                peor = max(peor, e)
                inclin.append(abs(np.degrees(Q_ACTUAL[K_CODO]
                                              + Q_ACTUAL[K_MUNECA])))
                if prev is not None:
                    salto = max(salto, float(np.abs(Q_ACTUAL - prev).max()))
                prev = Q_ACTUAL.copy()
            mover_a(a_mundo(seg[-1], ALTURA_LAPIZ))
            Q_ACTUAL, _ = dls(a_mundo(TRAYECTORIAS[d][0][0], 0.0), Q_ACTUAL)
            if prev is not None:
                salto_via = max(salto_via,
                                float(np.abs(Q_ACTUAL - prev).max()))
        filas.append((d, peor, salto))
        peor_g = max(peor_g, peor)
        salto_g = max(salto_g, salto)

    print(f"{'digito':<9}{'error punta':>15}{'salto':>13}")
    for d, e, s in filas:
        print(f"  {d:<7}{e:>12.3f} mm{s:>10.3f} rad")
    print()
    print(f"  panel vertical en el plano YZ, x={X_PANEL:.2f} m, "
          f"centro a z={Z_PANEL:.2f} m")
    print(f"  digito de {DIG_ANCHO*1000:.0f} x {DIG_ALTO*1000:.0f} mm")
    print(f"  ERROR MAXIMO DE LA PUNTA : {peor_g:.3f} mm")
    print(f"  SALTO MAXIMO PINTANDO    : {salto_g:.3f} rad")
    print(f"  traslado con lapiz arriba: {salto_via:.3f} rad "
          f"(no afecta la calidad del trazo)")
    print(f"  DESVIO COD+MUNECA (0 = lapiz alineado con el objetivo): "
          f"{np.mean(inclin):.2f} deg")
    ok = peor_g < 1.0 and salto_g < 0.30
    print(f"\n  {'CORRECTO' if ok else 'SIGUE FALLANDO'}: "
          f"criterio error < 1.0 mm y salto < 0.30 rad")

    # auto-colision: el brazo no debe rozarse a si mismo al escribir
    p.performCollisionDetection()
    choques = [c for c in p.getContactPoints(bodyA=robot) if c[1] != c[2]]
    if choques:
        print(f"  AUTO-COLISION: {len(choques)} contactos, por ejemplo "
              f"link {choques[0][1]} contra link {choques[0][2]}")
    else:
        print("  AUTO-COLISION: ninguna")
    p.disconnect()
    return 0 if ok else 1


# =============================================================================
# 7. BUCLE PRINCIPAL
# =============================================================================
def colocar_camara():
    
    p.resetDebugVisualizerCamera(CAM_DIST, CAM_YAW, CAM_PITCH, CAM_OBJETIVO)


def main():
    global Q_ACTUAL
    print("=" * 70)
    print("BRAZO CON LAPIZ - dibuja el digito que teclees")
    print("=" * 70)
    print(f"URDF temporal: {RUTA_URDF}")
    print(f"Panel vertical en el plano YZ, x={X_PANEL:.2f} m, "
          f"digito de {DIG_ANCHO*1000:.0f} x {DIG_ALTO*1000:.0f} mm")

    Q_ACTUAL, e0 = buscar_postura(a_mundo((0, 0), 0.0))
    print(f"Postura inicial: error {e0:.3f} mm")
    mover_a(a_mundo((0, 0), ALTURA_LAPIZ))
    dibujar_papel()
    colocar_camara()

    print("\n>>> Clic en la ventana de PyBullet y teclea 0-9")
    print(">>> ESPACIO borra, R reinicia, C reencuadra, ESC o Q sale\n")

    teclas = {}                     # eventos del frame anterior
    HUD = 1                         # replaceItemUniqueId DEBE ser int, no str

    lector = conectar_serial(PUERTO_SERIAL)
    if lector is None:
        print("  -> sin ESP32. Solo funciona el teclado de la PC.\n")

    def mostrar(texto, color):
        p.addUserDebugText(texto, [0.0, 0.0, 1.05], color, textSize=3.0,
                           lifeTime=0, replaceItemUniqueId=HUD)

    def escribir(digito):
        """Dibuja un digito y lo anuncia en el HUD y en la consola."""
        err = dibujar(digito)
        mostrar(f"digito {digito}   error {err:.2f} mm", [0.1, 0.3, 0.1])
        print(f"  digito {digito}: error de punta {err:.3f} mm")

    mostrar("Listo: 0-9", [0.3, 0.2, 0.1])

    while p.isConnected():
        try:
            # --- teclado matricial de la ESP32 --------------------------
            if lector is not None:
                recibidos, ignorados = lector.digitos()
                for ch in ignorados:
                    print(f"  tecla '{ch}' sin digito; A-D, # y * se ignoran")
                for d in recibidos:
                    escribir(d)

            # --- teclado de la PC (respaldo) ---------------------------
            eventos = p.getKeyboardEvents()
            nuevo = eventos if eventos != teclas else {}
            teclas = eventos

            for code, estado in nuevo.items():
                # Ojo: en PyBullet 3.2.7 no existe KEY_IS_TRIGGERED, solo
                # KEY_WAS_TRIGGERED, KEY_IS_DOWN y KEY_WAS_RELEASED.
                if estado != p.KEY_WAS_TRIGGERED:
                    continue
                if code == 27:                      # ESC
                    p.disconnect()
                    print("\nAdios.")
                    return
                # ojo: el espacio es 32, hay que incluirlo a mano
                letra = chr(code) if (code == 32 or 32 < code < 127) else ""
                if letra in TRAYECTORIAS:
                    escribir(letra)
                elif letra == " ":
                    p.removeAllUserDebugItems()
                    dibujar_papel()
                    print("  dibujo borrado")
                elif letra in ("r", "R"):
                    Q_ACTUAL, _ = buscar_postura(a_mundo((0, 0), 0.0))
                    colocar_camara()
                    print("  postura y camara reiniciadas")
                elif letra in ("c", "C"):
                    colocar_camara()
                    print("  camara reencuadrada")
                elif letra in ("q", "Q"):
                    p.disconnect()
                    print("\nAdios.")
                    return

            mantener(Q_ACTUAL)
        except Exception:
            # Si algo falla, que no se cierre la ventana en silencio: imprime
            # el error y deja el programa parado para poder leerlo.
            import traceback
            traceback.print_exc()
            print("\n*** Error arriba. La ventana se queda abierta; "
                  "cierrala con la X. ***")
            while p.isConnected():
                time.sleep(0.2)

    print("\nVentana cerrada.")


if __name__ == "__main__":
    sys.exit(verificar() if VERIFICAR else main())
