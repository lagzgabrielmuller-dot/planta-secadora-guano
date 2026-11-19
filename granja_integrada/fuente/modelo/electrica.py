"""Instalación eléctrica nueva de la granja integrada en 3D (Fase 7 de la consigna).

Agrega lo que la Rev. F no tenía: el tablero TS-GU con el PLC-01 en la sala de control, la bandeja troncal que cruza la
nave hasta la recepción, la periferia RIO-TP con su pantalla, las bandejas y caños de la tolva pulmón, de los cabezales
de las cintas principales y de las torres, el CCM del transporte de guano de cada galpón con sus bandejas y caños hasta
cada motor, los seccionadores de seguridad, las botoneras de fila, la puesta a tierra y los pararrayos de las torres.

Las rutas se definen una sola vez, en metros, en `red()`: el 3D las dibuja y `electrica_granja.py` mide con ellas el
largo de cada cable, así lo que se ve y lo que se calcula es lo mismo.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import componentes as C
import galpon as GP
import planta as PL
from cad import T, Rz

RAIZ = Path(__file__).resolve().parents[2]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
TR = {t["id"]: t for t in D["transporte"]}
TT = {t["lado"]: t for t in D["torres"]}
NAVE = D["planta"]["nave"]

# ===================================================================================== tableros (m)
TS_GU = {"x": 25.65, "y": 3.10, "rotz": -90.0, "ancho": 1.2, "alto": 2.0, "prof": 0.4}   # muro Este de la sala de control
TG2 = (23.60, 0.27)                    # TG2 de la Rev. F (muro Sur de la sala de control)
TGF = (24.80, 0.45)                    # TGF de la Rev. F
RIO_TP = {"x": 7.00, "y": 14.20, "rotz": 90.0, "ancho": 0.8, "alto": 1.2, "prof": 0.3, "zocalo": 0.3}
TGBT = (-7.40, -74.40)                 # tablero general de baja tensión en la subestación (sitio.py)
Z_TRONCAL = 5.60                       # cota de la troncal de la nave: sobre las bandejas de la Rev. F (+4,96 y +5,36)
Z_TORRE = 7.40                         # bandeja de las torres: 2,6 m libres sobre la plataforma, bajo las vigas de techo
Z_CABECERA = 3.45                      # bandeja de la cabecera de guano de los galpones (sobre la protección de transmisiones)
Z_SUBT = -0.70                         # caños enterrados


def _galpon_geo(g):
    """Medidas de la cabecera de guano de un galpón, en m."""
    sig = g["hacia_planta"]
    x_w = g["x1"] if sig > 0 else g["x0"]                       # muro del lado de la planta (donde sale la CI)
    x_o = g["x0"] if sig > 0 else g["x1"]
    yc0 = g["y0"] + GP.CAB_G / 1000
    filas = [x / 1000 for x in GP.x_filas(g["x"] * 1000)]
    dep = next(d for d in D["depositos"] if g["id"] in d["galpones"])
    lado_dep = 1 if (dep["x0"] + dep["x1"]) / 2 > g["x"] else -1
    xs0, xs1 = sorted((g["x"] - lado_dep * 1.0, g["x"] - lado_dep * 5.25))
    k = g["id"][1]
    ct, ci = TR[f"CT-{k}"], TR[f"CI-{k}"]
    return {"sig": sig, "x_w": x_w, "x_o": x_o, "y_bt": g["y0"] + 1.5, "yc0": yc0, "filas": filas,
            "ccm": (x_w + sig * 0.37, g["y0"] + 1.5), "ts": ((xs0 + xs1) / 2 - 0.6, g["y1"] + 2.8),
            "x_ci": ci["p0"][0], "x_ct_cab": ct["p1"][0], "y_ct": ct["p0"][1], "x_t": ci["p0"][0] + sig * 0.80}


def _z_ci(ci, y):
    """Cota de la banda de la CI (tramo inclinado) en la ordenada y."""
    (x0, y0, z0), (x1, y1, z1) = ci["trazado"][1], ci["trazado"][2]
    return z0 + (y0 - y) / (y0 - y1) * (z1 - z0)


def _torre_geo(lado):
    t = TT[lado]
    sig = 1 if lado == "O" else -1
    x0, x1 = t["x"] - t["A"] / 2, t["x"] + t["A"] / 2
    y0, y1 = t["y"] - t["B"] / 2, t["y"] + t["B"] / 2
    x_ce, x_cp = (x0, x1) if sig > 0 else (x1, x0)
    return {"sig": sig, "x0": x0, "x1": x1, "y0": y0, "y1": y1, "x_ce": x_ce, "x_cp": x_cp,
            "rio": (x_cp - sig * 0.17, y0 + 0.50), "rio_rotz": -90.0 * sig}


# ===================================================================================== red de canalizaciones
def red():
    """Todas las canalizaciones como polilíneas en m: (nombre, tipo, puntos, red).

    tipo: 'bandeja' (nueva, se dibuja), 'existente' (bandeja que ya dibuja transporte.py), 'caño' (nuevo, se dibuja),
    'subterraneo' (caño enterrado: solo se dibujan las cámaras). red: 'planta', 'G1'…'G4' o 'acometida'.
    """
    R = []
    # ---------------------------------------------------------------- planta: TG2 → TS-GU y troncal de la nave
    xg, yg = TS_GU["x"], TS_GU["y"]
    R.append(("Bandeja de la sala de control TG2 → TS-GU", "bandeja",
              [(TG2[0], 0.30, 2.00), (TG2[0], 0.30, 2.80), (xg, 0.30, 2.80), (xg, yg, 2.80), (xg, yg, 2.20)], "planta"))
    R.append(("Troncal TS-GU → recepción (pasa sobre la sala de control y cruza la nave)", "bandeja",
              [(xg, yg, 2.20), (xg, yg, Z_TRONCAL), (6.80, yg, Z_TRONCAL), (6.80, 13.20, Z_TRONCAL),
               (6.80, 13.98, 4.97)], "planta"))
    # bandejas que ya dibuja transporte.py (medidas del modelo)
    R.append(("Bandeja interior de la CP-E (colgada de las cerchas)", "existente",
              [(33.00, 13.98, 4.28), (6.80, 13.98, 4.97), (5.04, 13.98, 4.98)], "planta"))
    R.append(("Bandeja de la galería de la CP-E", "existente", [(33.14, 16.40, 4.15), (41.35, 16.40, 3.95)], "planta"))
    R.append(("Bandeja de la galería de la CP-O", "existente", [(-0.10, 16.40, 4.72), (-8.32, 16.40, 4.06)], "planta"))
    R.append(("Bandeja de la galería de la CE-O", "existente", [(-11.64, 12.80, 5.65), (-63.70, 12.80, 5.65)], "planta"))
    R.append(("Bandeja de la galería de la CE-E", "existente", [(44.64, 12.80, 5.65), (96.70, 12.80, 5.65)], "planta"))
    # pórtico de cabezales PC-01: motores M82 y M84 y cruce del muro Oeste hasta la galería de la CP-O
    R.append(("Bandeja del pórtico de cabezales PC-01", "bandeja",
              [(5.04, 13.98, 4.98), (5.04, 13.50, 4.85), (0.90, 13.50, 4.85)], "planta"))
    R.append(("Caño de cruce del muro Oeste a la galería de la CP-O", "caño",
              [(0.90, 13.50, 4.85), (-0.40, 13.50, 4.85), (-0.40, 13.50, 4.20), (-0.40, 16.40, 4.20),
               (-0.40, 16.40, 4.68), (-0.10, 16.40, 4.72)], "planta"))
    R.append(("Caño de cruce del muro Este a la galería de la CP-E", "caño",
              [(33.00, 13.98, 4.28), (33.40, 13.98, 4.28), (33.40, 13.98, 3.55), (33.40, 16.40, 3.55),
               (33.40, 16.40, 4.10), (33.14, 16.40, 4.15)], "planta"))
    # periferia RIO-TP y bandeja de piso de la tolva pulmón
    xr, yr = RIO_TP["x"], RIO_TP["y"]
    z_rio = RIO_TP["zocalo"] + RIO_TP["alto"]
    R.append(("Bajada de la CP-E al RIO-TP", "bandeja", [(xr, 13.98, 4.95), (xr, 13.98, z_rio + 0.25),
                                                        (xr - 0.05, yr, z_rio + 0.25), (xr - 0.05, yr, z_rio)], "planta"))
    R.append(("Bandeja de piso de la tolva pulmón (motores de los sinfines)", "bandeja",
              [(xr - 0.05, yr, z_rio + 0.25), (5.45, yr, 2.30), (5.45, 17.35, 2.30), (0.75, 17.35, 2.30)], "planta"))
    R.append(("Caño de los sensores del extremo Sur de los sinfines (por la columna del PC-01)", "caño",
              [(3.62, 13.50, 4.85), (3.62, 13.50, 5.60), (3.62, 9.95, 5.60), (3.62, 9.95, 1.75), (3.62, 8.80, 1.75),
               (0.80, 8.80, 1.75)], "planta"))
    R.append(("Caño de los sensores del extremo Sur (rama Este)", "caño", [(3.62, 8.80, 1.75), (4.75, 8.80, 1.75)], "planta"))
    # torres: bandeja perimetral a +7,40 con subidas desde las galerías
    for lado in ("O", "E"):
        g = _torre_geo(lado)
        s = g["sig"]
        x_cpt = -8.32 if lado == "O" else 41.35
        z_cpt = 4.06 if lado == "O" else 3.95
        x_cet = -11.64 if lado == "O" else 44.64
        R.append((f"Bandeja de la torre TT-{lado}", "bandeja",
                  [(x_cpt, 16.40, z_cpt), (x_cpt, 16.40, Z_TORRE), (g["x_cp"] - s * 0.15, g["y1"] - 0.15, Z_TORRE),
                   (g["x_cp"] - s * 0.15, g["y0"] + 0.15, Z_TORRE), (g["x_ce"] + s * 0.15, g["y0"] + 0.15, Z_TORRE),
                   (x_cet, 12.80, Z_TORRE), (x_cet, 12.80, 5.65)], "planta"))
        xr_, yr_ = g["rio"]
        R.append((f"Bajada al RIO-{lado}", "bandeja", [(g["x_cp"] - s * 0.15, yr_, Z_TORRE),
                                                    (g["x_cp"] - s * 0.15, yr_, 4.80 + 1.10)], "planta"))
    # ---------------------------------------------------------------- galpones: CCM, cabecera, CT y CI
    for gal in D["galpones"]:
        gid = gal["id"]
        k = gid[1]
        q = _galpon_geo(gal)
        s, x_w, x_o, y_bt = q["sig"], q["x_w"], q["x_o"], q["y_bt"]
        xc, yc = q["ccm"]
        ci = TR[f"CI-{k}"]
        R.append((f"Bandeja de la cabecera de guano del {gid}", "bandeja",
                  [(xc, yc, 2.00), (xc, yc, 2.20), (x_w - s * 0.30, y_bt, 2.20), (x_w - s * 0.30, y_bt, Z_CABECERA),
                   (x_o + s * 0.30, y_bt, Z_CABECERA)], gid))
        for f, xf in enumerate(q["filas"]):
            for lado_f, nom in ((1, "motores"), (-1, "sensores")):
                xv = xf + lado_f * 1.01
                R.append((f"Caño de los {nom} de la fila {'ABCD'[f]} del {gid}", "caño",
                          [(xv, y_bt, Z_CABECERA), (xv, q["yc0"] - 0.70, Z_CABECERA),
                           (xv, q["yc0"] - 0.70, GP.z_piso(0) / 1000 - 0.05)], gid))
        # CT: baja por el muro del lado de la planta y entra al canal
        x_b = x_w - s * 0.30
        x_m = q["x_ct_cab"]
        R.append((f"Caño de la cinta transversal CT-{k}", "caño",
                  [(x_b, y_bt, Z_CABECERA), (x_w - s * 0.12, y_bt + 0.20, Z_CABECERA), (x_w - s * 0.12, y_bt + 0.20, 0.12),
                   (x_m + s * 0.05, y_bt + 0.20, 0.12), (x_m + s * 0.05, y_bt + 0.20, -0.20)], gid))
        # CI: bandeja sobre las patas del tramo inclinado, caño enterrado hasta el CCM
        xt = q["x_t"]
        ya, yb = 21.30, 15.55
        R.append((f"Bandeja de la cinta inclinada CI-{k}", "bandeja",
                  [(xt, ya, _z_ci(ci, ya) + 0.20), (xt, yb, _z_ci(ci, yb) + 0.20)], gid))
        R.append((f"Caño enterrado CCM-{gid} → pie de la CI-{k}", "subterraneo",
                  [(xc, yc, 0.20), (xc, yc, Z_SUBT), (xc, ya, Z_SUBT), (xt, ya, Z_SUBT), (xt, ya, _z_ci(ci, ya) + 0.20)], gid))
        # alimentación del CCM desde el TS del galpón (enterrada por el lado de la planta)
        xts, yts = q["ts"]
        xe = x_w + s * 1.20
        R.append((f"Alimentador TS-{gid} → CCM-{gid} (enterrado)", "subterraneo",
                  [(xts, yts, 0.0), (xts, yts, Z_SUBT), (xts, gal["y1"] + 1.5, Z_SUBT), (xe, gal["y1"] + 1.5, Z_SUBT),
                   (xe, yc, Z_SUBT), (xc, yc, Z_SUBT), (xc, yc, 0.20)], f"{gid}-alim"))
        # fibra óptica: de la galería de la colectora a la bandeja de la CI (cruce bajo el piso de la galería)
        R.append((f"Caño de cruce de la galería de la CE a la CI-{k} (fibra óptica)", "caño",
                  [(xt, 12.80, 5.65), (xt, 12.80, 5.15), (xt, yb, 5.15), (xt, yb, _z_ci(ci, yb) + 0.20)], "fibra"))
    # ---------------------------------------------------------------- acometida: TGBT → TG2 y TGF (enterrados)
    R.append(("Alimentador TGBT → TG2 (enterrado)", "subterraneo",
              [(TGBT[0], TGBT[1], 0.0), (TGBT[0], TGBT[1], Z_SUBT - 0.1), (TGBT[0], -10.0, Z_SUBT - 0.1),
               (22.0, -10.0, Z_SUBT - 0.1), (22.0, -1.0, Z_SUBT - 0.1), (TG2[0], -1.0, Z_SUBT - 0.1),
               (TG2[0], TG2[1], Z_SUBT - 0.1), (TG2[0], TG2[1], 0.0)], "acometida"))
    R.append(("Alimentador TGBT → TGF (enterrado)", "subterraneo",
              [(TGBT[0], TGBT[1], 0.0), (TGBT[0], TGBT[1], Z_SUBT - 0.1), (TGBT[0], -10.0, Z_SUBT - 0.1),
               (22.0, -10.0, Z_SUBT - 0.1), (22.0, -1.0, Z_SUBT - 0.1), (TGF[0], -1.0, Z_SUBT - 0.1),
               (TGF[0], TGF[1], Z_SUBT - 0.1), (TGF[0], TGF[1], 0.0)], "acometida"))
    return R


# ===================================================================================== dibujo
def _mm(p):
    return tuple(v * 1000 for v in p)


def _bandeja(e, pts, ancho, tag, cables=3, colgar=None):
    for a, b in zip(pts, pts[1:]):
        if math.dist(a, b) < 0.06:
            continue
        C.bandeja(e, _mm(a), _mm(b), ancho, tag=tag)
        C.cables_en_bandeja(e, _mm(a), _mm(b), cables, ancho, tag=tag)
        if colgar and abs(a[2] - b[2]) < 0.05:
            _colgadores(e, a, b, colgar, tag)


def _colgadores(e, a, b, z_arriba, tag, paso=1.6):
    """Varillas roscadas M12 con perfil soporte cada `paso` m hasta la estructura de arriba (z_arriba(x, y) en m)."""
    a, b = np.array(a), np.array(b)
    L = np.linalg.norm(b - a)
    n = max(1, int(L // paso))
    u = (b - a) / L
    v = np.array([-u[1], u[0], 0.0])
    for i in range(n + 1):
        p = a + u * min(L, 0.3 + i * (L - 0.6) / max(1, n))
        zt = z_arriba(p[0], p[1])
        if zt - p[2] < 0.15:
            continue
        for sgn in (-1, 1):
            q = p + v * sgn * 0.22
            e.barra(_mm((q[0], q[1], p[2] - 0.03)), _mm((q[0], q[1], zt)), "RB 12", "galv", cod=tag, nom="Varilla roscada M12")
        e.barra(_mm(p - v * 0.24 + (0, 0, -0.03)), _mm(p + v * 0.24 + (0, 0, -0.03)), "C 80", "galv", up=(0, 0, 1),
                cod=tag, nom="Perfil soporte de bandeja")


def _cano(e, pts, d, tag):
    C.cano(e, [_mm(p) for p in pts], d, tag=tag)


def _pantalla(e, c, n, ancho, alto, tag, nom):
    """Panel de operador (HMI) embutido en la puerta de un tablero."""
    n = np.array(n, float) / np.linalg.norm(n)
    rz = math.degrees(math.atan2(n[1], n[0])) - 90
    c = np.array(c)
    e.caja_rot(tuple(_mm(c + n * 0.012)), (ancho * 1000, 24, alto * 1000), rz, "negro", tag, nom)
    e.caja_rot(tuple(_mm(c + n * 0.026)), (ancho * 1000 - 50, 4, alto * 1000 - 50), rz, "vidrio", tag, "")


def _camara(e, x, y, tag, nom="Cámara de paso 40 × 40 cm"):
    e.caja((x - 0.24) * 1000, (y - 0.24) * 1000, -500, (x + 0.24) * 1000, (y + 0.24) * 1000, 30, "hormigon", tag, nom)
    e.caja((x - 0.2) * 1000, (y - 0.2) * 1000, 30, (x + 0.2) * 1000, (y + 0.2) * 1000, 50, "acero_pintado", tag, "Tapa de chapa")


def _jabalina(e, x, y, tag):
    _camara(e, x, y, tag, "Cámara de inspección de la puesta a tierra")
    e.cil(((x) * 1000, y * 1000, -3000), (x * 1000, y * 1000, 60), 9, "cobre", cod=tag, nom="Jabalina Cu-acero Ø3/4\" × 3 m")


def construir(e):
    zt = lambda x, y: PL._y_techo(y * 1000) / 1000 - 0.20       # noqa: E731  bajo las correas de la nave
    # ---------------------------------------------------------------- sala de control
    e.en("Instalación eléctrica - tableros y PLC")
    g = TS_GU
    C.tablero(e, g["x"] * 1000, g["y"] * 1000, 0, g["ancho"] * 1000, g["alto"] * 1000 - 100, g["prof"] * 1000,
              rotz=g["rotz"], tag="TS-GU",
              nombre="Tablero TS-GU del transporte de guano: 8 variadores G120, PLC-01 S7-1500F, UPS 1 kVA y switch")
    _pantalla(e, (g["x"] - g["prof"] / 2 - 0.02, g["y"] - 0.25, 1.55), (-1, 0, 0), 0.33, 0.24, "TS-GU",
              "Panel de operador TP1200 Comfort (supervisión de la planta)")
    # ---------------------------------------------------------------- canalizaciones de la red
    ruta = {n: (t, p, r) for n, t, p, r in red()}
    e.en("Instalación eléctrica - canalizaciones")
    for nom, (tipo, pts, r) in ruta.items():
        if tipo == "bandeja":
            if "sala de control" in nom:
                _bandeja(e, pts, 200, "BT-SC", cables=4, colgar=lambda x, y: 3.0)
            elif nom.startswith("Troncal"):
                _bandeja(e, pts, 300, "BT-01", cables=6, colgar=zt)
            elif "PC-01" in nom:
                _bandeja(e, pts, 200, "BT-PC01", cables=3, colgar=lambda x, y: 6.17)
            elif "tolva pulmón" in nom or "RIO-TP" in nom:
                _bandeja(e, pts, 200, "BT-TP", cables=4)
            elif "torre" in nom or nom.startswith("Bajada al RIO"):
                lado = "O" if ("TT-O" in nom or "RIO-O" in nom) else "E"
                _bandeja(e, pts, 200, f"BT-TT-{lado}", cables=4, colgar=lambda x, y: 8.02)
            elif "cabecera" in nom:
                gid = nom.split()[-1]
                gal = next(x for x in D["galpones"] if x["id"] == gid)
                eje = gal["x"]
                z_g = lambda x, y, eje=eje: (GP.HA + (GP.A / 2 - abs(x * 1000 - eje * 1000)) * math.tan(GP.PEND)) / 1000 - 0.16  # noqa: E731
                _bandeja(e, pts[3:], 200, f"BT-{gid}", cables=5, colgar=z_g)
                _bandeja(e, pts[:4], 200, f"BT-{gid}", cables=5)
            elif "inclinada" in nom:
                _bandeja(e, pts, 150, nom.split()[-1].replace("CI-", "BT-CI-"), cables=2)
        elif tipo == "caño":
            d = 32 if "fibra" in nom else (50 if "cruce del muro" in nom else 25)
            tag = "FO" if "fibra" in nom else ("CT" if "transversal" in nom else "CÑ")
            _cano(e, pts, d, tag)
    # ---------------------------------------------------------------- recepción: RIO-TP, sinfines y cabezales
    e.en("Instalación eléctrica - tableros y PLC")
    r = RIO_TP
    C.tablero(e, r["x"] * 1000, r["y"] * 1000, 0, r["ancho"] * 1000, r["alto"] * 1000, r["prof"] * 1000, rotz=r["rotz"],
              tag="RIO-TP", nombre="Tablero de periferia RIO-TP (ET 200SP con F-DI y SIWAREX WP231)", zocalo=r["zocalo"] * 1000)
    _pantalla(e, (r["x"] + r["prof"] / 2 + 0.02, r["y"], r["zocalo"] + 0.85), (1, 0, 0), 0.20, 0.15, "RIO-TP",
              "Panel de operador KTP700 de la recepción")
    C.columna(e, (r["x"] - 0.25) * 1000, (r["y"] - 0.20) * 1000, 0, 4900, "RHS 80", tag="RIO-TP", placa=(200, 200, 12),
              d_anclaje=12, dado=False)
    e.en("Instalación eléctrica - canalizaciones")
    for y in np.arange(9.4, 17.4, 1.5):                        # ménsulas de la bandeja de piso de la tolva
        e.barra((5000, y * 1000, 2250), (5650, y * 1000, 2250), "L 40", "galv", cod="BT-TP", nom="Ménsula de bandeja L 40")
    for x in np.arange(1.0, 5.6, 1.5):
        e.barra((x * 1000, 17800, 2250), (x * 1000, 17150, 2250), "L 40", "galv", cod="BT-TP", nom="Ménsula de bandeja L 40")
    e.en("Instalación eléctrica - seccionadores y botoneras")
    # estación de bloqueo de los 4 sinfines en el lado Este de la tolva
    e.caja(5150, 15050, 700, 5170, 16650, 1500, "galv", "LOTO-TP", "Placa de la estación de bloqueo de los sinfines")
    for i, yy in enumerate((15.25, 15.65, 16.05, 16.45)):
        C.seccionador(e, (5170, yy * 1000, 1100), (1, 0, 0), tag=f"Q-M{85 + i}")
    _cano(e, [(5.45, 15.25, 2.30), (5.25, 15.25, 2.30), (5.25, 15.25, 1.55)], 32, "CÑ")
    xs_m = [1.15 + 1.10 * i for i in range(4)]
    for xm in xs_m:
        _cano(e, [(xm, 17.35, 2.30), (xm, 17.35, 1.80), (xm, 16.95, 1.80), (xm, 16.95, 1.62)], 25, "CÑ")
    # cabezales de las principales: seccionadores en las columnas Norte del PC-01
    for xx, tag, xm in ((1.75, "Q-M82", 2.02), (3.75, "Q-M84", 4.19)):
        C.seccionador(e, (xx * 1000, 16550, 5850), (0, -1, 0), tag=tag)
        _cano(e, [(xm, 13.50, 4.85), (xm, 13.50, 5.05), (xm, 13.85, 5.05)], 25, "CÑ")
    # ---------------------------------------------------------------- torres
    for lado in ("O", "E"):
        t = _torre_geo(lado)
        s = t["sig"]
        tag = f"TT-{lado}"
        m_ce, m_dv = ("M81", "M89") if lado == "O" else ("M83", "M90")
        x_mce = -10.90 if lado == "O" else 43.90
        x_mdv = -9.68 if lado == "O" else 42.68
        e.en("Instalación eléctrica - canalizaciones")
        _cano(e, [(x_mce, t["y0"] + 0.15, Z_TORRE), (x_mce, 15.00, Z_TORRE), (x_mce, 15.00, 6.30)], 25, "CÑ")
        _cano(e, [(x_mdv, t["y0"] + 0.15, Z_TORRE), (x_mdv, 14.30, Z_TORRE), (x_mdv, 14.30, 5.70)], 25, "CÑ")
        e.en("Instalación eléctrica - seccionadores y botoneras")
        C.seccionador(e, ((t["x_ce"] + s * 0.12) * 1000, (t["y1"] - 0.15) * 1000, 6000), (s, -1, 0), tag=f"Q-{m_ce}")
        C.seccionador(e, ((t["x_cp"] - s * 1.20) * 1000, (t["y0"] + 0.10) * 1000, 5700), (0, 1, 0), tag=f"Q-{m_dv}")
        # puesta a tierra, barra equipotencial y pararrayos
        e.en("Instalación eléctrica - puesta a tierra y pararrayos")
        xc, yc = TT[lado]["x"], TT[lado]["y"]
        e.cil((xc * 1000, yc * 1000, 8260), (xc * 1000, yc * 1000, 9900), 16, "inox", cod=f"PR-{lado}",
              nom="Mástil de la punta captora Franklin (IRAM 2184)")
        e.cono((xc * 1000, yc * 1000, 9900), (xc * 1000, yc * 1000, 10250), 22, 2, "cobre", cod=f"PR-{lado}",
               nom="Punta captora Franklin")
        x_b, y_b = t["x_ce"] - s * 0.42, t["y1"] + 0.42
        e.polilinea([(xc * 1000, yc * 1000, 8300), (x_b * 1000, y_b * 1000, 8300), (x_b * 1000, y_b * 1000, 60)], 5,
                    "cobre", cod=f"PR-{lado}", nom="Bajada de Cu desnudo 50 mm²")
        _jabalina(e, x_b - s * 0.45, y_b + 0.30, f"PAT-{lado}")
        e.caja((t["x_cp"] - s * 0.15 - 0.2) * 1000, (t["y0"] + 0.06) * 1000, 4900, (t["x_cp"] - s * 0.15 + 0.2) * 1000,
               (t["y0"] + 0.08) * 1000, 4960, "cobre", f"PAT-{lado}", "Barra equipotencial de la torre")
    # ---------------------------------------------------------------- galpones
    for gal in D["galpones"]:
        gid = gal["id"]
        q = _galpon_geo(gal)
        s, x_w, y_bt = q["sig"], q["x_w"], q["y_bt"]
        xc, yc = q["ccm"]
        e.en("Instalación eléctrica - tableros y PLC")
        C.tablero(e, xc * 1000, yc * 1000, 0, 1000, 1800, 400, rotz=90.0 * s, tag=f"CCM-{gid}",
                  nombre=f"CCM-{gid} del transporte de guano (IP65): 20 guardamotores, arranque de la CT, variador de la CI, "
                         f"RIO-{gid} ET 200SP y switch de fibra", zocalo=200, color="inox")
        _pantalla(e, (xc + s * 0.22, yc - 0.28, 1.45), (s, 0, 0), 0.14, 0.10, f"CCM-{gid}", "Panel de operador KTP400")
        e.caja(min(x_w, x_w + s * 1.0) * 1000, (yc - 0.65) * 1000, 2350, max(x_w, x_w + s * 1.0) * 1000, (yc + 0.65) * 1000,
               2400, "chapa_techo", f"CCM-{gid}", "Alero de chapa del CCM")
        for yy in (yc - 0.55, yc + 0.55):
            e.barra((x_w * 1000, yy * 1000, 2340), ((x_w + s * 0.95) * 1000, yy * 1000, 2340), "L 40", "galv",
                    cod=f"CCM-{gid}", nom="Ménsula del alero")
        e.en("Instalación eléctrica - puesta a tierra y pararrayos")
        _jabalina(e, xc + s * 0.55, yc + 0.35, f"PAT-{gid}")
        e.cil(((xc + s * 0.2) * 1000, (yc + 0.25) * 1000, 60), ((xc + s * 0.2) * 1000, (yc + 0.25) * 1000, 400), 4, "cobre",
              cod=f"PAT-{gid}", nom="Conductor de tierra del CCM")
        e.en("Instalación eléctrica - canalizaciones")
        camaras = []
        for nom_r, (tipo, pts, r) in ruta.items():
            if r in (gid, f"{gid}-alim") and tipo == "subterraneo":
                cam = [p[:2] for p in pts[1:-1] if abs(p[2] - Z_SUBT) < 0.01]
                if r == f"{gid}-alim":                        # cámaras intermedias cada 30 m en el tramo largo
                    a, b = pts[3], pts[4]
                    cam += [(a[0], yy) for yy in np.arange(b[1] + 30, a[1] - 5, 30)]
                hechas = list(camaras)
                for c in cam:
                    if math.dist(c, (xc, yc)) > 0.6 and all(math.dist(c, h) > 1.5 for h in hechas):
                        _camara(e, c[0], c[1], f"CÑ-{gid}")
                        hechas.append(c)
                camaras[:] = hechas
        # caños a cada motor y sensor de las cintas de piso
        for f, xf in enumerate(q["filas"]):
            for n in range(GP.PISOS):
                zr = (GP.z_piso(n) - 190) / 1000
                _cano(e, [(xf + 1.01, q["yc0"] - 0.70, zr + 0.12), (xf + 1.01, q["yc0"] - 0.05, zr + 0.12),
                          (xf + 0.90, q["yc0"] - 0.05, zr + 0.12)], 20, "CÑ")
                _cano(e, [(xf - 1.01, q["yc0"] - 0.70, zr + 0.18), (xf - 1.01, q["yc0"] - 0.15, zr + 0.18),
                          (xf - 0.86, q["yc0"] - 0.15, zr + 0.18)], 16, "CÑ")
            e.en("Instalación eléctrica - seccionadores y botoneras")
            C.botonera(e, ((xf + 1.01) * 1000, (q["yc0"] - 0.80) * 1000, 1250), (0, -1, 0), tag=f"HS-{gid}-{'ABCD'[f]}")
            e.en("Instalación eléctrica - canalizaciones")
        # ménsulas de la bandeja de la CI
        ci = TR[f"CI-{gid[1]}"]
        for yy in np.arange(15.9, 21.3, 1.8):
            z = _z_ci(ci, yy) + 0.17
            e.barra(((q["x_ci"] + s * 0.30) * 1000, yy * 1000, z * 1000), ((q["x_t"] + s * 0.12) * 1000, yy * 1000, z * 1000),
                    "L 40", "galv", cod=f"BT-CI-{gid[1]}", nom="Ménsula de bandeja L 40")
