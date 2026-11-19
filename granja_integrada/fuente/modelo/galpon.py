"""Galpones automáticos de postura (Fase 3) y depósitos de huevos copiados del TP San Jorge v2.

Cada galpón: 100 × 10,5 m, 4 filas de jaulas de 5 pisos (36.000 gallinas), cintas de guano por piso con su
accionamiento en la cabecera Sur, cintas de huevos y elevadores en la cabecera Norte, carro de alimentación por fila,
líneas de bebederos de niple, ventilación túnel (4 ventiladores de 50" en el testero Sur, 3 por lateral, 3 de 36"
de mínima y paneles evaporativos de 15,4 × 1,8 m por lado al Norte), entradas de aire de mínima, iluminación LED,
silos de alimento con sinfín, sala de servicio con el tablero TS-Gg y el controlador ambiental.

Depósito de huevos: copia del depósito de San Jorge v2 (21,8 × 16 m, transelevador sobre riel de 17 m, 24 lugares,
muelle en U con 2 mesas elevadoras a 1,25 m, estaciones de armado E1 y E2), girado para que el portón dé al camino
Norte. Las cintas de huevos llegan en galería aérea cubierta desde cada galpón hasta su estación.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import componentes as C
from cad import T, Rx, Ry, Rz, caja0, cil0, proto, wp

RAIZ = Path(__file__).resolve().parents[2]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
K = json.loads((RAIZ / "datos" / "calculos.json").read_text(encoding="utf-8"))
GAL, J = D["galpon"], D["jaulas"]
VEN = K["ventilacion"]
MOTORES = {m["tag"]: m for m in K["motores_nuevos"]}

# ===================================================================================== medidas (mm)
A = GAL["A"] * 1000
Lg = GAL["L"] * 1000
HA = GAL["h_alero"] * 1000
PEND = math.radians(GAL["pendiente_deg"])
HC = HA + A / 2 * math.tan(PEND)
ZOC = GAL["zocalo"] * 1000
CAB_G, CAB_H = GAL["cabecera_guano"] * 1000, GAL["cabecera_huevos"] * 1000
CEL_A, CEL_P, CEL_H = J["celda_ancho"] * 1000, J["celda_prof"] * 1000, J["celda_alto"] * 1000
MOD = J["modulo"] * 1000
NMOD = J["modulos_por_fila"]
PASO = J["paso_pisos"] * 1000
Z1 = J["z_piso1"] * 1000
AF = J["ancho_fila"] * 1000
PAS = J["pasillo"] * 1000
PISOS, FILAS = J["pisos"], J["filas"]


def x_filas(eje):
    x_in0 = eje - A / 2 + GAL["e_muro"] * 1000
    return [x_in0 + PAS * (k + 1) + AF * k + AF / 2 for k in range(FILAS)]


def z_piso(n):
    return Z1 + PASO * n


# ===================================================================================== prototipos de jaula
def _p_malla():
    h = CEL_H
    P = CEL_P
    piezas = [caja0(P - 5, MOD, 3).translate((-P, 0, 0)), caja0(P - 5, MOD, 3).translate((5, 0, 0)),
              caja0(P - 5, MOD, 3).translate((-P, 0, h - 3)), caja0(P - 5, MOD, 3).translate((5, 0, h - 3)),
              caja0(6, MOD, h).translate((-3, 0, 0)),
              caja0(3, MOD, h - 60).translate((-P - 3, 0, 60)), caja0(3, MOD, h - 60).translate((P, 0, 60))]
    for k in range(int(round(MOD / CEL_A)) + 1):
        y = min(k * CEL_A, MOD - 3)
        piezas += [caja0(P - 5, 3, h).translate((-P, y, 0)), caja0(P - 5, 3, h).translate((5, y, 0))]
    return piezas


def _p_comedero():
    P = CEL_P
    piezas = []
    for s in (-1, 1):
        x0 = P + 3 if s > 0 else -(P + 3) - 140
        piezas += [caja0(140, MOD, 3).translate((x0, 0, 150)),                         # fondo del comedero
                   caja0(3, MOD, 110).translate((x0 + (137 if s > 0 else 0), 0, 150)),  # labio exterior
                   caja0(3, MOD, 80).translate((x0 + (0 if s > 0 else 137), 0, 150)),   # labio interior
                   caja0(AF / 2 - P - 3, MOD, 3).translate((x0 if s > 0 else -AF / 2, 0, -25)),   # bandeja de huevos
                   caja0(3, MOD, 60).translate(((AF / 2 - 3) if s > 0 else -AF / 2, 0, -25))]
    return piezas


def _p_cinta_huevos():
    return [caja0(100, MOD, 4).translate((s * (AF / 2 - 80) - 50, 0, -21)) for s in (-1, 1)]


def _p_cinta_guano():
    return caja0(J["cinta_guano_ancho"] * 1000, MOD, 2).translate((-J["cinta_guano_ancho"] * 500, 0, -88))


def _p_bebedero():
    piezas = []
    for s in (-1, 1):
        piezas.append(cil0(11, MOD).rotate((0, 0, 0), (1, 0, 0), -90).translate((s * 140, 0, CEL_H - 70)))
        for k in range(10):
            piezas.append(cil0(4, 40).translate((s * 140, CEL_A / 2 * (2 * k + 1) / 2, CEL_H - 120)))
    return piezas


def _p_gallinas():
    """60 gallinas de una jaula de 5 celdas × 2 lados (6 por celda): cuerpo, cabeza y cola."""
    piezas = []
    for s in (-1, 1):
        for c in range(int(round(MOD / CEL_A))):
            for k in range(6):
                fila, col = divmod(k, 3)
                x = s * (110 + 190 * fila + 40 * (col % 2))
                y = c * CEL_A + 105 + 200 * col
                piezas.append(wp().sphere(88).translate((x, y, 92)))
                piezas.append(wp().sphere(38).translate((x + s * 115, y + 20, 175)))
                piezas.append(wp().sphere(45).translate((x - s * 85, y - 10, 150)))
    return piezas


def _p_poste():
    alto = z_piso(PISOS - 1) + CEL_H + 160
    return [caja0(40, 40, alto).translate((-20, -20, 0)), caja0(120, 120, 6).translate((-60, -60, 0))]


# ===================================================================================== galpón
def galpon(e, g):
    gid = g["id"]
    eje, x0, x1, y0, y1 = (g[k] * 1000 for k in ("x", "x0", "x1", "y0", "y1"))
    sig = g["hacia_planta"]
    k_g = int(gid[1])
    dep = next(d for d in D["depositos"] if gid in d["galpones"])
    lado_dep = 1 if (dep["x0"] + dep["x1"]) / 2 * 1000 > eje else -1      # de qué lado está el depósito
    tag = gid
    # ------------------------------------------------------------------ estructura y cerramientos
    e.en(f"Galpones - estructura {gid}")
    from sitio import _rect_sin_huecos                                               # noqa: E402
    ct = next(t for t in D["transporte"] if t["id"] == f"CT-{k_g}")
    ci = next(t for t in D["transporte"] if t["id"] == f"CI-{k_g}")
    xa_c, xb_c = sorted((ct["p0"][0] * 1000, ct["p1"][0] * 1000))
    y_ct = ct["p0"][1] * 1000
    f = ci["foso"]
    huecos = [(xa_c - 650, xb_c + 350, y_ct - 850, y_ct + 850),
              (f["x0"] * 1000 - 200, f["x1"] * 1000 + 200, y0 - 300, f["y1"] * 1000 + 200)]
    for (a_, b_, c_, d_) in _rect_sin_huecos(x0 - 300, x1 + 300, y0 - 300, y1 + 300, huecos):
        e.caja(a_, c_, -150, b_, d_, 0, "hormigon_piso", tag, "Platea de H° con pendiente a los canales")
    for (a, b, c, d_) in ((x0, y0, x0 + 150, y1), (x1 - 150, y0, x1, y1)):
        e.caja(a, b, 0, c, d_, ZOC, "revoque", tag, "Zócalo de H° 0,50 m")
    e.caja(x0, y1 - 150, 0, x1, y1, ZOC, "revoque", tag, "Zócalo de H° 0,50 m")
    e.caja(x0, y0, 0, x1, y0 + 150, ZOC, "revoque", tag, "Zócalo de H° 0,50 m")
    paso_p = GAL["paso_porticos"] * 1000
    ys_p = list(np.arange(y0 + 150, y1, paso_p)) + [y1 - 150]
    for yy in ys_p:
        for xx in (x0 + 150, x1 - 150):
            C.columna(e, xx, yy, 0, HA - 150, "IPN 200", tag=tag, placa=(280, 280, 16), d_anclaje=16, dado=False, rot=0)
        for s in (-1, 1):
            xa = x0 + 150 if s < 0 else x1 - 150
            e.barra((xa, yy, HA - 150), (eje, yy, HC - 180), "IPN 200", "estructura", up=(0, 0, 1), cod=tag,
                    nom="Viga del pórtico IPN 200")
            e.barra((xa, yy, HA - 900), (xa - s * 900 * 0 + (-s) * 900, yy, HA - 150 + 900 * math.tan(PEND) * 0 + 300), "L 63",
                    "estructura", cod=tag, nom="Cartela del pórtico")
    # correas de techo y de pared
    n_corr = 5
    for s in (-1, 1):
        for k in range(n_corr):
            f = (k + 0.5) / n_corr
            xx = eje + s * (A / 2 - 150) * (1 - f)
            zz = HA - 60 + (HC - HA) * f
            e.barra((xx, y0, zz), (xx, y1, zz), "C 100", "galv", up=(0, 0, 1), cod=tag, nom="Correa de techo C 100")
        for zz in (1500.0, 2700.0, 3800.0):
            xx = x0 + 60 if s < 0 else x1 - 60
            e.barra((xx, y0, zz), (xx, y1, zz), "C 80", "galv", up=(0, 0, 1), cod=tag, nom="Correa de pared C 80")
    for (ya, yb) in ((y0 + 150, y0 + 150 + paso_p), (y1 - 150 - paso_p, y1 - 150)):
        for s in (-1, 1):
            xa = x0 + 150 if s < 0 else x1 - 150
            e.barra((xa, ya, HA - 300), (eje, yb, HC - 350), "RB 12", "galv", cod=tag, nom="Cruz de techo Ø12")
            e.barra((xa, yb, HA - 300), (eje, ya, HC - 350), "RB 12", "galv", cod=tag, nom="Cruz de techo Ø12")
    e.en(f"Galpones - cubierta {gid}")
    lf = (A / 2 + 400) / math.cos(PEND)
    for s in (-1, 1):
        G = T(eje, y0 - 300, HC + 60) @ Ry(s * GAL["pendiente_deg"])
        if s > 0:
            e.caja(0, 0, 0, lf, Lg + 600, 60, "panel_galpon", M=G, cod=tag, nom="Panel sándwich de techo PIR 50 mm")
        else:
            e.caja(-lf, 0, 0, 0, Lg + 600, 60, "panel_galpon", M=G, cod=tag, nom="Panel sándwich de techo PIR 50 mm")
    e.caja(eje - 200, y0 - 300, HC + 80, eje + 200, y1 + 300, HC + 140, "galv", tag, "Cumbrera")
    # cerramiento lateral con paneles, ventiladores, paneles evaporativos y entradas de aire
    e.en(f"Galpones - cerramientos {gid}")
    y_fan = [y0 + 4000.0, y0 + 6200.0, y0 + 8400.0][:VEN["ventiladores_laterales_por_lado"]]
    pad_L, pad_H = VEN["panel_por_lado_m"] * 1000, VEN["panel_alto_m"] * 1000
    yp1 = y1 - 3800.0
    yp0 = yp1 - pad_L
    for s in (-1, 1):
        xw = x0 if s < 0 else x1
        huecos = [(yf - 720, yf + 720, 1150, 2650) for yf in y_fan] + [(yp0, yp1, 700, 700 + pad_H)]
        huecos += [(yy - 450, yy + 450, 3350, 3700) for yy in np.arange(y0 + 15000, yp0 - 2000, 5000)]
        _pared_lateral(e, xw, s, y0, y1, ZOC, HA, huecos, tag)
        for yf in y_fan:
            _ventilador(e, (xw, yf, 1900), (s, 0, 0), 50, tag)
        _panel_evap(e, xw, s, yp0, yp1, 700, 700 + pad_H, tag)
        for yy in np.arange(y0 + 15000, yp0 - 2000, 5000):
            e.caja(xw - 25, yy - 450, 3350, xw + 25, yy + 450, 3700, "plastico_blanco", tag, "Entrada de aire de mínima con aleta")
            e.caja(xw - s * 120, yy - 60, 3720, xw - s * 40, yy + 60, 3800, "gris_motor", tag, "")
        e.barra((xw - s * 100, y0 + 15000, 3760), (xw - s * 100, yp0 - 2000, 3760), "RB 6", "inox", cod=tag,
                nom="Cable de accionamiento de las entradas de aire")
    # testeros: Sur con ventiladores túnel y de mínima; Norte con puertas y salida de huevos
    x_fan = [eje + d for d in (-3000, -1000, 1000, 3000)][:VEN["ventiladores_cabecera"]]
    x_36 = [eje + d for d in (-2000, 0, 2000)][:VEN["ventiladores_36"]]
    hs = [(xf - 720, xf + 720, 1150, 2650) for xf in x_fan] + [(xf - 500, xf + 500, 2950, 3950) for xf in x_36]
    _testero(e, y0, -1, x0, x1, eje, hs, tag)
    for xf in x_fan:
        _ventilador(e, (xf, y0, 1900), (0, -1, 0), 50, tag)
    for xf in x_36:
        _ventilador(e, (xf, y0, 3450), (0, -1, 0), 36, tag)
    x_sal = eje + lado_dep * 4600.0
    hn = [(eje - 1250, eje + 1250, 0, 2600), (x_sal - 350, x_sal + 350, 700, 1350), (eje - lado_dep * 3200 - 450, eje - lado_dep * 3200 + 450, 0, 2100)]
    _testero(e, y1, 1, x0, x1, eje, hn, tag)
    e.caja(eje - 1250, y1 - 25, 0, eje + 1250, y1 + 25, 2600, "chapa_trap", tag, "Portón de servicio 2,5 × 2,6 m")
    e.caja(eje - lado_dep * 3200 - 450, y1 - 25, 0, eje - lado_dep * 3200 + 450, y1 + 25, 2100, "acero_pintado", tag,
           "Puerta de personal (pediluvio y cambio de calzado)")
    e.caja(x0 - 25, y0 + 1500, 0, x0 + 25, y0 + 2400, 2100, "acero_pintado", tag, "Puerta de la cabecera de guano")
    # ------------------------------------------------------------------ jaulas, cintas, comederos y bebederos
    e.en(f"Galpones - jaulas {gid}")
    yc0 = y0 + CAB_G
    k_malla = proto(("jaula_malla",), _p_malla)
    k_com = proto(("jaula_comedero",), _p_comedero)
    k_hue = proto(("jaula_cinta_huevos",), _p_cinta_huevos)
    k_gua = proto(("jaula_cinta_guano",), _p_cinta_guano)
    k_beb = proto(("jaula_bebedero",), _p_bebedero)
    k_pos = proto(("jaula_poste",), _p_poste)
    k_gal = proto(("jaula_gallinas",), _p_gallinas)
    xs = x_filas(eje)
    z_top = z_piso(PISOS - 1) + CEL_H
    for f, xf in enumerate(xs):
        fila = "ABCD"[f]
        for m in range(NMOD):
            ym = yc0 + MOD * m
            for n in range(PISOS):
                M = T(xf, ym, z_piso(n))
                e.add(k_malla, "malla", M, f"{gid}-{fila}", f"Jaula de 5 celdas × 2 lados, 6 aves por celda (piso {n + 1})")
                e.add(k_com, "galv", M, f"{gid}-{fila}", "Comedero y bandeja de huevos")
                e.add(k_hue, "plastico_blanco", M, f"{gid}-{fila}", "Cinta de huevos de 100 mm")
                e.add(k_gua, "banda_pp", M, f"{gid}-{fila}", "Cinta de guano de PP 1,25 m")
                e.add(k_beb, "plastico_gris", M, f"{gid}-{fila}", "Línea de bebederos de niple")
                e.add(k_gal, "gallina", M, f"{gid}-{fila}", "Gallinas ponedoras (60 por jaula)")
            for x_ in (-AF / 2 - 20, 0.0, AF / 2 + 20):
                e.add(k_pos, "galv", T(xf + x_, ym, 0), f"{gid}-{fila}", "Parante de la batería" if m == 0 else "")
        ym1 = yc0 + MOD * NMOD
        for x_ in (-AF / 2 - 20, 0.0, AF / 2 + 20):
            e.add(k_pos, "galv", T(xf + x_, ym1, 0), f"{gid}-{fila}", "")
        # rieles y carro de alimentación
        for s in (-1, 1):
            e.barra((xf + s * 600, yc0 - 300, z_top + 120), (xf + s * 600, ym1 + 900, z_top + 120), "L 40", "galv",
                    cod=f"{gid}-{fila}", nom="Riel del carro de alimentación")
        _carro(e, xf, yc0 + MOD * (6 + 7 * f), z_top, f"{gid}-{fila}")
        # cabecera Sur: accionamientos de las cintas de guano y chute al canal de la transversal
        e.en(f"Galpones - accionamientos de guano {gid}")
        for n in range(PISOS):
            zr = z_piso(n) - 190
            e.cil((xf - 700, yc0 - 150, zr), (xf + 700, yc0 - 150, zr), 100, "acero_pintado", cod=f"{gid}-{fila}",
                  nom=f"Rodillo motriz de la cinta de guano (piso {n + 1})")
            e.caja(xf - 640, yc0 - 280, zr - 120, xf + 640, yc0 - 260, zr - 20, "naranja", f"{gid}-{fila}", "Rascador de la cinta de guano")
            num = f * PISOS + n + 1
            tg = f"M{k_g}{num:02d}"
            C.motorreductor_ortogonal(e, 1.1, T(xf + 760, yc0 - 150, zr) @ Rz(90), tg)
            C.sensor(e, "velocidad", (xf - 760, yc0 - 150, zr + 60), (-1, 0, 0), tag=f"SS-{tg}")
        e.caja(xf - AF / 2, yc0 - 520, 0, xf + AF / 2, yc0 - 500, z_top, "galv", f"{gid}-{fila}", "Chute de descarga de guano al canal")
        for s in (-1, 1):
            e.caja(xf + s * AF / 2 - 10, yc0 - 520, 0, xf + s * AF / 2 + 10, yc0 - 40, z_top, "galv", f"{gid}-{fila}", "")
        e.caja(xf - 900, yc0 - 600, z_top + 50, xf + 900, yc0 - 20, z_top + 60, "malla", f"{gid}-{fila}", "Protección de transmisiones")
        # cabecera Norte: elevador de huevos de la fila
        e.en(f"Galpones - huevos {gid}")
        ye = ym1 + 150
        e.caja(xf - AF / 2, ye, 0, xf + AF / 2, ye + 550, z_top, "galv", f"{gid}-{fila}", "Elevador de huevos de varillas (5 pisos, 2 lados)")
        e.caja(xf - AF / 2 + 60, ye + 550, 0, xf + AF / 2 - 60, ye + 560, z_top - 100, "policarbonato", f"{gid}-{fila}", "Tapa transparente del elevador")
        C.motor(e, 0.37, T(xf + AF / 2 + 120, ye + 280, z_top - 200) @ Rz(90), f"MH{k_g}{f + 1}", patas=False)
        e.en(f"Galpones - jaulas {gid}")
    # cinta transversal de huevos y salida hacia el depósito
    e.en(f"Galpones - huevos {gid}")
    yh = yc0 + MOD * NMOD + 1100
    xa, xb = sorted((xs[0] - AF / 2, x_sal))
    if lado_dep < 0:
        xa, xb = sorted((xs[-1] + AF / 2, x_sal))
    e.caja(xa, yh - 150, 950, xb, yh + 150, 1000, "plastico_blanco", tag, "Cinta transversal de huevos 300 mm")
    e.caja(xa, yh - 170, 880, xb, yh + 170, 950, "inox", tag, "Bastidor de la cinta transversal de huevos")
    for xx in np.arange(xa + 300, xb, 2000):
        e.caja(xx - 20, yh - 160, 0, xx + 20, yh + 160, 880, "inox", tag, "")
    e.caja(x_sal - 170, yh, 880, x_sal + 170, y1 + 300, 1000, "inox", tag, "Curva y salida de la cinta de huevos")
    C.tablero(e, eje - lado_dep * 1600, y1 - 400, 0, 600, 800, 250, rotz=180, tag=f"MH-{gid}", nombre="Mando de la recolección de huevos")
    # ------------------------------------------------------------------ alimentación, agua, luz y control
    e.en(f"Galpones - servicios {gid}")
    yb = y1 - 1200
    e.cil((x0 + 300, yb, z_top + 600), (x1 - 300, yb, z_top + 600), 45, "galv", cod=tag, nom="Sinfín de alimento Ø90 a los carros")
    for xf in xs:
        e.cono((xf, yb, z_top + 560), (xf, yb, z_top + 220), 60, 220, "galv", cod=tag, nom="Bajada a la tolva de carga del carro")
    e.polilinea([(x0 + 400, yb + 300, z_top + 450), (x1 - 400, yb + 300, z_top + 450)], 16, "plastico_gris", cod=tag,
                nom="Colector de agua PEAD Ø32 a las líneas de bebederos")
    for xf in xs:
        e.polilinea([(xf, yb + 300, z_top + 450), (xf, yc0 + MOD * NMOD, z_top + 450), (xf, yc0 + MOD * NMOD, z_top - 60)], 10,
                    "plastico_gris", cod=tag, nom="Bajada a los reguladores de presión de la fila")
    for xa_ in [x0 + 150 + GAL["e_muro"] * 1000 + PAS / 2 + (PAS + AF) * k for k in range(FILAS + 1)]:
        for yy in np.arange(yc0 + 1500, yc0 + MOD * NMOD, 6000):
            e.caja(xa_ - 20, yy - 600, z_top + 260, xa_ + 20, yy + 600, z_top + 300, "luz", "IL-" + gid, "Tubo LED regulable 18 W (luz de postura)")
        for zl in (z_piso(1) + 300, z_piso(3) + 300):
            for yy in np.arange(yc0 + 4500, yc0 + MOD * NMOD, 6000):
                e.caja(xa_ - 15, yy - 450, zl, xa_ + 15, yy + 450, zl + 25, "luz", "IL-" + gid, "Lámpara LED de pasillo a media altura 9 W")
    # sala de servicio exterior con tablero y controlador
    xs0 = eje - lado_dep * 5250 if lado_dep > 0 else eje + 1000
    xs1 = xs0 + 4250 if lado_dep > 0 else eje + 5250
    xs0, xs1 = sorted((eje - lado_dep * 1000, eje - lado_dep * 5250))
    e.caja(xs0, y1, 0, xs1, y1 + 3000, 3000, "panel", f"SS-{gid}", f"Sala de servicio del {gid}")
    e.caja(xs0 - 100, y1 - 100, 3000, xs1 + 100, y1 + 3100, 3080, "chapa_techo", f"SS-{gid}", "")
    C.tablero(e, (xs0 + xs1) / 2 - 600, y1 + 3000 + 2, 0, 1200, 2000, 400, rotz=0, tag=f"TS-{gid}",
              nombre=f"Tablero seccional TS-{gid} (fuerza, CCM de las cintas y PLC)")
    C.tablero(e, (xs0 + xs1) / 2 + 900, y1 + 3000 + 2, 600, 600, 800, 250, rotz=0, tag=f"CA-{gid}",
              nombre="Controlador ambiental (temperatura, humedad, NH3 y CO2)")
    for yy in (y0 + 30000, y0 + 60000, y0 + 90000):
        C.sensor(e, "humedad", (eje, yy, 2400), (0, 0, -1), tag=f"TH-{gid}")
    C.sensor(e, "presion", (x1 - 200, y1 - 6000, 3500), (-1, 0, 0), tag=f"PDT-{gid}")


def _pared_lateral(e, xw, s, y0, y1, z0, z1, huecos, tag):
    from planta import _rectangulos_libres                                          # noqa: E402
    for (a, b, za, zb) in _rectangulos_libres(y0, y1, z0, z1, huecos):
        e.caja(xw - (60 if s < 0 else 0), a, za, xw + (60 if s > 0 else 0), b, zb, "panel_galpon", tag,
               "Panel sándwich de pared PIR 50 mm")


def _testero(e, y, s, x0, x1, eje, huecos, tag):
    from planta import _rectangulos_libres                                          # noqa: E402
    for (a, b, za, zb) in _rectangulos_libres(x0, x1, ZOC, HA, huecos):
        e.caja(a, y - (60 if s < 0 else 0), za, b, y + (60 if s > 0 else 0), zb, "panel_galpon", tag, "Panel sándwich del testero")
    k = proto(("triang_gal", round(A), round(HC - HA)), lambda: wp().polyline([(0, 0), (A, 0), (A / 2, HC - HA)]).close().extrude(60))
    e.add(k, "panel_galpon", T(x0, y + (0 if s > 0 else 0), HA) @ Rx(90) @ T(0, 0, -30), tag, "Panel del hastial")


def _ventilador(e, c, n, pulg, tag):
    """Ventilador de pared con marco, persiana, cono y motor. c: centro en el plano de la pared; n: normal hacia afuera."""
    lado = 1380.0 if pulg == 50 else 920.0
    nx, ny = n[0], n[1]
    rot = 90 if abs(nx) > 0.5 else 0
    G = T(*c) @ Rz(rot if nx >= 0 and ny >= 0 else rot + 180)
    k = proto(("vent", pulg), lambda: [caja0(lado, 420, lado).translate((-lado / 2, -200, -lado / 2)).faces(">Y").shell(-3),
                                       cil0(lado * 0.46, 380).rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 220, 0))])
    e.add(k, "galv", G, tag, f"Ventilador de {pulg}\" ({36000 if pulg == 50 else 17000} m³/h a 25 Pa)")
    kp = proto(("vent_pers", pulg), lambda: [caja0(lado - 40, 8, 40).translate((-(lado - 40) / 2, 0, -lado / 2 + 30 + 110 * i))
                                             for i in range(int((lado - 60) / 110))])
    e.add(kp, "plastico_blanco", G @ T(0, 205, 0), tag, "Persiana de cierre")
    C.motor(e, 1.1 if pulg == 50 else 0.55, G @ T(0, -230, 0) @ Rz(-90), "", patas=False)


def _panel_evap(e, xw, s, ya, yb, za, zb, tag):
    e.caja(xw - 75, ya, za, xw + 75, yb, zb, "celulosa", tag, "Panel evaporativo de celulosa 150 mm")
    e.caja(xw - s * 75 - 60, ya, zb, xw - s * 75 + 60, yb, zb + 120, "plastico_gris", tag, "Distribuidor de agua del panel")
    e.caja(xw - s * 75 - 80, ya, za - 150, xw - s * 75 + 80, yb, za, "plastico_gris", tag, "Canaleta colectora")
    e.cil((xw + s * 600, ya - 600, 0), (xw + s * 600, ya - 600, 700), 450, "plastico_gris", cod=tag, nom="Tanque de recirculación 400 L con bomba")
    e.caja(xw + s * 130, ya - 200, za - 100, xw + s * 170, yb + 200, zb + 300, "malla", tag, "Malla antipájaros del panel")


def _carro(e, xf, y, z_top, tag):
    """Carro de alimentación sobre rieles con 10 tolvas (5 pisos × 2 lados)."""
    e.caja(xf - 700, y - 300, z_top + 140, xf + 700, y + 300, z_top + 340, "amarillo", tag, "Carro de alimentación automático")
    C.motor(e, 0.55, T(xf, y + 380, z_top + 260) @ Rz(90), "", patas=False)
    for s in (-1, 1):
        x_ = xf + s * (AF / 2 + 40)
        e.barra((x_, y, z_top + 140), (x_, y, z_piso(0) + 300), "RHS 40", "amarillo", cod=tag, nom="Bajada del carro")
        for n in range(PISOS):
            zt = z_piso(n) + 420
            e.cono((x_ - s * 20, y, zt), (x_ - s * 20, y, zt - 180), 140, 50, "galv", cod=tag, nom="Tolva del carro")


# ===================================================================================== silos de alimento
def silos(e):
    e.en("Galpones - silos de alimento")
    for s in D["silos_alimento"]:
        x, y = s["x"] * 1000, s["y"] * 1000
        R = s["D"] * 500
        hp, hc, hcil = s["h_patas"] * 1000, s["h_cono"] * 1000, s["h_cil"] * 1000
        tag = s["id"]
        e.cono((x, y, hp + hc), (x, y, hp), R, 150, "galv", cod=tag, nom=f"Silo de alimento {s['cap_t']} t: cono")
        e.tubo((x, y, hp + hc), (x, y, hp + hc + hcil), R, R - 4, "galv", cod=tag, nom="Silo de alimento: cuerpo corrugado")
        e.cono((x, y, hp + hc + hcil), (x, y, hp + hc + hcil + 900), R + 50, 300, "galv", cod=tag, nom="Techo del silo con boca de carga")
        for a in range(4):
            ang = math.radians(45 + 90 * a)
            px, py = x + (R - 100) * math.cos(ang), y + (R - 100) * math.sin(ang)
            C.columna(e, px, py, 0, hp + hc * 0.6, "RHS 100", tag=tag, placa=(250, 250, 12), d_anclaje=16)
        C.escalera_marinera(e, (x + R + 120, y, 0), hp + hc + hcil + 700, tag=tag, frente=(-1, 0, 0))
        g = next(gg for gg in D["galpones"] if gg["id"] == s["galpon"])
        xw = g["x0"] * 1000 if x < g["x"] * 1000 else g["x1"] * 1000
        e.polilinea([(x, y, hp - 100), (x, y, 1200), (xw, y, 1200)], 45, "galv", cod=tag, nom="Sinfín flexible Ø90 al galpón")
        C.motor(e, 0.75, T(x, y, hp - 200), f"MS-{tag}", patas=False)
        C.sensor(e, "celda", (x + R - 100, y, 0), (0, 0, 1), tag=f"WT-{tag}")


# ===================================================================================== depósito de huevos (San Jorge v2)
SJ = {"riel": (3850.0, 20900.0), "mod": [19650.0, 18300.0, 16950.0, 15600.0, 14250.0, 12900.0],
      "lugares_l": [2750.0, 1700.0, -1700.0, -2750.0], "E1": 7500.0, "E2": 10100.0, "l_est": -1700.0,
      "mesas_d": 5100.0, "mesas_l": [1700.0, -1700.0], "muelle": (0.0, 6100.0, -3600.0, 3600.0),
      "muelle_hueco": (0.0, 3700.0, -900.0, 900.0), "muelle_h": 1250.0, "porton": (3500.0, 3800.0),
      "palet": (1200.0, 1000.0, 1800.0), "h_piso": 320.0}


def deposito(e, dep):
    tag = dep["id"]
    x0, x1, y0, y1 = (dep[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
    xm = (x0 + x1) / 2
    sx = 1 if dep["lado"] == "O" else -1
    em = D["deposito"]["e_muro"] * 1000
    hl = D["deposito"]["h_libre"] * 1000
    yi = y1 - em

    def P(d, l, z=0.0):                         # (d desde el muro del portón, l desde el eje del pasillo) -> (x, y, z)
        return (xm + sx * l, yi - d, z)
    e.en(f"Depósitos de huevos - edificio {tag}")
    e.caja(x0, y0, -150, x1, y1, 0, "hormigon_piso", tag, "Platea de H° con terminación llaneada")
    wp_, hp = SJ["porton"]
    for (a, b, c, d_) in ((x0, y0, x1, y0 + em), (x0, y0, x0 + em, y1), (x1 - em, y0, x1, y1)):
        e.caja(a, b, 0, c, d_, hl + 300, "panel", tag, "Muro de panel sándwich 100 mm")
    e.caja(x0, y1 - em, 0, xm - wp_ / 2, y1, hl + 300, "panel", tag, "Muro del portón")
    e.caja(xm + wp_ / 2, y1 - em, 0, x1, y1, hl + 300, "panel", tag, "Muro del portón")
    e.caja(xm - wp_ / 2, y1 - em, hp, xm + wp_ / 2, y1, hl + 300, "panel", tag, "Dintel del portón")
    e.caja(xm - wp_ / 2, y1 - 30, 0, xm + wp_ / 2, y1 + 10, hp, "chapa_trap", tag, f"Portón seccional {wp_ / 1000:.1f} × {hp / 1000:.1f} m")
    e.caja(x0 - 300, y0 - 300, hl + 300, x1 + 300, y1 + 300, hl + 450, "chapa_techo", tag, "Techo de chapa con aislación")
    for yy in np.arange(y0 + 500, y1, 5450):
        e.barra((x0, yy, hl + 250), (x1, yy, hl + 250), "IPE 200", "estructura", up=(0, 0, 1), cod=tag, nom="Viga de techo IPE 200")
    e.caja(xm - wp_ / 2 - 400, y1, hp + 100, xm + wp_ / 2 + 400, y1 + 1500, hp + 200, "chapa_techo", tag, "Alero del muelle")
    for yy in np.arange(y0 + 2700, y1 - 1000, 5450):
        e.caja(xm - 3500, yy - 500, hl + 452, xm + 3500, yy + 500, hl + 470, "policarbonato", tag, "Lucernario")
        for xx in (xm - 4500, xm + 4500):
            e.cono((xx, yy, hl + 200), (xx, yy, hl - 100), 120, 230, "aluminio", cod=f"IL-{tag}", nom="Campana LED 100 W (200 lx)")
            e.cil((xx, yy, hl - 100), (xx, yy, hl - 120), 225, "luz", cod=f"IL-{tag}", nom="")
    # ------------------------------------------------------------------ muelle en U con 2 mesas elevadoras
    e.en(f"Depósitos de huevos - muelle y almacén {tag}")
    d0, d1, l0, l1 = SJ["muelle"]
    hd0, hd1, hl0, hl1 = SJ["muelle_hueco"]
    hm = SJ["muelle_h"]
    for (da, db, la, lb) in ((d0, d1, l0, hl0), (d0, d1, hl1, l1), (hd1, d1, hl0, hl1)):
        pa, pb = P(da, la), P(db, lb)
        e.caja(min(pa[0], pb[0]), min(pa[1], pb[1]), 0, max(pa[0], pb[0]), max(pa[1], pb[1]), hm, "hormigon", tag,
               "Muelle en U de H° a +1,25 m")
    for l in SJ["mesas_l"]:
        c = P(SJ["mesas_d"], l)
        e.caja(c[0] - 700, c[1] - 600, 0, c[0] + 700, c[1] + 600, hm - 30, "gris_motor", tag, "Mesa elevadora de tijera 1.000 kg")
        e.caja(c[0] - 700, c[1] - 600, hm - 30, c[0] + 700, c[1] + 600, hm, "rejilla", tag, "")
    for l in (l0, l1):
        pa, pb = P(0, l), P(d1, l)
        e.barra((pa[0], pa[1], hm), (pb[0], pb[1], hm), "CHS 42", "amarillo", cod=tag, nom="Baranda del muelle")
    # ------------------------------------------------------------------ riel y transelevador
    da, db = SJ["riel"]
    pa, pb = P(da, 0), P(db, 0)
    for lr in (-600, 600):
        q0, q1 = P(da, lr), P(db, lr)
        e.barra(q0, q1, "UPN 100", "acero", up=(0, 0, 1), cod=f"TE-{tag}", nom="Riel del transelevador (17 m)")
    d_te = 12000.0
    c = P(d_te, 0)
    e.caja(c[0] - 700, c[1] - 1250, 100, c[0] + 700, c[1] + 1250, 400, "amarillo", f"TE-{tag}", "Transelevador 1.000 kg: testero con ruedas Ø250")
    for (sl, sd) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        e.cil((c[0] + sl * 600 - 60, c[1] + sd * 1000, 125), (c[0] + sl * 600 + 60, c[1] + sd * 1000, 125), 125, "negro",
              cod=f"TE-{tag}", nom="Rueda Ø250")
    for sd in (-1, 1):
        e.caja(c[0] - 120, c[1] + sd * 1000 - 100, 400, c[0] + 120, c[1] + sd * 1000 + 100, 3950, "amarillo", f"TE-{tag}", "Mástil")
    e.caja(c[0] - 150, c[1] - 1150, 3750, c[0] + 150, c[1] + 1150, 3950, "amarillo", f"TE-{tag}", "Travesaño superior del pórtico")
    e.caja(c[0] - 500, c[1] - 900, 1200, c[0] + 500, c[1] + 900, 1300, "gris_motor", f"TE-{tag}", "Carro de elevación")
    for sd in (-1, 1):
        e.caja(c[0] - 1700 * sx * 0 - 600, c[1] + sd * 300 - 60, 1150, c[0] + 600, c[1] + sd * 300 + 60, 1200, "acero",
               f"TE-{tag}", "Horquilla telescópica")
    e.caja(c[0] + 300, c[1] + 900, 600, c[0] + 700, c[1] + 1250, 1500, "tablero", f"TE-{tag}", "Tablero de a bordo")
    # ------------------------------------------------------------------ almacén: 24 lugares sobre largueros de 0,32 m
    lp, ap, hpal = SJ["palet"]
    ocup = [(0, 2750), (0, 1700), (0, -1700), (0, -2750), (1, 2750), (1, 1700), (1, -2750), (2, 2750), (5, 2750)]
    for i, d in enumerate(SJ["mod"]):
        for l in SJ["lugares_l"]:
            c = P(d, l)
            for s_ in (-1, 1):
                e.caja(c[0] - 520, c[1] + s_ * 420 - 50, 0, c[0] + 520, c[1] + s_ * 420 + 50, SJ["h_piso"], "amarillo", tag,
                       "Larguero de apoyo de palet (0,32 m)")
            if (i, l) in ocup:
                _palet(e, c[0], c[1], SJ["h_piso"], tag)
    for d in (SJ["E1"], SJ["E2"]):
        c = P(d, SJ["l_est"])
        for s_ in (-1, 1):
            e.caja(c[0] - 520, c[1] + s_ * 420 - 50, 0, c[0] + 520, c[1] + s_ * 420 + 50, SJ["h_piso"], "amarillo", tag,
                   "Estación de armado de palets")
        _palet(e, c[0], c[1], SJ["h_piso"], tag, alto=1000)
        C.tablero(e, c[0] + sx * (-900), c[1], 0, 600, 1000, 300, rotz=90 if sx > 0 else -90, tag=f"E-{tag}",
                  nombre="Puesto de armado: botonera y pantalla KTP400")
    C.tablero(e, x1 - em - 10 if sx < 0 else x0 + em + 10, y0 + 2500, 0, 1000, 1900, 400, rotz=-90 if sx > 0 else 90,
              tag=f"TE-01-{tag}", nombre="Tablero TE-01 del transelevador (S7-1200, Flexi Soft, G120C)")


def _palet(e, x, y, z, tag, alto=None):
    lp, ap, hp = SJ["palet"]
    hp = alto or hp
    e.caja(x - lp / 2, y - ap / 2, z, x + lp / 2, y + ap / 2, z + 144, "madera", tag, "Palet de madera 1,2 × 1,0 m")
    e.caja(x - lp / 2 + 10, y - ap / 2 + 10, z + 144, x + lp / 2 - 10, y + ap / 2 - 10, z + hp, "carton", tag,
           "Cajones de 12 maples de 30 huevos (25 por palet)")
    e.caja(x - lp / 2 + 5, y - ap / 2 + 5, z + hp - 20, x + lp / 2 - 5, y + ap / 2 - 5, z + hp, "plastico_blanco", tag, "Film y esquineros")


# ===================================================================================== cintas de huevos a los depósitos
def cintas_huevos(e):
    """Galería aérea cubierta (+2,6 m) desde la salida de cada galpón hasta su estación de armado."""
    e.en("Galpones - cintas de huevos al depósito")
    z = 2600.0
    for dep in D["depositos"]:
        x0, x1, y0, y1 = (dep[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
        xm = (x0 + x1) / 2
        sx = 1 if dep["lado"] == "O" else -1
        yi = y1 - D["deposito"]["e_muro"] * 1000
        x_muro = x0 if sx > 0 else x1
        for gid, est in zip(sorted(dep["galpones"], key=lambda g: abs(next(gg for gg in D["galpones"] if gg["id"] == g)["x"] * 1000 - xm),
                                   reverse=True), ("E1", "E2")):
            g = next(gg for gg in D["galpones"] if gg["id"] == gid)
            eje, gy1 = g["x"] * 1000, g["y1"] * 1000
            lado_dep = 1 if xm > eje else -1
            x_sal = eje + lado_dep * 4600.0
            y_est = yi - SJ[est]
            x_est = xm + sx * SJ["l_est"]
            x_carril = x_muro - sx * (1400.0 if est == "E1" else 2950.0)
            if est == "E1":
                pts = [(x_sal, gy1 + 300, 1000), (x_sal, gy1 + 1300, z), (x_sal, y_est, z), (x_muro, y_est, z),
                       (x_est - sx * 600, y_est, z), (x_est - sx * 600, y_est, 1000)]
            else:
                pts = [(x_sal, gy1 + 300, 1000), (x_sal, gy1 + 1300, z), (x_sal, gy1 + 2000, z), (x_carril, gy1 + 2000, z),
                       (x_carril, y_est, z), (x_muro, y_est, z), (x_est - sx * 600, y_est, z), (x_est - sx * 600, y_est, 1000)]
            tag = f"CH-{gid}"
            for a, b in zip(pts, pts[1:]):
                _tramo_huevos(e, np.array(a, float), np.array(b, float), tag, cubierta=(a[2] == z and b[2] == z))
            for a, b in zip(pts[1:-2], pts[2:-1]):
                a, b = np.array(a), np.array(b)
                Lt = np.linalg.norm(b - a)
                for t_ in np.arange(1500, Lt, 3000):
                    p = a + (b - a) * t_ / Lt
                    if (x0 - 100 < p[0] < x1 + 100) and (y0 - 100 < p[1] < y1 + 100):
                        continue
                    C.columna(e, p[0], p[1], 0, z - 120, "RHS 60", tag=tag, placa=(180, 180, 10), d_anclaje=12, dado=False)
            C.sensor(e, "velocidad", tuple(np.array(pts[2]) + (0, 0, 60)), (0, 0, 1), tag=f"SS-{tag}")


def _tramo_huevos(e, a, b, tag, cubierta=True):
    from cad import alinear
    Lt = float(np.linalg.norm(b - a))
    if Lt < 50:
        return
    G = alinear(a, b, up=(0, 0, 1))
    e.caja(-20, -150, 0, 0, 150, Lt, "plastico_blanco", M=G, cod=tag, nom="Cinta de huevos 300 mm")
    e.caja(-120, -180, 0, -20, 180, Lt, "inox", M=G, cod=tag, nom="Bastidor de acero inoxidable")
    if cubierta:
        R = 350.0
        k = proto(("tunel_huevos", round(Lt)), lambda: wp().moveTo(R, 0).threePointArc((0, R), (-R, 0)).lineTo(-R + 3, 0)
                  .threePointArc((0, R - 3), (R - 3, 0)).close().extrude(Lt))
        e.add(k, "policarbonato", G @ Rz(-90) @ T(0, 0, 0), tag, "Túnel de policarbonato de la cinta de huevos")


def construir(e):
    for g in D["galpones"]:
        galpon(e, g)
    silos(e)
    for dep in D["depositos"]:
        deposito(e, dep)
    cintas_huevos(e)
