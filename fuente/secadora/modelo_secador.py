"""Modelo 3D detallado del secador de cinta de 3 pisos SC-4 (CadQuery, sólidos exactos).

Sirve para el entregable aparte de la secadora: STEP para SolidWorks/Fusion 360, GLB para el visor y
Blender, vistas DXF (proyección con líneas ocultas) para los planos SC-01 a SC-07, el despiece
(vectores de explosión de cada pieza) y la lista de piezas con masas.

Medidas en mm, Z arriba. Origen: vértice Sudoeste del secador sobre el piso (x al Este a lo largo de
la cámara, y al Norte). En la planta el secador está en x = 11.500, y = 8.000 (layout del visor).
Todas las cotas salen de los planos 02, 03, 09 y 22 y de fuente/datos/layout_planta.json.

    python modelo_secador.py            # STEP + GLB + piezas.json + vistas DXF
"""
from __future__ import annotations

import json
import math
import os

import cadquery as cq
from cadquery import Vector as V

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
G = json.load(open(os.path.join(RAIZ, "fuente", "datos", "layout_planta.json"), encoding="utf-8"))["G"]["secador"]
SALIDA = os.path.join(RAIZ, "secadora", "modelo_3d")
OFFSET_PLANTA = (G["x0"] * 1000, G["y0"] * 1000, 0.0)

# ------------------------------------------------------------------ datos (mm)
L = G["L"] * 1000                 # 13.000 largo de la cámara
A = G["A"] * 1000                 # 2.600 ancho
H = G["H"] * 1000                 # 3.400 altura total
HP = G["h_patas"] * 1000          # 400 patas
E_PANEL = G["panel"] * 1000       # 80 panel sándwich
YC = A / 2                        # eje longitudinal de la cámara
B_BANDA = G["banda_ancho"] * 1000
R_MOT = G["r_motriz"] * 1000      # 158 (Ø316 con goma)
R_REE = G["r_reenvio"] * 1000     # 125
L_TAMBOR = 2100
COLS_X = [x * 1000 for x in G["columnas_x"]]
PISOS = [{"n": p["n"], "z": p["zc"] * 1000, "sentido": p["sentido"], "cabeza": p["cabeza"] * 1000,
          "cola": p["cola"] * 1000} for p in G["pisos"]]
U_APOYO, U_CUBO, U_ESCALON, U_CORONA = 1370, 1044, 1455, 1505   # desde el eje de la cámara (plano 03)
RET_X = [x * 1000 for x in G["rodillos_retorno_x"]]
GUIAS_Y = [y * 1000 for y in G["guias_y"]]

# colores (RGB 0-1)
C = {
    "acero": (0.30, 0.34, 0.38), "galv": (0.70, 0.72, 0.74), "inox": (0.80, 0.82, 0.84),
    "panel": (0.93, 0.93, 0.90), "panel_int": (0.78, 0.80, 0.82), "malla": (0.62, 0.64, 0.66),
    "goma": (0.12, 0.12, 0.13), "motor": (0.15, 0.33, 0.55), "reductor": (0.42, 0.45, 0.50),
    "amarillo": (0.95, 0.75, 0.10), "uhmw": (0.96, 0.96, 0.92), "ptfe": (0.92, 0.93, 0.96), "rojo": (0.75, 0.12, 0.12),
    "negro": (0.10, 0.10, 0.11), "bronce": (0.72, 0.55, 0.30), "verde": (0.20, 0.55, 0.30),
    "hormigon": (0.72, 0.72, 0.70),
}
DENS = {"acero": 7.85, "inox": 7.93, "galv": 7.85, "uhmw": 0.94, "ptfe": 2.17, "goma": 1.3, "panel": 0.24, "fundicion": 7.2}


# ------------------------------------------------------------------ primitivas
def caja(x0, y0, z0, x1, y1, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cil(r, h, p, d=(0, 0, 1)):
    return cq.Solid.makeCylinder(r, h, V(*p), V(*d))


def tubo(ro, ri, h, p, d=(0, 0, 1)):
    return cil(ro, h, p, d).cut(cil(ri, h, p, d))


def cono(r1, r2, h, p, d=(0, 0, 1)):
    return cq.Solid.makeCone(r1, r2, h, V(*p), V(*d))


def comp(lista):
    planas = []
    for s in lista:
        if s is None:
            continue
        if isinstance(s, cq.Compound):
            planas.extend(s.Solids())
        else:
            planas.append(s)
    return cq.Compound.makeCompound(planas)


def perfil(pts, largo, p, eje="z"):
    """Extruye un perfil 2D (pts en el plano normal al eje) desde el punto p."""
    plano = {"z": "XY", "x": "YZ", "y": "XZ"}[eje]
    s = cq.Workplane(plano).polyline(pts).close().extrude(largo).val()
    return s.translate(V(*p))


def upn(h=120, b=55, tw=7, tf=9):
    """Sección UPN (alma en x=0, alas hacia +x), coordenadas (x, y) del plano."""
    return [(0, -h / 2), (b, -h / 2), (b, -h / 2 + tf), (tw, -h / 2 + tf), (tw, h / 2 - tf), (b, h / 2 - tf),
            (b, h / 2), (0, h / 2)]


def ipn(h=140, b=66, tw=5.7, tf=8.6):
    return [(-b / 2, -h / 2), (b / 2, -h / 2), (b / 2, -h / 2 + tf), (tw / 2, -h / 2 + tf), (tw / 2, h / 2 - tf),
            (b / 2, h / 2 - tf), (b / 2, h / 2), (-b / 2, h / 2), (-b / 2, h / 2 - tf), (-tw / 2, h / 2 - tf),
            (-tw / 2, -h / 2 + tf), (-b / 2, -h / 2 + tf)]


def angulo(a=50, e=5):
    return [(0, 0), (a, 0), (a, e), (e, e), (e, a), (0, a)]


# ------------------------------------------------------------------ equipos normalizados
def motor_iec(largo=270, diam=160, h_eje=80, eje_d=19, eje_l=40, aletas=16, patas=True):
    """Motor asincrónico IEC (por defecto carcasa 80, 0,75 kW 4 polos) con el eje según +x, en origen
    en la cara de la brida del lado accionamiento. Carcasa con aletas, tapa de ventilador con rejilla,
    caja de bornes, cáncamo y patas B3 (opcional)."""
    r = diam / 2
    piezas = []
    cuerpo = cil(r * 0.86, largo * 0.72, (-largo * 0.78, 0, 0), (1, 0, 0))
    piezas.append(cuerpo)
    # aletas de refrigeración radiales
    for i in range(aletas):
        a = 2 * math.pi * i / aletas
        if abs(math.sin(a) - 1) < 0.08:      # sin aletas debajo de la caja de bornes
            continue
        aleta = caja(-largo * 0.76, -2.2, r * 0.80, -largo * 0.08, 2.2, r)
        piezas.append(aleta.rotate(V(0, 0, 0), V(1, 0, 0), math.degrees(a)))
    # escudos
    piezas.append(cil(r * 0.9, largo * 0.08, (-largo * 0.08, 0, 0), (1, 0, 0)))
    piezas.append(cil(r * 0.9, largo * 0.06, (-largo * 0.84, 0, 0), (1, 0, 0)))
    # tapa del ventilador (cono truncado + rejilla)
    piezas.append(cono(r * 0.88, r * 0.80, largo * 0.16, (-largo * 0.84, 0, 0), (-1, 0, 0)))
    for k in range(6):
        piezas.append(caja(-largo - 1.5, -r * 0.75 + k * r * 0.3, -r * 0.6, -largo, -r * 0.75 + k * r * 0.3 + 6, r * 0.6))
    # eje con chaveta
    piezas.append(cil(eje_d / 2, eje_l, (0, 0, 0), (1, 0, 0)))
    piezas.append(caja(eje_l * 0.15, -3, eje_d / 2 - 2, eje_l * 0.85, 3, eje_d / 2 + 2))
    # caja de bornes y prensacable
    piezas.append(caja(-largo * 0.55, -r * 0.42, r * 0.80, -largo * 0.22, r * 0.42, r * 1.22))
    piezas.append(cil(9, 14, (-largo * 0.40, r * 0.42, r * 1.0), (0, 1, 0)))
    # cáncamo
    piezas.append(cil(6, 18, (-largo * 0.62, 0, r * 0.9), (0, 0, 1)))
    if patas:
        for x in (-largo * 0.70, -largo * 0.20):
            piezas.append(caja(x - 18, -r * 0.82, -h_eje, x + 18, r * 0.82, -h_eje + 12))
            piezas.append(caja(x - 12, -r * 0.5, -h_eje + 12, x + 12, r * 0.5, -r * 0.55))
    return comp(piezas)


def motorreductor_doble_sinfin():
    """Motorreductor 0,75 kW, doble sinfín-corona 1:300 (4.5). Origen: centro del eje hueco de salida,
    eje de salida según y. El motor (eje según −x) va bridado al primer sinfín."""
    piezas = []
    # carcasa de la segunda etapa (sale el eje): caja con nervios
    piezas.append(caja(-110, -75, -110, 110, 75, 120))
    for x in (-80, -30, 30, 80):
        piezas.append(caja(x - 4, -78, -110, x + 4, 78, 100))
    piezas.append(cil(62, 160, (0, -80, 0), (0, 1, 0)))          # cubos de salida
    piezas.append(cil(30, 230, (0, -115, 0), (0, 1, 0)))         # eje de salida Ø60 (macizo)
    # primera etapa (sinfín de entrada) arriba, a 90°
    piezas.append(caja(-120, -55, 120, 60, 55, 210))
    piezas.append(cil(48, 70, (-120, 0, 165), (-1, 0, 0)))       # brida B5 del motor
    # patas con colisos
    piezas.append(caja(-130, -90, -130, 130, 90, -110))
    m = motor_iec(patas=False).translate(V(0, 0, 0))
    m = m.rotate(V(0, 0, 0), V(0, 0, 1), 180).translate(V(-190, 0, 165))
    return comp(piezas), m


def rodamiento_ucf212():
    """Unidad con brida cuadrada UCF 212 (aprox. NTN: 167 × 167, agujeros a 143, altura de cubo 65)."""
    a, esp = 167, 25
    base = caja(-esp / 2, -a / 2, -a / 2, esp / 2, a / 2, a / 2)
    base = base.cut(cil(52, esp, (-esp / 2, 0, 0), (1, 0, 0)))
    for sy in (-1, 1):
        for sz in (-1, 1):
            base = base.cut(cil(9.5, esp, (-esp / 2, sy * 71.5, sz * 71.5), (1, 0, 0)))
    cubo = tubo(52, 30, 65, (-32, 0, 0), (1, 0, 0))
    graser = cil(4, 14, (0, 0, 52), (0, 0, 1))
    bulones = [cil(8, 40, (-esp / 2 - 10, sy * 71.5, sz * 71.5), (1, 0, 0)) for sy in (-1, 1) for sz in (-1, 1)]
    return comp([base, cubo, graser] + bulones)


def unidad_tensora_uct210(carrera=150):
    """Unidad tensora UCT 210 con marco de colisa y tornillo tensor M20 + contratuerca (4.14)."""
    marco = caja(-20, -40, -70, 20, 40 + carrera + 120, 70)
    marco = marco.cut(caja(-20, -30, -40, 20, 30 + carrera, 40))
    carro = caja(-28, -55, -50, 28, 55, 50)
    carro = carro.cut(cil(26, 56, (-28, 0, 0), (1, 0, 0)))
    tornillo = cil(10, carrera + 200, (0, 55, 0), (0, 1, 0))
    tuercas = [caja(-15, y, -15, 15, y + 16, 15) for y in (40 + carrera + 120, 40 + carrera + 140)]
    return comp([marco, carro, tornillo] + tuercas)


def rueda_dentada(z, paso=19.05, ancho=11.9, cubo_d=100, cubo_l=72, agujero=50):
    """Piñón/corona ASA 60 simplificado: disco primitivo con dientes como prismas."""
    dp = paso / math.sin(math.pi / z)
    r = dp / 2
    disco = tubo(r - 6, agujero / 2, ancho, (0, -ancho / 2, 0), (0, 1, 0))
    dientes = []
    for i in range(z):
        a = 2 * math.pi * i / z
        t = caja(-4.5, -ancho / 2, r - 7, 4.5, ancho / 2, r + 5)
        dientes.append(t.rotate(V(0, 0, 0), V(0, 1, 0), math.degrees(a)))
    cubo = tubo(cubo_d / 2, agujero / 2, cubo_l, (0, -cubo_l / 2, 0), (0, 1, 0))
    return comp([disco, cubo] + dientes), dp


def cadena(p1, p2, r1, r2, ancho=12):
    """Cadena ASA 60 como dos ramales rectos (placas) entre ruedas de radios r1 y r2 (plano x-z)."""
    (x1, z1), (x2, z2) = p1, p2
    ang = math.atan2(z2 - z1, x2 - x1)
    piezas = []
    for s in (1, -1):
        # tangente exterior aproximada
        nx, nz = -math.sin(ang) * s, math.cos(ang) * s
        a = (x1 + nx * r1, z1 + nz * r1)
        b = (x2 + nx * r2, z2 + nz * r2)
        lar = math.hypot(b[0] - a[0], b[1] - a[1])
        ram = caja(0, -ancho / 2, -9, lar, ancho / 2, 9)
        ram = ram.rotate(V(0, 0, 0), V(0, 1, 0), -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
        piezas.append(ram.translate(V(a[0], 0, a[1])))
    return comp(piezas)


def carter_cadena(x, z_sup, z_inf, r_sup, r_inf, y_cad, prof=76, e=1.6):
    """Cárter cerrado de chapa (4.15c) con forma de estadio que envuelve la corona (arriba) y el piñón
    (abajo): contorno = envolvente de dos circunferencias, profundidad 76 mm centrada en el plano de la
    cadena y. Lleva los agujeros de paso del eje motriz (cara interior y exterior) y del eje del reductor."""
    def estadio(ra, rb, h):
        d = z_sup - z_inf
        s_ = (ra - rb) / d
        c_ = math.sqrt(1 - s_ * s_)
        pts = [(ra * c_, ra * s_), (rb * c_, -d + rb * s_), (-rb * c_, -d + rb * s_), (-ra * c_, ra * s_)]
        w = cq.Workplane("XY").polyline(pts).close().extrude(h)
        w = w.union(cq.Workplane("XY").circle(ra).extrude(h)).union(cq.Workplane("XY").center(0, -d).circle(rb).extrude(h))
        # plano XY (u = x, v = z) -> girar 90° alrededor de x: v pasa a z y la extrusión a -y
        return w.val().rotate(V(0, 0, 0), V(1, 0, 0), 90)
    ext = estadio(r_sup, r_inf, prof).translate(V(x, y_cad + prof / 2, z_sup))
    inte = estadio(r_sup - e, r_inf - e, prof - 2 * e).translate(V(x, y_cad + prof / 2 - e, z_sup))
    c = ext.cut(inte)
    c = c.cut(cil(32, prof + 10, (x, y_cad - prof / 2 - 5, z_sup), (0, 1, 0)))     # eje motriz Ø50
    c = c.cut(cil(36, prof / 2 + 5, (x, y_cad - prof / 2 - 5, z_inf), (0, 1, 0)))  # eje del reductor Ø60
    # tapa de inspección abulonada (para engrasar la cadena) y bisagras de la tapa
    tapa = caja(x - 70, y_cad - prof / 2 - 3, z_inf + 120, x + 70, y_cad - prof / 2 - e, z_inf + 300)
    torn = [cil(5, 6, (x + sx * 58, y_cad - prof / 2 - 9, z_inf + 210 + sz * 75), (0, 1, 0))
            for sx in (-1, 1) for sz in (-1, 1)]
    return comp([c, tapa] + torn)


def consola_motorreductor(x, y_cad, z_red):
    """Consola 4.16b: chapa base PL 12 con colisos (tensado de la cadena), dos cartelas triangulares PL 10
    y placa de pared PL 12 abulonada al bastidor a través del panel (columna auxiliar del lado Sur)."""
    zb = z_red - 130                          # cara superior de la chapa base (apoyo de las patas del reductor)
    y_ext = y_cad - 300                       # borde exterior de la chapa
    piezas = [caja(x - 170, y_ext, zb - 12, x + 170, -2, zb)]
    for sx in (-1, 1):                        # colisos 18 × 60 (como relieve, para que se vean)
        for yy in (y_cad - 240, y_cad - 80):
            piezas.append(caja(x + sx * 105 - 9, yy - 30, zb - 13, x + sx * 105 + 9, yy + 30, zb - 11))
    for xx in (x - 160, x + 150):             # cartelas triangulares
        cart = (cq.Workplane("YZ").polyline([(-2, zb - 12), (y_ext + 30, zb - 12), (-2, zb - 420)]).close()
                .extrude(10).val().translate(V(xx, 0, 0)))
        piezas.append(cart)
    piezas.append(caja(x - 190, -14, zb - 440, x + 190, -2, zb + 20))          # placa de pared
    for sx in (-1, 1):
        for zz in (zb - 400, zb - 20):
            piezas.append(cil(12, 30, (x + sx * 170, -44, zz), (0, 1, 0)))      # cabezas de bulón M16
    return piezas


# ------------------------------------------------------------------ construcción
PIEZAS = []


# masas reales (kg) de las piezas que el modelo representa como sólidos simplificados (malla como chapa,
# rejilla maciza, paneles y puertas sin núcleo): especificación de catálogo o cálculo aparte
MASA_REAL = {
    "4.1": 25 * 2.0 * 12,                 # malla AISI 304 12 kg/m², desarrollo 25 m
    "4.2": 110, "4.3": 85,                # tambores (tubo + goma + discos + bujes)
    "4.9": 6 * 15,                        # puertas de panel 60 mm con marco inox
    "4.10": 80, "4.19a": 45, "4.12": 60, "4.19b": 35, "4.18": 90,
    "4.13": 530,                          # rejilla 32 kg/m², barandas, escalera y jaula
    "4.5": 45, "M": 11,                   # reductor doble sinfín 1:300 y motor IEC 80 de 0,75 kW
    "4.8a": 39 * 17, "4.8b": 39 * 17, "4.8c": 7.3 * 17, "4.8d": 7.3 * 17, "4.8e": 33.8 * 17, "4.8f": 33.8 * 17,
}


def pieza(cod, nombre, grupo, forma, color, material, explosion=(0, 0, 0), cantidad=1, nota=""):
    base = cod.split("-")[0]
    real = MASA_REAL.get(base, MASA_REAL.get("M") if cod.startswith("M") else None)
    PIEZAS.append({"cod": cod, "nombre": nombre, "grupo": grupo, "forma": forma, "color": C[color],
                   "material": material, "explosion": explosion, "cantidad": cantidad, "nota": nota,
                   "masa_real": real})


def bastidor():
    """4.11 Estructura: 10 columnas UPN 120, vigas IPN 140, travesaños L 50×5 y placas base (4.17)."""
    cols = []
    for x in COLS_X:
        for lado, y in (("S", 0.0), ("N", A)):
            # alma sobre la cara exterior, alas hacia adentro de la cámara
            if lado == "S":
                pts = [(x + py, y + px) for px, py in upn()]
            else:
                pts = [(x + py, y - px) for px, py in upn()]
            cols.append(perfil(pts, H - 12, (0, 0, 12)))
    pieza("4.11a", "Columnas UPN 120 × 3.388 mm", "estructura", comp(cols), "acero", "F-24 (IRAM-IAS U 500-503)",
          (0, 0, 0), 10)
    vigas = []
    for z in (HP + 70, H - 70):
        for y in (60.0, A - 60.0):
            pts = [(y + px, z + py) for px, py in ipn()]
            vigas.append(cq.Workplane("YZ").polyline(pts).close().extrude(L).val())
    pieza("4.11b", "Vigas longitudinales IPN 140 × 13.000 mm", "estructura", comp(vigas), "acero", "F-24", (0, 0, 0), 4)
    trav = []
    for p in PISOS:
        z_sop = p["z"] - 70                       # bajo las guías UHMW (20) y la malla
        for k in range(int(L // 1000) + 1):
            x = 150 + k * 1000
            if x > L - 100:
                continue
            ang = cq.Workplane("XZ").polyline([(x + px, z_sop - 50 + py) for px, py in angulo()]).close() \
                .extrude(-(A - 2 * E_PANEL)).val().translate(V(0, E_PANEL, 0))
            trav.append(ang)
    pieza("4.20", "Travesaños L 50×50×5 (soportes de guías) c/1,0 m", "estructura", comp(trav), "acero", "F-24",
          (0, 0, 0), len(trav))
    placas, anclas = [], []
    for x in COLS_X:
        for y in (30.0, A - 30.0):
            pl = caja(x - 100, y - 100, 0, x + 100, y + 100, 12)
            for dx in (-70, 70):
                for dy in (-70, 70):
                    pl = pl.cut(cil(9, 12, (x + dx, y + dy, 0)))
                    anclas.append(cil(8, 190, (x + dx, y + dy, -125)))       # varilla M16 (h_ef 125)
                    anclas.append(caja(x + dx - 12, y + dy - 12, 12, x + dx + 12, y + dy + 12, 26))  # tuerca
                    anclas.append(cil(15, 3, (x + dx, y + dy, 12)))           # arandela
            placas.append(pl)
    pieza("4.17", "Placa base PL 200×200×12 (4 agujeros Ø18)", "anclaje", comp(placas), "acero", "F-24",
          (0, 0, -250), 10)
    pieza("4.17a", "Anclaje químico: varilla M16 5.8 × 190, tuerca y arandela (h_ef 125 mm)", "anclaje",
          comp(anclas), "galv", "acero 5.8 zincado", (0, 0, -450), 40)


def cerramiento():
    """4.8 Paneles sándwich 80 mm (lana de roca, cara interior inox) y 4.9 puertas de inspección."""
    z0, z1 = HP, H
    puertas = G["puertas"]
    cortes_s, cortes_n = [], []
    for p in puertas:
        x = p["x"] * 1000
        cortes_s.append(caja(x - 350, -1, p["z0"] * 1000, x + 350, E_PANEL + 1, p["z1"] * 1000))
        cortes_n.append(caja(x - 350, A - E_PANEL - 1, p["z0"] * 1000, x + 350, A + 1, p["z1"] * 1000))
    ventanas = [caja(v["x"] * 1000 - 250, -1, v["z0"] * 1000, v["x"] * 1000 + 250, E_PANEL + 1, v["z1"] * 1000)
                for v in G["ventanas"]]
    sur = caja(0, 0, z0, L, E_PANEL, z1)
    for c_ in cortes_s + ventanas:
        sur = sur.cut(c_)
    norte = caja(0, A - E_PANEL, z0, L, A, z1)
    ea = G["entrada_aire"]
    norte = norte.cut(caja(ea["x0"] * 1000, A - E_PANEL - 1, ea["z0"] * 1000, ea["x1"] * 1000, A + 1, ea["z1"] * 1000))
    for c_ in cortes_n:
        norte = norte.cut(c_)
    # juntas entre paneles de 1,0 m (ranuras de 3 mm para que se lean los módulos)
    def juntas(sol, y_ext):
        for k in range(1, int(L // 1000) + 1):
            sol = sol.cut(caja(k * 1000 - 1.5, y_ext - 2, z0, k * 1000 + 1.5, y_ext + 2, z1))
        return sol
    sur = juntas(sur, 0)
    norte = juntas(norte, A)
    pieza("4.8a", "Paneles sándwich 80 mm – lado Sur (accionamientos)", "panel_s", sur, "panel", "lana de roca + inox 0,6 / galv. 0,5", (0, -2600, 0), 13)
    pieza("4.8b", "Paneles sándwich 80 mm – lado Norte", "panel_n", norte, "panel", "lana de roca + inox 0,6 / galv. 0,5", (0, 2600, 0), 13)
    oeste = caja(-E_PANEL + E_PANEL, E_PANEL, z0, E_PANEL, A - E_PANEL, z1)
    este = caja(L - E_PANEL, E_PANEL, z0, L, A - E_PANEL, z1)
    pieza("4.8c", "Paneles sándwich 80 mm – testero Oeste", "panel_o", oeste, "panel", "lana de roca", (-2200, 0, 0), 3)
    pieza("4.8d", "Paneles sándwich 80 mm – testero Este", "panel_e", este, "panel", "lana de roca", (2200, 0, 0), 3)
    techo = caja(0, 0, H - E_PANEL, L, A, H)
    cx = G["campana_x"] * 1000
    techo = techo.cut(caja(cx - 400, YC - 400, H - E_PANEL - 1, cx + 400, YC + 400, H + 1))
    ax = G["alimentacion_x"] * 1000
    techo = techo.cut(caja(ax - 200, YC - 300, H - E_PANEL - 1, ax + 200, YC + 300, H + 1))
    pieza("4.8e", "Paneles sándwich 80 mm – techo", "techo", techo, "panel", "lana de roca", (0, 0, 3600), 13)
    piso = caja(0, 0, HP, L, A, HP + E_PANEL)
    td = G["descarga_x"]
    piso = piso.cut(caja(td[0] * 1000 - 150, YC - 1000, HP - 1, td[1] * 1000 + 50, YC + 1000, HP + E_PANEL + 1))
    pieza("4.8f", "Paneles sándwich 80 mm – piso de la cámara", "piso", piso, "panel", "lana de roca", (0, 0, -150), 13)
    # puertas (hoja + bisagras + leva + microinterruptor): la hoja sobresale 60 mm de la cara exterior
    hojas = []
    for p in puertas:
        x = p["x"] * 1000
        za, zb = p["z0"] * 1000, p["z1"] * 1000
        for y_c, s in ((0.0, -1), (A, 1)):
            ya, yb = sorted((y_c, y_c + s * 60))
            hojas.append(caja(x - 345, ya, za + 5, x + 345, yb, zb - 5))
            yy = y_c + s * 60
            ya, yb = sorted((yy, yy + s * 30))
            hojas.append(caja(x + 255, ya, (za + zb) / 2 - 60, x + 290, yb, (za + zb) / 2 + 60))   # leva y manija
            for z in (za + 80, zb - 120):
                hojas.append(cil(12, 40, (x - 360, yy, z), (0, 0, 1)))                              # bisagras
    pieza("4.9", "Puertas de inspección 700 × 600 con leva y microinterruptor", "puertas", comp(hojas), "inox",
          "AISI 304 + lana de roca", (0, 0, 0), 6)


def cintas():
    """4.1 bandas, 4.2 tambores motrices, 4.3 tambores de reenvío, 4.4 UCF 212, 4.14 UCT 210, 4.6 rodillos
    de retorno, 4.7 guías UHMW-PE, 4.5 motorreductores y 4.15 transmisiones por cadena."""
    y0b, y1b = YC - B_BANDA / 2, YC + B_BANDA / 2
    for p in PISOS:
        n = p["n"]
        z = p["z"]
        xm, xr = p["cabeza"], p["cola"]
        zm, zr = z - R_MOT, z - R_REE                 # ejes de los tambores
        sx_m = 1 if xm > L / 2 else -1                # despiece: los tambores salen por su testero
        x_a, x_b = sorted((xm, xr))
        esp = 4.0
        # banda: ramal superior, ramal de retorno y abrazos en los tambores (simplificados)
        sup = caja(x_a, y0b, z, x_b, y1b, z + esp)
        ret = caja(x_a, y0b, min(zm - R_MOT, zr - R_REE) - esp, x_b, y1b, min(zm - R_MOT, zr - R_REE))
        # la banda abraza la mitad exterior de cada tambor (la cabeza mira al sentido de avance)
        s_ = 1 if p["sentido"] > 0 else -1
        abr_m = tubo(R_MOT + esp, R_MOT, B_BANDA, (xm, y0b, zm), (0, 1, 0))
        abr_m = abr_m.cut(caja(xm, y0b - 1, zm - R_MOT - esp - 2, xm - s_ * (R_MOT + esp + 2), y1b + 1, zm + R_MOT + esp + 2))
        abr_r = tubo(R_REE + esp, R_REE, B_BANDA, (xr, y0b, zr), (0, 1, 0))
        abr_r = abr_r.cut(caja(xr, y0b - 1, zr - R_REE - esp - 2, xr + s_ * (R_REE + esp + 2), y1b + 1, zr + R_REE + esp + 2))
        # cadenas laterales de borde
        bordes = [caja(x_a, y - 8, z - 12, x_b, y + 8, z) for y in (y0b + 8, y1b - 8)]
        pieza(f"4.1-{n}", f"Banda de malla AISI 304 Ø2 p5 × 2.000 – piso {n}", f"cinta{n}",
              comp([sup, ret, abr_m, abr_r] + bordes), "malla", "AISI 304", (0, 0, 0), 1, "desarrollo ≈ 25 m")
        # tambor motriz 4.2: tubo Ø300×4 + engomado 8 + discos + eje Ø60 (Ø50 en la corona)
        # accionamiento del lado Sur (y < 0)
        tm = [tubo(150, 146, L_TAMBOR, (xm, YC - L_TAMBOR / 2, zm), (0, 1, 0)),
              tubo(R_MOT, 150, L_TAMBOR - 40, (xm, YC - L_TAMBOR / 2 + 20, zm), (0, 1, 0))]
        for u in (-1044, 1044 - 12):
            tm.append(tubo(146, 58, 12, (xm, YC + u, zm), (0, 1, 0)))
            tm.append(tubo(58, 30, 80, (xm, YC + u - 34, zm), (0, 1, 0)))   # buje de fijación cónico
        pieza(f"4.2-{n}", f"Tambor motriz Ø300 × 2.100 con goma 8 mm – piso {n}", f"cinta{n}", comp(tm), "goma",
              "SAE 1020 + goma romboidal", (sx_m * 1600, 0, 0), 1)
        eje = [cil(30, (U_ESCALON + 1440), (xm, YC - 1440, zm), (0, 1, 0))]
        eje.append(cil(25, U_CORONA + 55 - U_ESCALON, (xm, YC - U_ESCALON - (U_CORONA + 55 - U_ESCALON), zm), (0, 1, 0)))
        pieza(f"4.2.1-{n}", f"Eje motriz SAE 1045 Ø60 / Ø50 × 3.000 (asiento rectificado) – piso {n}", f"cinta{n}",
              comp(eje), "acero", "SAE 1045", (sx_m * 1600, -3200, 0), 1, "chavetero 14×9 en Ø50; escalón r = 2")
        # rodamientos UCF 212 en ambos lados (fuera de la cámara) y ménsulas PL 12
        rod, men = [], []
        for s in (-1, 1):
            r_ = rodamiento_ucf212().rotate(V(0, 0, 0), V(0, 0, 1), 90).translate(V(xm, YC + s * U_APOYO, zm))
            rod.append(r_)
            yy = YC + s * (U_APOYO + 18) if s > 0 else YC - U_APOYO - 30
            men.append(caja(xm - 120, yy, zm - 260, xm + 120, yy + 12, zm + 110))
            men.append(caja(xm - 120, min(yy, YC + s * (A / 2)), zm - 260, xm - 108, max(yy + 12, YC + s * (A / 2)), zm + 110))
            men.append(caja(xm + 108, min(yy, YC + s * (A / 2)), zm - 260, xm + 120, max(yy + 12, YC + s * (A / 2)), zm + 110))
        pieza(f"4.4-{n}", f"Rodamientos con brida UCF 212 (2) – piso {n}", f"cinta{n}", comp(rod), "acero",
              "fundición gris + rodamiento", (sx_m * 1600, 0, 0), 2, "C = 52,5 kN; C0 = 36 kN (NTN)")
        pieza(f"4.16-{n}", f"Ménsulas PL 12 de los apoyos (2) – piso {n}", "estructura", comp(men), "acero", "F-24",
              (0, 0, 0), 2)
        # tambor de reenvío 4.3 con eje Ø60 entre cubos y muñones Ø50 (Rev. E)
        tr = [tubo(R_REE, R_REE - 6, L_TAMBOR, (xr, YC - L_TAMBOR / 2, zr), (0, 1, 0))]
        for u in (-1044, 1044 - 12):
            tr.append(tubo(R_REE - 6, 58, 12, (xr, YC + u, zr), (0, 1, 0)))
        pieza(f"4.3-{n}", f"Tambor de reenvío Ø250 × 2.100 – piso {n}", f"cinta{n}", comp(tr), "galv",
              "SAE 1020", (-sx_m * 1600, 0, 0), 1)
        ejr = [cil(30, 2 * 1250, (xr, YC - 1250, zr), (0, 1, 0)),
               cil(25, 300, (xr, YC - 1550, zr), (0, 1, 0)), cil(25, 300, (xr, YC + 1250, zr), (0, 1, 0))]
        pieza(f"4.3.1-{n}", f"Eje de reenvío SAE 1045 Ø60 con muñones Ø50 – piso {n}", f"cinta{n}", comp(ejr), "acero",
              "SAE 1045", (-sx_m * 1600, 3200, 0), 1, "Rev. E: Ø60 entre cubos (fatiga)")
        ten = []
        for s in (-1, 1):
            u_ = unidad_tensora_uct210().rotate(V(0, 0, 0), V(0, 0, 1), 90 if p["sentido"] > 0 else -90)
            ten.append(u_.translate(V(xr, YC + s * U_APOYO, zr)))
        pieza(f"4.14-{n}", f"Unidades tensoras UCT 210 con tornillo M20 (2) – piso {n}", f"cinta{n}", comp(ten),
              "galv", "fundición + acero", (-sx_m * 1600, 0, 0), 2, "carrera 150 mm")
        # rodillos de retorno y guías (Rev. F: PTFE en los pisos 2 y 3, que reciben el aire de entrada caliente)
        z_ret = min(zm - R_MOT, zr - R_REE) - 46
        rods = [tubo(44.5, 41.5, B_BANDA + 100, (x, y0b - 50, z_ret), (0, 1, 0)) for x in RET_X if x_a + 300 < x < x_b - 300]
        rods += [cil(10, B_BANDA + 260, (x, y0b - 130, z_ret), (0, 1, 0)) for x in RET_X if x_a + 300 < x < x_b - 300]
        pieza(f"4.6-{n}", f"Rodillos de retorno Ø89 – piso {n}", f"cinta{n}", comp(rods), "galv", "acero galvanizado",
              (0, 0, 0), len(RET_X))
        guias = [caja(x_a + 250, y - 20, z - 24, x_b - 250, y + 20, z - 4) for y in GUIAS_Y]
        mat_g = "UHMW-PE" if n == 1 else "PTFE"
        pieza(f"4.7-{n}", f"Guías {mat_g} 40 × 20 (5) – piso {n}", f"cinta{n}", comp(guias), "uhmw" if n == 1 else "ptfe",
              mat_g, (0, 0, 0), 5, "" if n == 1 else "Rev. F: PTFE (uso continuo hasta 260 °C)")
        # faldones de sellado de los bordes (Rev. F): chapa AISI 304 de 1,5 mm atornillada a la pared con labio de
        # silicona sobre el borde de la banda; cierran la rendija entre la banda y la pared
        fx0, fx1, zf = x_a + 200, x_b - 200, z + esp
        fald = [caja(fx0, E_PANEL, zf, fx1, y0b + 40, zf + 1.5), caja(fx0, E_PANEL, zf, fx1, E_PANEL + 1.5, zf + 60),
                caja(fx0, y1b - 40, zf, fx1, A - E_PANEL, zf + 1.5), caja(fx0, A - E_PANEL - 1.5, zf, fx1, A - E_PANEL, zf + 60)]
        pieza(f"4.21-{n}", f"Faldones de sellado de bordes AISI 304 1,5 mm + labio de silicona (2) – piso {n}", f"cinta{n}",
              comp(fald), "inox", "AISI 304 + goma siliconada", (0, 0, 250), 2, "Rev. F: el aire no sube por los bordes")
        # transmisión: corona Z75 en el eje (lado Sur), cadena, piñón Z15 y motorreductor abajo
        corona, dp2 = rueda_dentada(75, cubo_d=100, agujero=50)
        corona = corona.translate(V(xm, YC - U_CORONA, zm))
        pinon, dp1 = rueda_dentada(15, cubo_d=80, cubo_l=60, agujero=60)
        z_red = zm - 500
        pinon = pinon.translate(V(xm, YC - U_CORONA, z_red))
        cad = cadena((xm, zm), (xm, z_red), dp2 / 2, dp1 / 2).translate(V(0, YC - U_CORONA, 0))
        carter = carter_cadena(xm, zm, z_red, dp2 / 2 + 45, dp1 / 2 + 45, YC - U_CORONA)
        pieza(f"4.15-{n}", f"Transmisión ASA 60: corona Z75, piñón Z15 y cadena – piso {n}", f"trans{n}",
              comp([corona, pinon, cad]), "negro", "acero C45 / ASA 60", (0, -900, 0), 1, "relación 1:5")
        pieza(f"4.15c-{n}", f"Cárter protector de la cadena (chapa 1,6 mm) – piso {n}", f"trans{n}", carter, "amarillo",
              "chapa 1,6 mm", (0, -1500, 0), 1)
        red, mot = motorreductor_doble_sinfin()
        sx = 1 if p["sentido"] > 0 else -1
        red = red.rotate(V(0, 0, 0), V(0, 0, 1), 0 if sx > 0 else 180).translate(V(xm, YC - U_CORONA - 160, z_red))
        mot = mot.rotate(V(0, 0, 0), V(0, 0, 1), 0 if sx > 0 else 180).translate(V(xm, YC - U_CORONA - 160, z_red))
        pieza(f"4.5-{n}", f"Reductor doble sinfín-corona 1:300 – piso {n}", f"trans{n}", red, "reductor",
              "fundición gris", (0, -1300, 0), 1)
        pieza(f"M{4 + n}", f"Motor M{4 + n} 0,75 kW 4 polos IE3 (carcasa 80, B5) – piso {n}", f"trans{n}", mot, "motor",
              "aluminio / acero", (0, -1700, 0), 1, "VFD; ≈ 20 Hz en régimen")
        # consola del motorreductor (4.16b): chapa base 12 mm con colisos, dos cartelas y placa de pared
        cons = consola_motorreductor(xm, YC - U_CORONA, z_red)
        pieza(f"4.16b-{n}", f"Consola del motorreductor con colisos – piso {n}", f"trans{n}", comp(cons), "acero",
              "F-24", (0, -1100, 0), 1)


def accesorios():
    """4.10 tolvas de transferencia, 4.12 campana, 4.13 pasarela, 4.18 esparcidor, 4.19 plenum y descarga."""
    tol = []
    # transferencias: piso 1 (cabeza Este) -> piso 2 (cola Este); piso 2 (cabeza Oeste) -> piso 3 (cola Oeste)
    for (xa, za, xb, zb) in ((PISOS[0]["cabeza"], PISOS[0]["z"], PISOS[1]["cola"], PISOS[1]["z"]),
                              (PISOS[1]["cabeza"], PISOS[1]["z"], PISOS[2]["cola"], PISOS[2]["z"])):
        s = 1 if xb > xa else -1
        chapa = cq.Workplane("XZ").polyline([(xa + s * 250, za - 80), (xa + s * 280, za - 80),
                                             (xb + s * 40, zb + 60), (xb + s * 10, zb + 60)]).close() \
            .extrude(-(B_BANDA + 100)).val().translate(V(0, YC - B_BANDA / 2 - 50, 0))
        tol.append(chapa)
    pieza("4.10", "Tolvas de transferencia entre pisos (chapa inox 2 mm)", "acces", comp(tol), "inox", "AISI 304",
          (0, 0, 0), 2)
    # descarga del piso 3
    td = G["descarga_x"]
    x0d, x1d = td[0] * 1000 - 150, td[1] * 1000 + 50
    tolva_d = cq.Solid.makeLoft([cq.Wire.makePolygon([V(x0d, YC - 1000, HP), V(x1d, YC - 1000, HP), V(x1d, YC + 1000, HP),
                                                      V(x0d, YC - 1000, HP)][:3] + [V(x0d, YC + 1000, HP)], close=True),
                                 cq.Wire.makePolygon([V((x0d + x1d) / 2 - 90, YC - 120, 120), V((x0d + x1d) / 2 + 90, YC - 120, 120),
                                                      V((x0d + x1d) / 2 + 90, YC + 120, 120), V((x0d + x1d) / 2 - 90, YC + 120, 120)], close=True)])
    pieza("4.19a", "Tolva de descarga al sinfín (10)", "acces", tolva_d, "inox", "AISI 304", (0, 0, -600), 1)
    # plenum: entrada de aire caliente por la cara Norte
    ea = G["entrada_aire"]
    brida = caja(ea["x0"] * 1000 - 60, A, ea["z0"] * 1000 - 60, ea["x1"] * 1000 + 60, A + 150, ea["z1"] * 1000 + 60)
    brida = brida.cut(caja(ea["x0"] * 1000, A - 1, ea["z0"] * 1000, ea["x1"] * 1000, A + 151, ea["z1"] * 1000))
    pieza("4.19b", "Boca de entrada de aire caliente 1.200 × 400 con brida (plenum)", "acces", brida, "galv",
          "chapa galv. BWG 18", (0, 1200, 0), 1)
    # campana de salida 800 × 800 y conducto Ø800
    cx = G["campana_x"] * 1000
    camp = cq.Solid.makeLoft([cq.Wire.makePolygon([V(cx - 400, YC - 400, H), V(cx + 400, YC - 400, H),
                                                   V(cx + 400, YC + 400, H), V(cx - 400, YC + 400, H)], close=True),
                              cq.Wire.makeCircle(400, V(cx, YC, H + 350), V(0, 0, 1))])
    camp = comp([camp, tubo(402, 396, 400, (cx, YC, H + 350))])
    pieza("4.12", "Campana de salida 800 × 800 y arranque del conducto Ø800 (17)", "acces", camp, "galv",
          "chapa galv.", (0, 0, 1800), 1)
    # esparcidor 4.18 (rodillo de paletas Ø240 × 2.000) y compuerta niveladora
    ex = G["esparcidor_x"] * 1000
    zp1 = PISOS[0]["z"]
    esp = [cil(40, B_BANDA + 400, (ex, YC - B_BANDA / 2 - 200, zp1 + 150), (0, 1, 0))]
    for k in range(8):
        a = k * 45
        pal = caja(-3, YC - B_BANDA / 2 + 20, 40, 3, YC + B_BANDA / 2 - 20, 120)
        esp.append(pal.rotate(V(0, 0, 0), V(0, 1, 0), a).translate(V(ex, 0, zp1 + 150)))
    pieza("4.18", "Rodillo esparcidor de paletas Ø240 × 2.000 (M9)", "acces", comp(esp), "inox", "AISI 304", (0, 0, 2400), 1)
    cxn = G["compuerta_x"] * 1000
    pieza("4.18b", "Compuerta niveladora regulable (capa de 30 mm)", "acces",
          caja(cxn - 3, YC - B_BANDA / 2, zp1 + 30, cxn + 3, YC + B_BANDA / 2, zp1 + 400), "inox", "AISI 304", (0, 0, 2400), 1)
    # boca de alimentación (llega la cinta de alimentación, plano 12)
    ax = G["alimentacion_x"] * 1000
    boca = caja(ax - 200, YC - 300, H, ax + 200, YC + 300, H + 250).cut(caja(ax - 190, YC - 290, H - 1, ax + 190, YC + 290, H + 251))
    pieza("4.19c", "Boca de alimentación desde la cinta de alimentación (3)", "acces", boca, "inox", "AISI 304", (0, 0, 2000), 1)
    # pasarela superior 4.13: rejilla 0,8 m, baranda 1,0 m con travesaño y rodapié, escalera con jaula
    y0p, y1p = 50, 850
    pas = [caja(300, y0p, H + 5, 12700, y1p, H + 35)]
    for x in range(300, 12701, 1550):
        pas.append(cil(21, 1000, (x, y0p + 25, H + 35)))
    pas.append(cil(21, 12400, (300, y0p + 25, H + 1035), (1, 0, 0)))
    pas.append(cil(17, 12400, (300, y0p + 25, H + 535), (1, 0, 0)))
    pas.append(caja(300, y0p, H + 35, 12700, y0p + 4, H + 185))
    esc = [caja(-560, 200, 0, -540, 260, H + 1100), caja(-560, 640, 0, -540, 700, H + 1100)]
    for z in range(250, int(H) + 1000, 300):
        esc.append(cil(12, 440, (-550, 250, z), (0, 1, 0)))
    for k in range(5):                                   # flejes verticales de la jaula (Ø700)
        a = math.radians(-90 + 45 * k)
        xj, yj = -900 - 350 * math.cos(a), 450 + 350 * math.sin(a)
        esc.append(caja(xj - 4, yj - 25, 2300, xj + 4, yj + 25, H + 1100))
    for z in range(2300, int(H) + 1101, 600):
        esc.append(tubo(360, 352, 30, (-900, 450, z)))
    pieza("4.13", "Pasarela superior con baranda y escalera marinera con jaula", "pasarela",
          comp(pas + esc), "amarillo", "acero pintado amarillo seguridad", (0, -900, 1500), 1)


def construir():
    PIEZAS.clear()
    bastidor()
    cerramiento()
    cintas()
    accesorios()
    return PIEZAS


def masa(forma, material):
    clave = "inox" if "AISI" in material else "uhmw" if "UHMW" in material else "ptfe" if "PTFE" in material \
        else "panel" if "lana" in material \
        else "goma" if "goma" in material and "SAE" not in material else "acero"
    try:
        return forma.Volume() / 1e6 * DENS[clave]
    except Exception:
        return 0.0


def exportar(piezas, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    ens = cq.Assembly(name="Secador SC-4")
    datos = []
    for i, p in enumerate(piezas):
        ens.add(p["forma"], name=f"P{i:03d}", color=cq.Color(*p["color"]))
        bb = p["forma"].BoundingBox()
        datos.append({"id": f"P{i:03d}", "cod": p["cod"], "nombre": p["nombre"], "grupo": p["grupo"],
                      "material": p["material"], "cantidad": p["cantidad"], "nota": p["nota"],
                      "color": p["color"], "explosion_mm": p["explosion"],
                      "centro_mm": [round(bb.center.x, 1), round(bb.center.y, 1), round(bb.center.z, 1)],
                      "caja_mm": [round(bb.xmin), round(bb.ymin), round(bb.zmin), round(bb.xmax), round(bb.ymax), round(bb.zmax)],
                      "masa_kg": round(p["masa_real"] if p["masa_real"] else masa(p["forma"], p["material"]), 1)})
    step = os.path.join(carpeta, "Secador_SC4.step")
    ens.save(step)
    glb = os.path.join(carpeta, "Secador_SC4.glb")
    ens.save(glb, tolerance=0.6, angularTolerance=0.25)
    import trimesh
    esc = trimesh.load(glb, force="scene")
    esc.apply_scale(0.001)
    esc.export(glb)
    with open(os.path.join(carpeta, "piezas.json"), "w", encoding="utf-8") as f:
        json.dump({"offset_planta_mm": OFFSET_PLANTA, "piezas": datos}, f, ensure_ascii=False, indent=1)
    return ens, datos


def main():
    import time
    t0 = time.time()
    piezas = construir()
    print(f"{len(piezas)} piezas en {time.time() - t0:.1f} s")
    ens, datos = exportar(piezas, SALIDA)
    print(f"exportado en {time.time() - t0:.1f} s; masa total {sum(d['masa_kg'] for d in datos):,.0f} kg")
    for d in datos:
        print(f"  {d['cod']:9s} {d['masa_kg']:8.1f} kg  {d['nombre'][:70]}")


if __name__ == "__main__":
    main()
