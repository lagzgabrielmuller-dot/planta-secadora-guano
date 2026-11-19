"""Biblioteca CAD de la granja integrada (CadQuery, sólidos exactos en mm).

- Prototipos: cada pieza distinta se modela una sola vez en su origen y se guarda en un caché.
- Escena: lista de instancias (grupo, código, nombre, prototipo, material, matriz 4×4 en mm).
- Exporta GLB con instancias (trimesh, en metros, Y arriba) y STEP con ensambles (CadQuery/XCAF).

Convenciones: x al Este, y al Norte, z arriba, origen en el vértice Sudoeste de la nave de proceso.
Las matrices no tienen escala ni simetrías (solo rotación y traslación).
"""
from __future__ import annotations

import math
from collections import OrderedDict, defaultdict

import cadquery as cq
import numpy as np
import trimesh
from OCP.gp import gp_Trsf

# ===================================================================================== materiales
# nombre -> (r, g, b, metalicidad, rugosidad, alfa). Blender reemplaza varios por materiales procedurales.
MAT = {
    "acero": (0.33, 0.36, 0.39, 0.85, 0.45, 1.0),
    "acero_pintado": (0.30, 0.34, 0.38, 0.30, 0.55, 1.0),
    "estructura": (0.29, 0.33, 0.38, 0.35, 0.55, 1.0),
    "galv": (0.72, 0.74, 0.76, 0.90, 0.38, 1.0),
    "inox": (0.80, 0.82, 0.84, 1.00, 0.22, 1.0),
    "aluminio": (0.84, 0.85, 0.86, 1.00, 0.30, 1.0),
    "chapa_trap": (0.82, 0.84, 0.85, 0.80, 0.40, 1.0),
    "chapa_techo": (0.74, 0.77, 0.79, 0.85, 0.42, 1.0),
    "panel": (0.93, 0.93, 0.91, 0.05, 0.55, 1.0),
    "panel_galpon": (0.90, 0.91, 0.89, 0.05, 0.50, 1.0),
    "hormigon": (0.70, 0.70, 0.68, 0.00, 0.85, 1.0),
    "hormigon_piso": (0.62, 0.62, 0.60, 0.00, 0.80, 1.0),
    "ladrillo": (0.63, 0.36, 0.26, 0.00, 0.90, 1.0),
    "revoque": (0.86, 0.85, 0.80, 0.00, 0.90, 1.0),
    "amarillo": (0.95, 0.73, 0.08, 0.20, 0.45, 1.0),
    "naranja": (0.93, 0.42, 0.10, 0.20, 0.45, 1.0),
    "rojo": (0.72, 0.10, 0.10, 0.20, 0.45, 1.0),
    "verde": (0.16, 0.48, 0.26, 0.20, 0.50, 1.0),
    "azul_motor": (0.10, 0.27, 0.52, 0.40, 0.40, 1.0),
    "gris_motor": (0.46, 0.50, 0.54, 0.50, 0.45, 1.0),
    "reductor": (0.40, 0.43, 0.47, 0.50, 0.45, 1.0),
    "tablero": (0.86, 0.86, 0.83, 0.20, 0.45, 1.0),       # RAL 7035
    "tablero_int": (0.80, 0.80, 0.78, 0.30, 0.50, 1.0),
    "negro": (0.06, 0.06, 0.07, 0.10, 0.60, 1.0),
    "goma": (0.08, 0.08, 0.09, 0.00, 0.85, 1.0),
    "banda": (0.10, 0.10, 0.11, 0.00, 0.80, 1.0),
    "banda_pp": (0.86, 0.86, 0.80, 0.00, 0.55, 1.0),
    "uhmw": (0.95, 0.95, 0.90, 0.00, 0.50, 1.0),
    "malla": (0.70, 0.72, 0.74, 0.90, 0.40, 0.55),
    "rejilla": (0.66, 0.68, 0.70, 0.85, 0.45, 1.0),
    "vidrio": (0.65, 0.78, 0.85, 0.10, 0.05, 0.30),
    "policarbonato": (0.90, 0.92, 0.94, 0.00, 0.20, 0.45),
    "celulosa": (0.62, 0.52, 0.34, 0.00, 0.95, 1.0),
    "guano": (0.30, 0.24, 0.16, 0.00, 0.95, 1.0),
    "guano_seco": (0.42, 0.33, 0.21, 0.00, 0.95, 1.0),
    "cascara": (0.78, 0.66, 0.42, 0.00, 0.95, 1.0),
    "refractario": (0.70, 0.55, 0.42, 0.00, 0.90, 1.0),
    "aislacion": (0.84, 0.86, 0.87, 0.80, 0.35, 1.0),
    "madera": (0.62, 0.45, 0.27, 0.00, 0.80, 1.0),
    "carton": (0.70, 0.55, 0.36, 0.00, 0.85, 1.0),
    "huevo": (0.93, 0.85, 0.72, 0.00, 0.60, 1.0),
    "plastico_blanco": (0.92, 0.92, 0.90, 0.00, 0.50, 1.0),
    "plastico_gris": (0.45, 0.47, 0.49, 0.00, 0.55, 1.0),
    "pvc_naranja": (0.88, 0.45, 0.14, 0.00, 0.50, 1.0),
    "cobre": (0.72, 0.45, 0.20, 1.00, 0.35, 1.0),
    "cable": (0.12, 0.12, 0.13, 0.00, 0.60, 1.0),
    "asfalto": (0.18, 0.18, 0.19, 0.00, 0.90, 1.0),
    "ripio": (0.55, 0.52, 0.47, 0.00, 0.95, 1.0),
    "pasto": (0.36, 0.48, 0.22, 0.00, 0.95, 1.0),
    "tierra": (0.45, 0.36, 0.26, 0.00, 0.95, 1.0),
    "follaje": (0.22, 0.36, 0.16, 0.00, 0.90, 1.0),
    "tronco": (0.34, 0.25, 0.17, 0.00, 0.90, 1.0),
    "agua": (0.25, 0.40, 0.45, 0.00, 0.05, 0.75),
    "senal_verde": (0.10, 0.55, 0.30, 0.00, 0.50, 1.0),
    "senal_azul": (0.10, 0.30, 0.65, 0.00, 0.50, 1.0),
    "sensor": (0.13, 0.36, 0.62, 0.30, 0.45, 1.0),
    "sensor_amarillo": (0.96, 0.78, 0.10, 0.20, 0.45, 1.0),
    "luz": (1.00, 0.98, 0.92, 0.00, 0.30, 1.0),
    "biofiltro": (0.40, 0.30, 0.18, 0.00, 0.95, 1.0),
}

# ===================================================================================== matrices
I4 = np.eye(4)


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def Rx(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])


def Ry(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])


def Rz(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


def alinear(p0, p1, up=(0, 0, 1)):
    """Matriz que lleva el eje +Z local de p0 a p1; el eje +X local queda lo más cerca posible de `up` ⊥."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ez = p1 - p0
    n = np.linalg.norm(ez)
    ez = ez / n if n else np.array([0, 0, 1.0])
    up = np.asarray(up, float)
    ex = up - np.dot(up, ez) * ez
    if np.linalg.norm(ex) < 1e-6:
        alt = np.array([1.0, 0, 0]) if abs(ez[0]) < 0.9 else np.array([0, 1.0, 0])
        ex = alt - np.dot(alt, ez) * ez
    ex /= np.linalg.norm(ex)
    ey = np.cross(ez, ex)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = ex, ey, ez, p0
    return m


def _lineal(c):
    """sRGB (0-1) a lineal."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _trsf(m):
    t = gp_Trsf()
    t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return t


# ===================================================================================== prototipos
_PROTO: "OrderedDict[tuple, cq.Shape]" = OrderedDict()


def proto(key, constructor):
    if key not in _PROTO:
        s = constructor()
        if isinstance(s, cq.Workplane):
            vals = [v for v in s.vals() if isinstance(v, cq.Shape)]
            s = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
        elif isinstance(s, (list, tuple)):
            vals = []
            for w in s:
                vals += [v for v in (w.vals() if isinstance(w, cq.Workplane) else [w]) if isinstance(v, cq.Shape)]
            s = cq.Compound.makeCompound(vals)
        _PROTO[key] = s
    return key


def forma(key):
    return _PROTO[key]


def _r(v, d=1):
    return round(float(v), d)


def wp():
    return cq.Workplane("XY")


def caja0(dx, dy, dz):
    return wp().box(dx, dy, dz, centered=False)


def cil0(r, h):
    return wp().circle(r).extrude(h)


def tubo0(R, r, h):
    return wp().circle(R).circle(r).extrude(h)


def cono0(r0, r1, h):
    return cq.Workplane("XY").add(cq.Solid.makeCone(r0, r1, h))


def hex0(s, h):
    return wp().polygon(6, s / math.cos(math.radians(30))).extrude(h)


# ----------------------------------------------------------------------------- secciones de perfiles (en XY)
def _seccion(tipo, d):
    if tipo == "I":                       # h, b, tw, tf: alma según Y, alas según X
        h, b, tw, tf = d
        pts = [(-b / 2, -h / 2), (b / 2, -h / 2), (b / 2, -h / 2 + tf), (tw / 2, -h / 2 + tf), (tw / 2, h / 2 - tf),
               (b / 2, h / 2 - tf), (b / 2, h / 2), (-b / 2, h / 2), (-b / 2, h / 2 - tf), (-tw / 2, h / 2 - tf),
               (-tw / 2, -h / 2 + tf), (-b / 2, -h / 2 + tf)]
        return wp().polyline(pts).close()
    if tipo == "U":                       # h, b, tw, tf: alma en x = 0, alas hacia +X
        h, b, tw, tf = d
        pts = [(0, -h / 2), (b, -h / 2), (b, -h / 2 + tf), (tw, -h / 2 + tf), (tw, h / 2 - tf), (b, h / 2 - tf),
               (b, h / 2), (0, h / 2)]
        return wp().polyline(pts).close()
    if tipo == "C":                       # perfil C plegado: h, b, c (labio), t
        h, b, c, t = d
        pts = [(0, -h / 2), (b, -h / 2), (b, -h / 2 + c), (b - t, -h / 2 + c), (b - t, -h / 2 + t), (t, -h / 2 + t),
               (t, h / 2 - t), (b - t, h / 2 - t), (b - t, h / 2 - c), (b, h / 2 - c), (b, h / 2), (0, h / 2)]
        return wp().polyline(pts).close()
    if tipo == "L":                       # a (según X), b (según Y), t
        a, b, t = d
        pts = [(0, 0), (a, 0), (a, t), (t, t), (t, b), (0, b)]
        return wp().polyline(pts).close()
    if tipo == "RHS":                     # b (X), h (Y), t
        b, h, t = d
        return wp().rect(b, h).rect(b - 2 * t, h - 2 * t)
    if tipo == "CHS":                     # D, t
        D_, t = d
        return wp().circle(D_ / 2).circle(D_ / 2 - t)
    if tipo == "FB":                      # planchuela b (X), t (Y)
        b, t = d
        return wp().rect(b, t)
    if tipo == "RB":                      # redondo
        (D_,) = d
        return wp().circle(D_ / 2)
    raise ValueError(tipo)


PERFILES = {  # dimensiones normalizadas (mm)
    "IPN 300": ("I", (300, 125, 10.8, 16.2)), "IPN 200": ("I", (200, 90, 7.5, 11.3)), "IPN 160": ("I", (160, 74, 6.3, 9.5)),
    "IPN 140": ("I", (140, 66, 5.7, 8.6)), "IPE 200": ("I", (200, 100, 5.6, 8.5)), "IPE 160": ("I", (160, 82, 5.0, 7.4)),
    "HEB 140": ("I", (140, 140, 7.0, 12.0)), "HEB 160": ("I", (160, 160, 8.0, 13.0)), "HEB 120": ("I", (120, 120, 6.5, 11.0)),
    "UPN 200": ("U", (200, 75, 8.5, 11.5)), "UPN 160": ("U", (160, 65, 7.5, 10.5)), "UPN 140": ("U", (140, 60, 7.0, 10.0)),
    "UPN 120": ("U", (120, 55, 7.0, 9.0)), "UPN 100": ("U", (100, 50, 6.0, 8.5)), "UPN 80": ("U", (80, 45, 6.0, 8.0)),
    "C 200": ("C", (200, 70, 20, 2.5)), "C 160": ("C", (160, 60, 20, 2.0)), "C 120": ("C", (120, 50, 15, 2.0)),
    "C 100": ("C", (100, 50, 15, 2.0)), "C 80": ("C", (80, 40, 15, 1.6)),
    "L 80": ("L", (80, 80, 8)), "L 63": ("L", (63.5, 63.5, 6.35)), "L 50": ("L", (50, 50, 5)), "L 40": ("L", (40, 40, 4)),
    "L 30": ("L", (30, 30, 3)),
    "RHS 150": ("RHS", (150, 150, 6)), "RHS 120": ("RHS", (120, 120, 5)), "RHS 100": ("RHS", (100, 100, 4)),
    "RHS 80": ("RHS", (80, 80, 3.2)), "RHS 60": ("RHS", (60, 60, 3.2)), "RHS 50": ("RHS", (50, 50, 2.5)),
    "RHS 40": ("RHS", (40, 40, 2)), "RHS 100x50": ("RHS", (50, 100, 3.2)),
    "CHS 114": ("CHS", (114.3, 4.5)), "CHS 89": ("CHS", (88.9, 4.0)), "CHS 76": ("CHS", (76.1, 3.2)),
    "CHS 60": ("CHS", (60.3, 3.2)), "CHS 48": ("CHS", (48.3, 3.2)), "CHS 42": ("CHS", (42.2, 2.6)),
    "CHS 33": ("CHS", (33.7, 2.6)), "CHS 27": ("CHS", (26.9, 2.3)), "CHS 21": ("CHS", (21.3, 2.0)),
    "FB 100x10": ("FB", (100, 10)), "FB 150x6": ("FB", (150, 6)), "FB 50x6": ("FB", (50, 6)), "FB 30x5": ("FB", (30, 5)),
    "RB 16": ("RB", (16,)), "RB 12": ("RB", (12,)), "RB 20": ("RB", (20,)), "RB 6": ("RB", (6,)), "RB 4": ("RB", (4,)),
    "RB 3": ("RB", (3,)),
}


def perfil_proto(nombre, L):
    tipo, d = PERFILES[nombre]
    L = max(1.0, _r(L, 0))
    return proto(("perfil", nombre, L), lambda: _seccion(tipo, d).extrude(L))


# ----------------------------------------------------------------------------- tornillería (ISO 4014/4032, simplificada)
def bulon_proto(d, largo, tuerca_a=None):
    """Bulón hexagonal con arandela, saliendo de la superficie (z = 0) hacia +Z la cabeza y hacia −Z el vástago.
    Si `tuerca_a` (mm) está, agrega arandela y tuerca a esa profundidad."""
    def c():
        s, k, m = 1.6 * d, 0.65 * d, 0.85 * d
        partes = [hex0(s, k).translate((0, 0, 0.18 * d)),
                  cil0(1.05 * d, 0.18 * d),
                  cil0(d / 2, largo).translate((0, 0, -largo))]
        if tuerca_a is not None:
            partes += [cil0(1.05 * d, 0.18 * d).translate((0, 0, -tuerca_a - 0.18 * d)),
                       hex0(s, m).translate((0, 0, -tuerca_a - 0.18 * d - m))]
        return partes
    return proto(("bulon", d, _r(largo, 0), tuerca_a), c)


def tuerca_proto(d):
    return proto(("tuerca", d), lambda: [cil0(1.05 * d, 0.18 * d), hex0(1.6 * d, 0.85 * d).translate((0, 0, 0.18 * d))])


# ===================================================================================== escena
class Escena:
    def __init__(self, nombre="escena"):
        self.nombre = nombre
        self.inst = []            # dicts: grupo, cod, nom, key, mat, M
        self.mallas = []          # mallas sueltas (trimesh) en m, con su grupo: carteles, terreno
        self.grupo = "general"

    def en(self, grupo):
        self.grupo = grupo
        return self

    def add(self, key, mat, M=I4, cod="", nom="", grupo=None):
        if mat not in MAT:
            raise KeyError(mat)
        self.inst.append({"grupo": grupo or self.grupo, "cod": cod, "nom": nom, "key": key, "mat": mat,
                          "M": np.array(M, float)})

    # ------------------------------------------------------------------ primitivas colocadas
    def caja(self, x0, y0, z0, x1, y1, z1, mat, cod="", nom="", M=I4):
        dx, dy, dz = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
        if min(dx, dy, dz) <= 0.01:
            return
        k = proto(("caja", _r(dx), _r(dy), _r(dz)), lambda: caja0(_r(dx), _r(dy), _r(dz)))
        self.add(k, mat, M @ T(min(x0, x1), min(y0, y1), min(z0, z1)), cod, nom)

    def caja_rot(self, centro, dims, rotz, mat, cod="", nom="", M=I4):
        dx, dy, dz = dims
        k = proto(("caja", _r(dx), _r(dy), _r(dz)), lambda: caja0(_r(dx), _r(dy), _r(dz)))
        self.add(k, mat, M @ T(*centro) @ Rz(rotz) @ T(-dx / 2, -dy / 2, -dz / 2), cod, nom)

    def cil(self, p0, p1, r, mat, cod="", nom="", M=I4):
        L = float(np.linalg.norm(np.subtract(p1, p0)))
        if L < 0.5:
            return
        k = proto(("cil", _r(r), _r(L, 0)), lambda: cil0(_r(r), _r(L, 0)))
        self.add(k, mat, M @ alinear(p0, p1), cod, nom)

    def tubo(self, p0, p1, R, r, mat, cod="", nom="", M=I4):
        L = float(np.linalg.norm(np.subtract(p1, p0)))
        if L < 0.5:
            return
        k = proto(("tubo", _r(R), _r(r), _r(L, 0)), lambda: tubo0(_r(R), _r(r), _r(L, 0)))
        self.add(k, mat, M @ alinear(p0, p1), cod, nom)

    def cono(self, p0, p1, r0, r1, mat, cod="", nom="", M=I4):
        L = float(np.linalg.norm(np.subtract(p1, p0)))
        k = proto(("cono", _r(r0), _r(r1), _r(L, 0)), lambda: cono0(_r(r0), _r(r1), _r(L, 0)))
        self.add(k, mat, M @ alinear(p0, p1), cod, nom)

    def esfera(self, c, r, mat, cod="", nom="", M=I4):
        k = proto(("esfera", _r(r)), lambda: wp().sphere(_r(r)))
        self.add(k, mat, M @ T(*c), cod, nom)

    def barra(self, p0, p1, perfil, mat, up=(0, 0, 1), cod="", nom="", M=I4, giro=0.0):
        L = float(np.linalg.norm(np.subtract(p1, p0)))
        if L < 1:
            return
        k = perfil_proto(perfil, L)
        self.add(k, mat, M @ alinear(p0, p1, up) @ Rz(giro), cod, nom or perfil)

    def polilinea(self, pts, r, mat, cod="", nom="", M=I4, codos=True):
        for a, b in zip(pts, pts[1:]):
            self.cil(a, b, r, mat, cod, nom, M)
        if codos:
            for p in pts[1:-1]:
                self.esfera(p, r, mat, cod, nom, M)

    def bulon(self, p, n, d, largo, mat="galv", tuerca_a=None, cod="", nom="", M=I4):
        """Bulón con la cabeza en p, normal saliente n (cabeza hacia +n)."""
        k = bulon_proto(d, largo, tuerca_a)
        self.add(k, mat, M @ alinear(p, np.add(p, n)), cod, nom or f"Bulón M{d}")

    def bulones_rect(self, c, ux, uy, n, nx, ny, sx, sy, d, largo, mat="galv", M=I4, cod="", nom=""):
        c, ux, uy = np.asarray(c, float), np.asarray(ux, float), np.asarray(uy, float)
        for i in range(nx):
            for j in range(ny):
                ox = (i - (nx - 1) / 2) * sx if nx > 1 else 0
                oy = (j - (ny - 1) / 2) * sy if ny > 1 else 0
                self.bulon(c + ux * ox + uy * oy, n, d, largo, mat, cod=cod, nom=nom, M=M)

    def bulones_circ(self, c, n, R, cant, d, largo, mat="galv", fase=0.0, M=I4, cod="", nom=""):
        c, n = np.asarray(c, float), np.asarray(n, float) / np.linalg.norm(n)
        a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
        u = a - np.dot(a, n) * n
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        for i in range(cant):
            t = fase + 2 * math.pi * i / cant
            self.bulon(c + R * (math.cos(t) * u + math.sin(t) * v), n, d, largo, mat, cod=cod, nom=nom, M=M)

    def proto_en(self, key, mat, M, cod="", nom=""):
        self.add(key, mat, M, cod, nom)

    def malla_suelta(self, mesh_m, grupo=None):
        self.mallas.append((grupo or self.grupo, mesh_m))

    # ------------------------------------------------------------------ resumen y exportación
    def grupos(self):
        return sorted({i["grupo"] for i in self.inst} | {g for g, _ in self.mallas})

    def piezas(self):
        cuenta = defaultdict(int)
        for i in self.inst:
            if i["cod"] or i["nom"]:
                cuenta[(i["grupo"], i["cod"], i["nom"], i["mat"])] += 1
        return [{"grupo": g, "cod": c, "nom": n, "mat": m, "cant": k} for (g, c, n, m), k in sorted(cuenta.items())]

    def exportar_glb(self, ruta, filtro=None, tol_rel=1 / 400, max_tol=6.0):
        escena = trimesh.Scene()
        C = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])      # Z arriba -> Y arriba
        S = np.diag([0.001, 0.001, 0.001, 1.0])
        mallas = {}
        nodos_grupo = set()
        n = 0
        for i in self.inst:
            if filtro and not filtro(i):
                continue
            gk = (i["key"], i["mat"])
            if gk not in mallas:
                sh = forma(i["key"])
                bb = sh.BoundingBox()
                diag = math.sqrt(bb.xlen ** 2 + bb.ylen ** 2 + bb.zlen ** 2)
                tol = min(max_tol, max(0.15, diag * tol_rel))
                vs, fs = sh.tessellate(tol, 0.35)
                if not fs:
                    mallas[gk] = None
                    continue
                v = np.array([(p.x, p.y, p.z) for p in vs]) * 0.001
                m = trimesh.Trimesh(vertices=v, faces=np.array(fs), process=False)
                r, g_, b, met, rug, a = MAT[i["mat"]]
                r, g_, b = (_lineal(c) for c in (r, g_, b))       # glTF guarda el color base en espacio lineal
                pbr = trimesh.visual.material.PBRMaterial(
                    name=i["mat"], baseColorFactor=[int(r * 255), int(g_ * 255), int(b * 255), int(a * 255)],
                    metallicFactor=met, roughnessFactor=rug, alphaMode="BLEND" if a < 1 else "OPAQUE",
                    doubleSided=a < 1)
                m.visual = trimesh.visual.TextureVisuals(material=pbr)
                _ = m.vertex_normals
                nombre = f"m{len(mallas)}_{i['mat']}"
                escena.geometry[nombre] = m
                mallas[gk] = nombre
            nombre = mallas[gk]
            if nombre is None:
                continue
            grupo = "G:" + i["grupo"]
            if grupo not in nodos_grupo:
                escena.graph.update(frame_from=escena.graph.base_frame, frame_to=grupo, matrix=C)
                nodos_grupo.add(grupo)
            M = i["M"].copy()
            M[:3, 3] *= 0.001
            etiqueta = (i["cod"] + " " + i["nom"]).strip() or "pieza"
            escena.graph.update(frame_from=grupo, frame_to=f"{etiqueta}#{n}", matrix=M, geometry=nombre)
            n += 1
        for grupo, mm in self.mallas:
            if filtro and not filtro({"grupo": grupo, "cod": "", "nom": "", "mat": ""}):
                continue
            gname = "G:" + grupo
            if gname not in nodos_grupo:
                escena.graph.update(frame_from=escena.graph.base_frame, frame_to=gname, matrix=C)
                nodos_grupo.add(gname)
            nombre = f"suelta{len(escena.geometry)}"
            escena.geometry[nombre] = mm
            escena.graph.update(frame_from=gname, frame_to=f"{nombre}#{n}", matrix=np.eye(4), geometry=nombre)
            n += 1
        datos = escena.export(file_type="glb", include_normals=True)
        with open(ruta, "wb") as f:
            f.write(datos)
        return {"instancias": n, "mallas": len(escena.geometry), "bytes": len(datos)}

    def exportar_step(self, ruta, filtro=None, nombre=None):
        raiz = cq.Assembly(name=nombre or self.nombre)
        subs = {}
        cont = defaultdict(int)
        for i in self.inst:
            if filtro and not filtro(i):
                continue
            g = i["grupo"]
            if g not in subs:
                subs[g] = cq.Assembly(name=g.replace(" ", "_"))
            r, g_, b, _m, _r2, a = MAT[i["mat"]]
            base = (i["cod"] or i["nom"] or "pieza").replace(" ", "_").replace("/", "-")[:60]
            cont[(g, base)] += 1
            subs[g].add(forma(i["key"]), name=f"{base}_{cont[(g, base)]}", loc=cq.Location(_trsf(i["M"])),
                        color=cq.Color(r, g_, b, a))
        for g, s in subs.items():
            raiz.add(s, name=g.replace(" ", "_"))
        raiz.save(str(ruta), exportType="STEP")
        return {"instancias": sum(cont.values()), "subensambles": len(subs)}
