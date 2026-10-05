"""
Prueba el camino serial COMPLETO sin hardware, simulando lo que manda la
ESP32. Incluye los casos que en la vida real rompen la lectura:

  - '5\\r\\n' partido en dos read() ('5\\r' y luego '\\n')
  - dos teclas en un solo read()  ('3\\n8\\n')
  - bytes que no son digitos:  '#' de arranque, y A B C * #
  - basura binaria
"""
import importlib.util
import sys

sys.argv = ["x", "--verificar"]
spec = importlib.util.spec_from_file_location("m", "brazo_lapiz.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pybullet as p


class PuertoFalso:
    """Imita lo que hace pyserial: in_waiting + read(n)."""

    def __init__(self):
        self.datos = b""

    def alimentar(self, b):
        self.datos += b

    @property
    def in_waiting(self):
        return len(self.datos)

    def read(self, n):
        trozo, self.datos = self.datos[:n], self.datos[n:]
        return trozo


fallos = 0


def comprobar(nombre, esperado_digitos, esperado_ignorados, trozos):
    global fallos
    pf = PuertoFalso()
    lector = m.LectorTeclado(pf)
    digitos, ignorados = [], []
    for trozo in trozos:
        pf.alimentar(trozo)
        d, i = lector.digitos()
        digitos += d
        ignorados += i
    ok = digitos == esperado_digitos and ignorados == esperado_ignorados
    print(f"  {'OK   ' if ok else 'FALLA'} {nombre}")
    print(f"         digitos   = {digitos}   (esperado {esperado_digitos})")
    print(f"         ignorados = {ignorados}   (esperado {esperado_ignorados})")
    if not ok:
        fallos += 1


print("=" * 72)
print("PRUEBA DEL LECTOR SERIAL (sin ESP32)")
print("=" * 72)

comprobar("tecla simple, como la manda Serial.println",
          ["5"], [], [b"5\r\n"])
comprobar("partida entre dos read(): '\\r' y '\\n' separados",
          ["5"], [], [b"5\r", b"\n"])
comprobar("partida justo antes del '\\n'",
          ["7"], [], [b"7", b"\r\n"])
comprobar("dos teclas en un solo read()",
          ["3", "8"], [], [b"3\r\n8\r\n"])
comprobar("tecla de arranque '#' de la ESP32",
          [], ["#"], [b"#\n"])
comprobar("letras A B C de la matriz",
          [], ["A", "B", "C"], [b"A\nB\nC\n"])
comprobar("asterisco y almohadilla",
          [], ["*", "#"], [b"*\n#\n"])
comprobar("basura binaria entre digitos validos",
          ["1", "2"], ["\x00", "?"], [b"\x00?\n1\n2\n"])
comprobar("los diez digitos de golpe",
          list("0123456789"), [], [b"".join(f"{d}\r\n".encode()
                                             for d in "0123456789")])
comprobar("teclas repetidas (keypad con rebote)",
          ["4", "4", "4"], [], [b"4\n", b"4\n", b"4\n"])

# --- final de linea: el bucle principal siempre va -----------------------
# IMPORTANTE: se reutiliza el robot que ya creo el modulo al importarse.
# No se carga un segundo robot: dos brazos en el mismo sitio se empujan
# mutuamente por colision y dan errores de cientos de mm que NO son reales.
print()
print("=" * 72)
print("Y AHORA: DIBUJAR DE VERDAD con los digitos que 'llegaron' por serial")
print("=" * 72)
print(f"  robot en uso: j0..j{m.N_JOINTS-1}, "
      f"eje de escritura j{m.EE} ({m.hijo(m.EE)})")
print(f"  panel vertical en x={m.X_PANEL:.2f} m, digito de "
      f"{m.DIG_ANCHO*1000:.0f} x {m.DIG_ALTO*1000:.0f} mm")

pf = PuertoFalso()
lector = m.LectorTeclado(pf)
pf.alimentar(b"#\n5\r\nA\n0\n9\r\n")     # arranque, digito, letra, digito
d, i = lector.digitos()
print(f"  llegan por serial: digitos={d}  ignorados={i}")
print()

for digito in d:
    m.Q_ACTUAL, _ = m.buscar_postura(m.a_mundo((0, 0), 0.0))
    err = m.dibujar(digito)
    marca = "OK" if err < 1.0 else "MAL"
    print(f"  digito {digito} dibujado, error de punta {err:.3f} mm   [{marca}]")
    if err >= 1.0:
        fallos += 1

p.disconnect()
print()
print("=" * 72)
print(f"RESULTADO: {'TODO OK' if fallos == 0 else f'{fallos} PRUEBAS FALLARON'}")
print("=" * 72)
sys.exit(1 if fallos else 0)
