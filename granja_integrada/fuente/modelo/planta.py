"""Planta central de secado (Fases 6 y 7).

- Nave de proceso de la Rev. F (33 × 18 m, alero +7,00, cumbrera +8,35) reconstruida con estructura de detalle:
  pórticos con columnas IPN 300, cerchas tubulares, columnas de hastial, correas, vigas de borde, arriostramientos,
  placas base y anclajes, zócalo, cerramientos con todas las aberturas, portones, puertas, ventanas, techo con
  lucernarios, cumbrera, extractores eólicos, canaletas, bajadas e iluminación.
- Equipos de la Rev. F importados de la geometría del visor original (`datos/base/geo_revF.json.gz`, capturada con
  `fuente/capturar_geometria.js` del proyecto anterior), sin el biogás, sin la recepción por camión y pala, y con
  los ajustes que pide la granja (tanque de incendio corrido, campana de recepción reemplazada por la aspiración
  de la tolva pulmón).
- Secador SC-4 con el modelo CadQuery detallado del proyecto anterior (68 piezas).
- Piloto a GLP del hogar (reemplaza al piloto a biogás).
"""
from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

import cad
import componentes as C
from cad import MAT, T, Rx, Ry, Rz, alinear, proto, wp

RAIZ = Path(__file__).resolve().parents[2]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
NAVE = D["planta"]["nave"]
GEO = RAIZ / "datos" / "base" / "geo_revF.json.gz"
SECADORA = RAIZ.parent / "fuente" / "secadora"        # modelo del secador SC-4 (proyecto anterior, solo lectura)

# ===================================================================================== equipos de la Rev. F
EXCLUIR = {
    "N": "nave: se reconstruye con estructura de detalle",
    "1": "playa de recepción con pila y muro de contención: la reemplaza la tolva pulmón",
    "2": "tolva de recepción de 3,1 m³: la reemplaza la tolva pulmón TP-01",
    "3.6": "faldones bajo la tolva vieja: la TP-01 tiene sus bocas y faldones",
    "5": "esparcidor: viene con el SC-4 detallado",
    "6x": "",
    "E1": "estación de lavado de vehículos en el acceso viejo: el vado nuevo está en el portón de la granja",
    "E2": "lavadero de camiones de guano: ya no entran camiones de guano",
    "E8.1": "biogás", "E8.2": "biogás", "E8.3": "biogás", "E8.4": "biogás", "E8.5": "biogás", "E8.6": "biogás",
    "E9": "sector Este del predio viejo: ahí van los galpones G3 y G4",
    "D24": "flechas de flujo del visor viejo (mostraban la pala cargadora)",
    "L": "pala cargadora", "MC": "minicargadora", "AU1": "vehículo", "AU2": "vehículo", "AU3": "vehículo",
    "CA": "vehículo", "CB": "vehículo", "CC": "vehículo",
    "terreno": "terreno del predio viejo", "30": "báscula vieja", "31": "garita vieja", "32": "playones viejos",
    "33": "cerco viejo", "34": "estacionamiento viejo", "pilar": "pilar de acometida viejo",
}
GRUPOS = {
    "Planta - alimentación del secador": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.8", "26"],
    "Planta - generador de aire caliente": ["AN", "9", "10", "11", "12", "15", "16", "D8", "D12", "D14"],
    "Planta - cáscara de arroz": ["13", "14", "D13"],
    "Planta - tratamiento de aire": ["17", "18", "19", "20", "21", "E3", "F2", "D7", "D10", "D11"],
    "Planta - descarga y envasado": ["6", "7", "8", "F1", "E4", "E5", "E6", "28"],
    "Planta - edificios auxiliares": ["22", "23", "24", "25", "E7"],
    "Planta - instalación eléctrica": ["TGF", "29", "D15", "D16", "D17", "D4", "D5"],
    "Planta - seguridad y mantenimiento": ["D2", "D3", "D6", "D9", "D18", "D19", "D20", "D21", "D22", "D23", "27", "E10"],
}
GRUPO_DE = {k: g for g, ks in GRUPOS.items() for k in ks}


def _filtro_item(k, lo, hi):
    """Devuelve (incluir, desplazamiento) para un ítem de la parte k con caja [lo, hi] (m, proyecto)."""
    c = (lo + hi) / 2
    en_recepcion = c[0] < 9.6 and c[1] < 18.2
    if k == "7" and np.linalg.norm(c) < 0.5:
        return False, None                      # cangilones sin ubicar del visor viejo
    if k == "E3":
        if en_recepcion or c[2] > 8.2:
            return False, None                  # campana, ducto de la recepción y eólicos (van en la nave nueva)
        if 18.2 <= c[1] <= 19.3 and lo[2] > 6.3 and hi[0] > 6.0:
            return False, None                  # tramo horizontal del ducto viejo que venía de la campana
    if k in ("D16", "D19") and c[0] > 40.0:
        return False, None                      # puesta a tierra y matafuegos de la zona de biogás
    if k in ("D5", "D9", "D18") and 0.9 < c[0] < 4.2 and 8.2 < c[1] < 10.5 and c[2] > 0.8:
        return False, None                      # sensor, boca de limpieza y cartel de la tolva vieja
    if k == "E10" and c[0] < 9.6 and 4.5 < c[1] < 6.5:
        return True, np.array([-3.0, 0.0, 0.0])  # circulador sobre ruedas: se corre para liberar la escalera de la TP-01
    if k == "D17" and c[0] < 0.3 and 13.5 < c[1] < 16.5:
        return True, np.array([0.0, -2.6, 0.0])  # luminaria del muro Oeste: ahí entra la CP-O
    if k == "27":
        return True, np.array([-5.5, 0.0, 0.0])  # tanque de incendio y casilla de bombas (camino C2)
    return True, None


def _material_rgb(hexcol, op, nombre=None):
    r, g, b = ((hexcol >> 16) & 255) / 255, ((hexcol >> 8) & 255) / 255, (hexcol & 255) / 255
    gris = max(r, g, b) - min(r, g, b) < 0.12
    met = 0.35 if gris and 0.25 < (r + g + b) / 3 < 0.8 else 0.05
    lin = [cad._lineal(c) for c in (r, g, b)]
    return trimesh.visual.material.PBRMaterial(
        name=nombre or f"rf_{hexcol:06x}", baseColorFactor=[int(v * 255) for v in lin] + [int(op * 255)],
        metallicFactor=met, roughnessFactor=0.6, alphaMode="BLEND" if op < 0.99 else "OPAQUE", doubleSided=op < 0.99)


def importar_revF(e, informe=None):
    """Agrega los equipos de la Rev. F como mallas (una por parte y color)."""
    geo = json.loads(gzip.open(GEO, "rt", encoding="utf-8").read())
    partes, nombres = geo["partes"], geo.get("nombres", {})
    acum = {}
    contados = {"incluidas": 0, "excluidas": 0, "items_filtrados": 0}
    for k, items in partes.items():
        if k in EXCLUIR or k.startswith("4."):
            contados["excluidas"] += 1
            continue
        contados["incluidas"] += 1
        grupo = GRUPO_DE.get(k, "Planta - otros equipos")
        for it in items:
            if "tri" not in it or not it["tri"]:
                continue
            m = np.array(it["m"], float).reshape(4, 4).T
            v = np.array(it["tri"], float).reshape(-1, 3)
            w = (m @ np.c_[v, np.ones(len(v))].T).T[:, :3]
            p = np.c_[w[:, 0], -w[:, 2], w[:, 1]]                   # three.js (Y arriba) -> proyecto (Z arriba)
            ok, dxyz = _filtro_item(k, p.min(0), p.max(0))
            if not ok:
                contados["items_filtrados"] += 1
                continue
            if dxyz is not None:
                p = p + dxyz
            col = it.get("tex") if it.get("mapa") and it.get("tex") is not None else it.get("c", 0x999999)
            op = round(float(it.get("op", 1.0)), 2)
            if k == "E7" and op < 0.99 and int(col) in (0xFFFFFF, 0xDFE4E6):
                op = 1.0                                # el visor viejo mostraba los muros del E7 translúcidos
            clave = (grupo, k, int(col), op)
            acum.setdefault(clave, []).append(p)
    for (grupo, k, col, op), lista in acum.items():
        V = np.vstack(lista)
        F = np.arange(len(V)).reshape(-1, 3)
        malla = trimesh.Trimesh(vertices=V, faces=F, process=True)
        malla.visual = trimesh.visual.TextureVisuals(material=_material_rgb(col, op))
        malla.metadata["name"] = f"{k} {nombres.get(k, '')}"
        e.malla_suelta(malla, grupo)
    if informe is not None:
        informe.update(contados)
        informe["excluidas"] = {k: v for k, v in EXCLUIR.items() if v}
    return nombres


# ===================================================================================== secador SC-4 detallado
SC4_MAT = {"acero": "estructura", "galv": "galv", "inox": "inox", "panel": "panel", "panel_int": "panel_int",
           "malla": "inox", "goma": "goma", "motor": "azul_motor", "reductor": "reductor", "amarillo": "amarillo",
           "uhmw": "uhmw", "ptfe": "uhmw", "rojo": "rojo", "negro": "negro", "bronce": "bronce", "verde": "verde",
           "hormigon": "hormigon"}
MAT.setdefault("panel_int", (0.78, 0.80, 0.82, 0.30, 0.45, 1.0))
MAT.setdefault("bronce", (0.72, 0.55, 0.30, 0.90, 0.35, 1.0))


def secador_sc4(e):
    sys.path.insert(0, str(SECADORA))
    import modelo_secador as ms               # noqa: E402  (proyecto anterior, se usa sin modificarlo)
    inversa = {tuple(round(c, 3) for c in v): k for k, v in ms.C.items()}
    piezas = ms.construir()
    off = T(*ms.OFFSET_PLANTA)
    e.en("Secador SC-4")
    for p in piezas:
        nom_color = inversa.get(tuple(round(c, 3) for c in p["color"]), "acero")
        k = proto(("sc4", p["cod"]), lambda p=p: p["forma"])
        e.add(k, SC4_MAT.get(nom_color, "estructura"), off, p["cod"], p["nombre"])
    return piezas


# ===================================================================================== nave de proceso reconstruida
def _y_techo(y):
    """Cota de la cara superior del techo (mm) en la ordenada y (mm)."""
    A, ha, hc = NAVE["A"] * 1000, NAVE["h_alero"] * 1000, NAVE["h_cumbrera"] * 1000
    return ha + (hc - ha) * (1 - abs(y - A / 2) / (A / 2))


def _rectangulos_libres(u0, u1, z0, z1, huecos):
    """Parte el rectángulo [u0, u1] × [z0, z1] en rectángulos que no pisan los huecos (u0, u1, z0, z1)."""
    cortes = sorted({u0, u1} | {h[0] for h in huecos if u0 < h[0] < u1} | {h[1] for h in huecos if u0 < h[1] < u1})
    res = []
    for a, b in zip(cortes, cortes[1:]):
        if b - a < 1:
            continue
        m = (a + b) / 2
        hs = sorted((h[2], h[3]) for h in huecos if h[0] <= m <= h[1])
        z = z0
        for h0, h1 in hs:
            if h0 > z:
                res.append((a, b, z, min(h0, z1)))
            z = max(z, h1)
        if z < z1:
            res.append((a, b, z, z1))
    return [r for r in res if r[3] - r[2] > 1]


def _pared(e, eje, pos, u0, u1, z0, z1, huecos, cara, nom, mat="chapa_trap", esp=30, tag="NAVE"):
    """Chapa de cerramiento en el plano eje = pos (eje 'x' o 'y'), del lado `cara` (+1 hacia afuera = +eje)."""
    for (a, b, za, zb) in _rectangulos_libres(u0, u1, z0, z1, huecos):
        if eje == "y":
            e.caja(a, pos, za, b, pos + cara * esp, zb, mat, tag, nom)
        else:
            e.caja(pos, a, za, pos + cara * esp, b, zb, mat, tag, nom)


def _correas_pared(e, eje, pos, u0, u1, zs, huecos, tag="NAVE"):
    """Correas de pared C 100 que se interrumpen en los huecos, con marcos L 50 en los bordes."""
    for z in zs:
        tramos = [(u0, u1)]
        for h in huecos:
            if h[2] - 60 <= z <= h[3] + 60:
                nuevo = []
                for a, b in tramos:
                    if h[1] <= a or h[0] >= b:
                        nuevo.append((a, b))
                    else:
                        if h[0] - a > 100:
                            nuevo.append((a, h[0]))
                        if b - h[1] > 100:
                            nuevo.append((h[1], b))
                tramos = nuevo
        for a, b in tramos:
            p0 = (a, pos, z) if eje == "y" else (pos, a, z)
            p1 = (b, pos, z) if eje == "y" else (pos, b, z)
            e.barra(p0, p1, "C 100", "estructura", up=(0, 0, 1), cod=tag, nom="Correa de pared C 100")
    for (a, b, z0, z1) in huecos:                       # marco del hueco
        for u in (a, b):
            p0 = (u, pos, z0) if eje == "y" else (pos, u, z0)
            p1 = (u, pos, z1) if eje == "y" else (pos, u, z1)
            e.barra(p0, p1, "L 50", "estructura", cod=tag, nom="Marco de abertura L 50")
        for z in (z0, z1):
            if z > 50:
                p0 = (a, pos, z) if eje == "y" else (pos, a, z)
                p1 = (b, pos, z) if eje == "y" else (pos, b, z)
                e.barra(p0, p1, "L 50", "estructura", cod=tag, nom="Dintel / antepecho L 50")


def _ventana(e, eje, pos, a, b, z0, z1, cara, tag="NAVE"):
    if eje == "y":
        e.caja(a, pos - 20, z0, b, pos + 20, z1, "vidrio", tag, "Ventana de aluminio con vidrio laminado 3+3")
        for u in np.linspace(a, b, max(2, int((b - a) / 900) + 1)):
            e.caja(u - 20, pos - 30, z0, u + 20, pos + 30, z1, "aluminio", tag, "")
        for z in (z0, z1 - 40):
            e.caja(a, pos - 30, z, b, pos + 30, z + 40, "aluminio", tag, "")
    else:
        e.caja(pos - 20, a, z0, pos + 20, b, z1, "vidrio", tag, "Ventana de aluminio con vidrio laminado 3+3")
        for u in np.linspace(a, b, max(2, int((b - a) / 900) + 1)):
            e.caja(pos - 30, u - 20, z0, pos + 30, u + 20, z1, "aluminio", tag, "")
        for z in (z0, z1 - 40):
            e.caja(pos - 30, a, z, pos + 30, b, z + 40, "aluminio", tag, "")


def _porton(e, eje, pos, a, b, h, cara, cod, nom):
    """Portón seccional de paneles con riel, motor y botonera."""
    for z in np.arange(0, h - 1, 500):
        if eje == "y":
            e.caja(a, pos - 25, z + 5, b, pos + 25, min(h, z + 495), "chapa_trap", cod, nom if z == 0 else "")
        else:
            e.caja(pos - 25, a, z + 5, pos + 25, b, min(h, z + 495), "chapa_trap", cod, nom if z == 0 else "")
    for u in (a, b):
        p0 = (u, pos - cara * 80, 0) if eje == "y" else (pos - cara * 80, u, 0)
        p1 = (u, pos - cara * 80, h + 400) if eje == "y" else (pos - cara * 80, u, h + 400)
        e.barra(p0, p1, "L 63", "galv", cod=cod, nom="Riel del portón seccional")
    c = ((a + b) / 2, pos - cara * 250, h + 450) if eje == "y" else (pos - cara * 250, (a + b) / 2, h + 450)
    e.caja_rot(c, (450, 250, 250) if eje == "y" else (250, 450, 250), 0, "gris_motor", cod, "Motor del portón seccional")
    bot = (b + 300, pos - cara * 40, 1300) if eje == "y" else (pos - cara * 40, b + 300, 1300)
    C.botonera(e, bot, (0, -cara, 0) if eje == "y" else (-cara, 0, 0), tag=cod)


def _puerta(e, eje, pos, a, b, h, cara, cod, nom, mat="acero_pintado"):
    if eje == "y":
        e.caja(a, pos - 25, 0, b, pos + 25, h, mat, cod, nom)
        e.caja(a - 50, pos - 40, h, b + 50, pos + 40, h + 50, "estructura", cod, "")
        e.caja(b - 150, pos - cara * 70, 1000, b - 120, pos - cara * 30, 1100, "inox", cod, "Barral antipánico")
    else:
        e.caja(pos - 25, a, 0, pos + 25, b, h, mat, cod, nom)
        e.caja(pos - 40, a - 50, h, pos + 40, b + 50, h + 50, "estructura", cod, "")
        e.caja(pos - cara * 70, b - 150, 1000, pos - cara * 30, b - 120, 1100, "inox", cod, "Barral antipánico")
    C.placa(e, ((a + b) / 2, pos + cara * 30, h + 250) if eje == "y" else (pos + cara * 30, (a + b) / 2, h + 250),
            (0, cara, 0) if eje == "y" else (cara, 0, 0), 400, 150, "senal_verde", tag=cod, nom="Cartel SALIDA (IRAM 10005)")


def nave(e):
    L, A = NAVE["L"] * 1000, NAVE["A"] * 1000
    ha, hc = NAVE["h_alero"] * 1000, NAVE["h_cumbrera"] * 1000
    xs = [x * 1000 for x in NAVE["porticos"]]
    tag = "NAVE"
    e.en("Nave de proceso - estructura")
    # ------------------------------------------------------------------ platea, viga de fundación y zócalo
    e.caja(-200, -200, -150, L + 200, A + 200, 0, "hormigon_piso", tag, "Platea de H° H-25 de 15 cm con malla Q188")
    zocalo = 600
    puertas = {"S": [(28000, 32000), (19000, 20000)], "E": [(12400, 14900), (15000, 16200)], "O": [(2000, 3200)],
               "N": [(26200, 27200)]}
    for lado, (eje, pos, u1) in {"S": ("y", 0, L), "N": ("y", A, L), "O": ("x", 0, A), "E": ("x", L, A)}.items():
        huecos = [(a, b, 0, zocalo + 1) for a, b in puertas[lado]]
        for (a, b, za, zb) in _rectangulos_libres(0, u1, 0, zocalo, huecos):
            if eje == "y":
                e.caja(a, pos - 100, 0, b, pos + 100, zb, "revoque", tag, "Zócalo de mampostería revocada 0,60 m")
            else:
                e.caja(pos - 100, a, 0, pos + 100, b, zb, "revoque", tag, "Zócalo de mampostería revocada 0,60 m")
    # ------------------------------------------------------------------ pórticos: columnas IPN 300 y cerchas tubulares
    yc0, yc1 = 250.0, A - 250.0
    z_apoyo = ha - 175.0
    for i, x in enumerate(xs):
        xx = min(max(x, 100.0), L - 100.0)
        for yy in (yc0, yc1):
            C.columna(e, xx, yy, 0, z_apoyo - 100, "IPN 300", tag=f"P{i + 1}", placa=(420, 420, 22), d_anclaje=24,
                      rot=90)
            e.caja(xx - 120, yy - 160, z_apoyo - 100, xx + 120, yy + 160, z_apoyo - 80, "estructura", f"P{i + 1}",
                   "Placa de apoyo de la cercha")
            d = 1 if yy < A / 2 else -1
            e.barra((xx, yy, z_apoyo - 1700), (xx, yy + d * 1300, z_apoyo), "CHS 60", "estructura", cod=f"P{i + 1}",
                    nom="Pie de amigo CHS 60")
        _cercha(e, xx, yc0, yc1, z_apoyo, f"P{i + 1}")
    # vigas de borde (alero) y vigas de cumbrera entre pórticos
    for yy in (yc0, yc1):
        e.barra((100, yy, z_apoyo - 60), (L - 100, yy, z_apoyo - 60), "UPN 160", "estructura", up=(0, 0, 1), cod=tag,
                nom="Viga de borde UPN 160")
    # columnas de hastial (los huecos de cada testero mandan dónde van)
    hastial = {0.0: [4500.0, 9000.0, 13400.0], L: [3000.0, 7500.0, 12000.0, 16600.0]}
    for x, ys in hastial.items():
        xx = 100.0 if x == 0 else L - 100.0
        for yy in ys:
            ztop = _y_techo(yy) - 175 - 60
            C.columna(e, xx, yy, 0, ztop, "IPN 200", tag="HASTIAL", placa=(320, 320, 16), d_anclaje=20)
    # ------------------------------------------------------------------ correas de techo, arriostramientos y chapa
    ys_correa = [250.0 + 1200.0 * k for k in range(8)]
    ys_correa = ys_correa + [A - y for y in ys_correa]
    for yy in ys_correa:
        z = _y_techo(yy) - 70
        e.barra((-300, yy, z), (L + 300, yy, z), "C 120", "galv", up=(0, 0, 1), cod=tag, nom="Correa de techo C 120 galvanizada")
    for (xa, xb) in ((xs[0], xs[1]), (xs[-2], xs[-1])):
        for (ya, yb) in ((yc0, A / 2 - 400), (A / 2 + 400, yc1)):
            za, zb = _y_techo(ya) - 200, _y_techo(yb) - 200
            e.barra((xa + 100, ya, za), (xb - 100, yb, zb), "RB 16", "galv", cod=tag, nom="Cruz de techo Ø16 con tensor")
            e.barra((xa + 100, yb, zb), (xb - 100, ya, za), "RB 16", "galv", cod=tag, nom="Cruz de techo Ø16 con tensor")
    for (xa, xb, yy) in ((xs[0], xs[1], 0), (xs[4], xs[5], 0), (xs[0], xs[1], A), (xs[-2], xs[-1], A)):
        y_ = yc0 - 160 if yy == 0 else yc1 + 160
        e.barra((xa + 150, y_, 700), (xb - 150, y_, z_apoyo - 300), "RB 16", "galv", cod=tag, nom="Cruz de pared Ø16 con tensor")
        e.barra((xa + 150, y_, z_apoyo - 300), (xb - 150, y_, 700), "RB 16", "galv", cod=tag, nom="Cruz de pared Ø16 con tensor")
    e.en("Nave de proceso - cubierta")
    pend = math.atan2(hc - ha, A / 2)
    l_faldon = (A / 2 + 300) / math.cos(pend)
    for lado in (-1, 1):
        y_al = -300 if lado < 0 else A + 300
        G = T(-300, y_al, ha - (300 * math.tan(pend))) @ Rx(lado * -math.degrees(pend))
        bandas = [(0, L + 600)]
        for xc in (xs[0] + 2750, xs[2] + 2750, xs[4] + 2750):
            nuevo = []
            for a, b in bandas:
                if a < xc + 300 < b:
                    nuevo += [(a, xc + 300 - 550), (xc + 300 + 550, b)]
                else:
                    nuevo.append((a, b))
            bandas = nuevo
        for a, b in bandas:
            if lado < 0:
                e.caja(a, 0, 0, b, l_faldon, 30, "chapa_techo", M=G, cod=tag, nom="Chapa trapezoidal T-101 galvanizada 0,5 mm")
            else:
                e.caja(a, -l_faldon, 0, b, 0, 30, "chapa_techo", M=G, cod=tag, nom="Chapa trapezoidal T-101 galvanizada 0,5 mm")
        for xc in (xs[0] + 2750, xs[2] + 2750, xs[4] + 2750):
            a, b = xc + 300 - 550, xc + 300 + 550
            if lado < 0:
                e.caja(a, 0, 0, b, l_faldon, 25, "policarbonato", M=G, cod=tag, nom="Lucernario de policarbonato alveolar 10 mm")
            else:
                e.caja(a, -l_faldon, 0, b, 0, 25, "policarbonato", M=G, cod=tag, nom="Lucernario de policarbonato alveolar 10 mm")
    e.barra((-300, A / 2, hc + 40), (L + 300, A / 2, hc + 40), "L 80", "galv", up=(0, 0, 1), cod=tag, nom="Cumbrera de chapa plegada")
    for k in range(6):
        xc = 2750 + 5500 * k
        e.tubo((xc, A / 2, hc - 40), (xc, A / 2, hc + 250), 300, 296, "galv", cod="EOL", nom="Extractor eólico Ø600 (base)")
        e.esfera((xc, A / 2, hc + 470), 320, "aluminio", cod="EOL", nom="Extractor eólico Ø600 (turbina)")
    # canaletas y bajadas
    for yy, d in ((-300, -1), (A + 300, 1)):
        e.caja(-300, yy - (200 if d > 0 else 0) * 0 - (0 if d > 0 else 200), ha - 260, L + 300,
               yy + (200 if d > 0 else 0), ha - 60, "galv", tag, "Canaleta de chapa galvanizada 200 × 200")
        for x in (0.0, 11000.0, 22000.0, L):
            xb = min(max(x, 200.0), L - 200.0)
            yb = yy + d * 100
            e.tubo((xb, yb, 150), (xb, yb, ha - 260), 55, 52, "galv", cod=tag, nom="Bajada pluvial Ø110")
            e.caja(xb - 200, yb - 200, -100, xb + 200, yb + 200, 0, "hormigon", tag, "Cámara pluvial")
    # ------------------------------------------------------------------ cerramientos con aberturas
    e.en("Nave de proceso - cerramientos")
    ventanas_s = [(2750 + 5500 * k - 1250, 2750 + 5500 * k + 1250, 5000, 6000) for k in range(6)]
    huecos = {
        "S": [(28000, 32000, 0, 4500), (19000, 20000, 0, 2100)] + ventanas_s,
        "N": [(26200, 27200, 0, 2100), (14000, 15000, 6050, 6950), (21800, 23200, 3100, 3900), (850, 1550, 6100, 6800)]
             + [v for v in ventanas_s if not (12500 <= v[0] <= 15000)],
        "O": [(2000, 3200, 0, 2100), (13600, 16400, 4250, 6300), (5200, 8200, 5000, 6000)],
        "E": [(12400, 14900, 0, 3500), (15000, 16200, 0, 2100), (13600, 16400, 3700, 5600), (3950, 5250, 4250, 5550),
              (9250, 10550, 4250, 5550)],
    }
    zg = [1800.0, 3200.0, 4600.0, 6000.0]
    _pared(e, "y", 0, 0, L, zocalo, ha, huecos["S"], -1, "Chapa trapezoidal de pared T-101 0,5 mm")
    _pared(e, "y", A, 0, L, zocalo, ha, huecos["N"], 1, "Chapa trapezoidal de pared T-101 0,5 mm")
    for (x, lado, cara) in ((0.0, "O", -1), (L, "E", 1)):
        _pared(e, "x", x, 0, A, zocalo, ha, huecos[lado], cara, "Chapa trapezoidal de pared T-101 0,5 mm")
        # triángulo del hastial
        k = proto(("hastial", round(A), round(hc - ha)), lambda: wp().polyline([(0, 0), (A, 0), (A / 2, hc - ha)]).close().extrude(30))
        e.add(k, "chapa_trap", T(x + (0 if cara > 0 else -30), 0, ha) @ Rz(90) @ Rx(90), tag, "Chapa del hastial")
    e.en("Nave de proceso - estructura")
    _correas_pared(e, "y", yc0 - 200, 300, L - 300, zg, [(a, b, z0, z1) for a, b, z0, z1 in huecos["S"]], tag)
    _correas_pared(e, "y", yc1 + 200, 300, L - 300, zg, [(a, b, z0, z1) for a, b, z0, z1 in huecos["N"]], tag)
    _correas_pared(e, "x", 230, 300, A - 300, zg, huecos["O"], tag)
    _correas_pared(e, "x", L - 230, 300, A - 300, zg, huecos["E"], tag)
    # ------------------------------------------------------------------ portones, puertas y ventanas
    e.en("Nave de proceso - aberturas")
    _porton(e, "y", 0, 28000, 32000, 4500, -1, "P2", "Portón seccional P2 4,0 × 4,5 m (despacho)")
    _porton(e, "x", L, 12400, 14900, 3500, 1, "P3", "Portón seccional P3 2,5 × 3,5 m (palets a expedición)")
    _puerta(e, "y", 0, 19000, 20000, 2100, -1, "PP1", "Puerta de acceso del personal PP1")
    _puerta(e, "x", L, 15000, 16200, 2100, 1, "SE1", "Salida de emergencia SE1")
    _puerta(e, "x", 0, 2000, 3200, 2100, -1, "SE2", "Salida de emergencia SE2")
    _puerta(e, "y", A, 26200, 27200, 2100, 1, "PC1", "Puerta cortafuego RF-60 PC1 al anexo", mat="rojo")
    for (a, b, z0, z1) in ventanas_s:
        _ventana(e, "y", 0, a, b, z0, z1, -1)
    for (a, b, z0, z1) in huecos["N"][4:]:
        _ventana(e, "y", A, a, b, z0, z1, 1)
    _ventana(e, "x", 0, 5200, 8200, 5000, 6000, -1)
    # pasos de las cintas principales: marco con cortina de tiras de PVC
    for (x, a, b, z0, z1) in ((0.0, 13600, 16400, 4250, 6300), (L, 13600, 16400, 3700, 5600)):
        for zz in np.arange(z0 + 50, z1, 120):
            pass
        e.caja(x - 15, a, z1 - 80, x + 15, b, z1, "estructura", "PASO-CP", "Marco del paso de la cinta principal")
        for yy in np.arange(a + 60, b - 40, 140):
            e.caja(x - 3, yy, z0 + 100, x + 3, yy + 120, z1 - 80, "policarbonato", "PASO-CP", "Cortina de tiras de PVC")
    # ------------------------------------------------------------------ iluminación
    e.en("Nave de proceso - iluminación")
    for k in range(6):
        for yy in (4500.0, 13500.0):
            xc = 2750 + 5500 * k
            zt = _y_techo(yy) - 140
            e.barra((xc, yy, zt), (xc, yy, 6350), "RB 6", "galv", cod="IL", nom="Cadena de suspensión")
            e.cono((xc, yy, 6350), (xc, yy, 6050), 120, 230, "aluminio", cod="IL", nom="Campana LED 150 W IP65 (300 lx)")
            e.cil((xc, yy, 6050), (xc, yy, 6030), 225, "luz", cod="IL", nom="")


def _cercha(e, x, y0, y1, z_apoyo, tag):
    """Cercha triangular de caños: cordones CHS 89, montantes y diagonales CHS 48 (tipo Pratt)."""
    A = NAVE["A"] * 1000
    zc = lambda y: _y_techo(y) - 175               # noqa: E731  eje del cordón superior
    ym = A / 2
    e.barra((x, y0, z_apoyo), (x, ym, zc(ym)), "CHS 89", "estructura", cod=tag, nom="Cordón superior CHS 88,9 × 3,2")
    e.barra((x, ym, zc(ym)), (x, y1, z_apoyo), "CHS 89", "estructura", cod=tag, nom="Cordón superior CHS 88,9 × 3,2")
    e.barra((x, y0, z_apoyo), (x, y1, z_apoyo), "CHS 89", "estructura", cod=tag, nom="Cordón inferior CHS 88,9 × 3,2")
    paneles = [y0 + (ym - y0) * k / 6 for k in range(7)]
    paneles = paneles + [A - y for y in reversed(paneles[:-1])]
    for i, y in enumerate(paneles):
        if 0 < i < len(paneles) - 1:
            e.barra((x, y, z_apoyo), (x, y, zc(y)), "CHS 48", "estructura", cod=tag, nom="Montante CHS 48,3 × 2,6")
        if i < len(paneles) - 1:
            yb = paneles[i + 1]
            if yb <= ym:
                e.barra((x, y, zc(y)), (x, yb, z_apoyo), "CHS 48", "estructura", cod=tag, nom="Diagonal CHS 48,3 × 2,6")
            else:
                e.barra((x, y, z_apoyo), (x, yb, zc(yb)), "CHS 48", "estructura", cod=tag, nom="Diagonal CHS 48,3 × 2,6")


# ===================================================================================== piloto a GLP
def piloto_glp(e):
    """Tanque de GLP de 0,5 m³ con regulador y línea al quemador piloto del hogar (reemplaza al biogás)."""
    e.en("Planta - generador de aire caliente")
    s = next(x for x in D["servicios"] if x["id"] == "GLP")
    x, y = s["x"] * 1000, s["y"] * 1000
    Lt, Dt = s["L"] * 1000, s["D"] * 1000
    e.cil((x - Lt / 2, y, 800), (x + Lt / 2, y, 800), Dt / 2, "plastico_blanco", cod="GLP", nom="Tanque de GLP 0,5 m³ (ENARGAS NAG-112)")
    for xx in (x - Lt / 2, x + Lt / 2):
        e.esfera((xx, y, 800), Dt / 2, "plastico_blanco", cod="GLP", nom="")
    for xx in (x - Lt / 3, x + Lt / 3):
        e.caja(xx - 100, y - 350, 0, xx + 100, y + 350, 350, "hormigon", "GLP", "Cuna de H°")
    e.caja(x - 150, y - 150, 800 + Dt / 2, x + 150, y + 150, 800 + Dt / 2 + 220, "galv", "GLP", "Domo con válvulas y regulador de 1ª etapa")
    C.placa(e, (x, y - Dt / 2 - 10, 900), (0, -1, 0), 500, 250, "rojo", tag="GLP", nom="GLP · PELIGRO INFLAMABLE · NO FUMAR")
    xh, yh = 28400.0, 21300.0
    pts = [(x - 150, y, 800 + Dt / 2 + 220), (x - 150, y, 1300), (x - 150, 24500, 1300), (xh + 800, 24500, 1300),
           (xh + 800, yh, 1300), (xh, yh, 1300)]
    e.polilinea(pts, 14, "amarillo", cod="GLP", nom="Cañería de GLP de acero 3/4\" pintada amarilla")
    e.caja(xh + 400, yh - 200, 1100, xh + 700, yh + 200, 1500, "gris_motor", "GLP",
           "Tren de válvulas del piloto: regulador de 2ª etapa, 2 electroválvulas y presostato")
    for (px, py) in ((x - 150, 26000), (x - 150, 24500), (xh + 2500, 24500), (xh + 800, 23000)):
        e.barra((px, py, 0), (px, py, 1280), "RHS 40", "estructura", cod="GLP", nom="Soporte de la cañería")
    # cerco del tanque
    for (a, b) in (((x - 1800, y - 1300), (x + 1800, y - 1300)), ((x + 1800, y - 1300), (x + 1800, y + 1300)),
                   ((x + 1800, y + 1300), (x - 1800, y + 1300)), ((x - 1800, y + 1300), (x - 1800, y - 1300))):
        e.caja(min(a[0], b[0]) - 20, min(a[1], b[1]) - 20, 0, max(a[0], b[0]) + 20, max(a[1], b[1]) + 20, 1800,
               "malla", "GLP", "Cerco de malla del tanque de GLP")


# ===================================================================================== aspiración de la tolva pulmón
def aspiracion_tp01(e):
    """Ducto Ø600 desde la tapa de la TP-01 hasta la bajada existente al extractor M23 y al biofiltro."""
    e.en("Planta - tratamiento de aire")
    pts = [(1200, 15900, 6000), (1200, 15900, 6450), (1200, 18900, 6450), (5000, 18900, 6450)]
    e.polilinea(pts, 300, "galv", cod="E3", nom="Ducto de aspiración de la TP-01 Ø600 (reemplaza a la campana de la Rev. F)")
    for p in pts[1:]:
        e.esfera(p, 300, "galv", cod="E3", nom="Codo")
    for yy in (16900.0, 17700.0):
        e.barra((1200, yy, 6750), (1200, yy, 7000), "L 50", "estructura", cod="E3", nom="Colgador del ducto")


def construir(e, informe=None):
    nave(e)
    importar_revF(e, informe)
    secador_sc4(e)
    piloto_glp(e)
    aspiracion_tp01(e)
