"""Predio de la granja: terreno, caminos sucios y limpios, playones, cerco perimetral y sanitario interno, acceso
con portón, garita, vado sanitario, báscula y edificio de bioseguridad, estacionamiento, subestación, tanque de agua,
tanque de efluentes, compostera de mortandad, cortina forestal, alumbrado y los lugares de ampliación G0 y G5.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import componentes as C
from cad import T, Rz, proto, wp

RAIZ = Path(__file__).resolve().parents[2]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))


def _rect_sin_huecos(x0, x1, y0, y1, huecos):
    """Parte [x0, x1] × [y0, y1] en rectángulos que no pisan los huecos (x0, x1, y0, y1)."""
    xs = sorted({x0, x1} | {h[0] for h in huecos if x0 < h[0] < x1} | {h[1] for h in huecos if x0 < h[1] < x1})
    res = []
    for a, b in zip(xs, xs[1:]):
        m = (a + b) / 2
        hs = sorted((h[2], h[3]) for h in huecos if h[0] <= m <= h[1])
        y = y0
        for h0, h1 in hs:
            if h0 > y:
                res.append((a, b, y, min(h0, y1)))
            y = max(y, h1)
        if y < y1:
            res.append((a, b, y, y1))
    return [r for r in res if r[1] - r[0] > 1 and r[3] - r[2] > 1]


def terreno(e):
    e.en("Predio - terreno")
    pr = D["predio"]
    xc, yc = (pr["x0"] + pr["x1"]) / 2, (pr["y0"] + pr["y1"]) / 2
    X0, X1, Y0, Y1 = (xc - 700) * 1000, (xc + 700) * 1000, (yc - 700) * 1000, (yc + 700) * 1000
    huecos = []
    for t in D["transporte"]:
        if "foso" in t:
            f = t["foso"]
            y_muro = D["galpones"][0]["y0"]
            huecos.append((f["x0"] * 1000 - 200, f["x1"] * 1000 + 200, f["y0"] * 1000 - 200, y_muro * 1000))
    for (a, b, c, d) in _rect_sin_huecos(X0, X1, Y0, Y1, huecos):
        e.caja(a, c, -400, b, d, -20, "pasto", "TERRENO", "Terreno natural con césped")


def caminos(e):
    e.en("Predio - caminos y playones")
    for c in D["caminos"]:
        mat = "asfalto" if c["zona"] == "limpia" else "hormigon"
        e.caja(c["x0"] * 1000, c["y0"] * 1000, -20, c["x1"] * 1000, c["y1"] * 1000, 30, mat, c["id"],
               f"Camino {c['id']} ({c['zona']}): {c['nom']}")
    for p in D["playones"]:
        e.caja(p["x0"] * 1000, p["y0"] * 1000, -20, p["x1"] * 1000, p["y1"] * 1000, 40, "hormigon", p["id"], f"Playón {p['id']}: {p['nom']}")
    # acceso de la planta al depósito de expedición E7 (Rev. D), sector sucio
    e.caja(53000, -15000, -20, 80400, -1200, 40, "hormigon", "PY7", "Playón de expedición del depósito E7")
    calle = D["calle"]
    pr = D["predio"]
    e.caja((pr["x0"] - 600) * 1000, calle["y0"] * 1000, -20, (pr["x1"] + 600) * 1000, calle["y1"] * 1000, 20, "ripio",
           "CALLE", calle["nom"])
    a = D["acceso"]
    p = a["porton"]
    e.caja(p["x0"] * 1000, calle["y1"] * 1000, -20, p["x1"] * 1000, a["vado"]["y0"] * 1000, 30, "hormigon", "ACC",
           "Entrada desde el camino público")


def cerco(e):
    e.en("Predio - cercos y accesos")
    pr = D["predio"]
    a = D["acceso"]
    x0, x1, y0, y1 = (pr[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
    hueco = (a["porton"]["x0"] * 1000, a["porton"]["x1"] * 1000)
    bio = (a["bioseguridad"]["x0"] * 1000, a["bioseguridad"]["x1"] * 1000)
    tramos = [((x0, y0), (hueco[0], y0)), ((hueco[1], y0), (bio[0], y0)), ((bio[1], y0), (x1, y0)),
              ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    k_poste = proto(("poste_cerco",), lambda: wp().rect(100, 100).extrude(2400).translate((0, 0, -400)))
    for (pa, pb) in tramos:
        pa, pb = np.array(pa, float), np.array(pb, float)
        Lt = np.linalg.norm(pb - pa)
        if Lt < 10:
            continue
        u = (pb - pa) / Lt
        for t in np.arange(0, Lt + 1, 3000):
            p = pa + u * min(t, Lt)
            e.add(k_poste, "hormigon", T(p[0], p[1], 0), "CERCO", "Poste de H° del cerco perimetral" if t == 0 else "")
        ang = math.degrees(math.atan2(u[1], u[0]))
        e.caja_rot(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, 1000), (Lt, 6, 1800), ang, "malla", "CERCO",
                   "Tejido romboidal 2 m con 3 hilos de púa (cerco perimetral, bioseguridad)")
    # portón corredizo, garita, vado, báscula, bioseguridad, estacionamiento
    e.caja(hueco[0], y0 - 60, 0, hueco[1], y0 + 60, 1900, "malla", "ACC", "Portón corredizo de acceso de 11 m")
    g = a["garita"]
    e.caja(g["x0"] * 1000, g["y0"] * 1000, 0, g["x1"] * 1000, g["y1"] * 1000, g["h"] * 1000, "revoque", "GAR",
           "Garita de control de ingreso")
    e.caja(g["x0"] * 1000 - 400, g["y0"] * 1000 - 400, g["h"] * 1000, g["x1"] * 1000 + 400, g["y1"] * 1000 + 400,
           g["h"] * 1000 + 150, "chapa_techo", "GAR", "")
    v = a["vado"]
    e.caja(v["x0"] * 1000, v["y0"] * 1000, -300, v["x1"] * 1000, v["y1"] * 1000, -40, "agua", "VADO",
           "Vado sanitario con solución desinfectante (largo útil 5 m)")
    for xx in (v["x0"] * 1000 - 200, v["x1"] * 1000):
        e.caja(xx, v["y0"] * 1000, -300, xx + 200, v["y1"] * 1000, 150, "hormigon", "VADO", "Cordón del vado")
    for s in (-1, 1):
        xx = (v["x0"] if s < 0 else v["x1"]) * 1000 + s * 600
        e.cil((xx, (v["y0"] + v["y1"]) * 500, 0), (xx, (v["y0"] + v["y1"]) * 500, 3200), 50, "galv", cod="VADO",
              nom="Arco de aspersión de ruedas y chasis")
    e.cil((v["x0"] * 1000 - 600, (v["y0"] + v["y1"]) * 500, 3200), (v["x1"] * 1000 + 600, (v["y0"] + v["y1"]) * 500, 3200), 50,
          "galv", cod="VADO", nom="Arco de aspersión de ruedas y chasis")
    b = a["bascula"]
    e.caja(b["x0"] * 1000, b["y0"] * 1000, -50, b["x1"] * 1000, b["y1"] * 1000, 120, "acero_pintado", "BAS",
           f"Báscula para camiones {b['cap_t']} t (16 × 3,5 m)")
    e.caja(b["x1"] * 1000 + 2000, (b["y0"] + 6) * 1000, 0, b["x1"] * 1000 + 5000, (b["y0"] + 9) * 1000, 2700, "revoque", "BAS",
           "Casilla del indicador de la báscula")
    bi = a["bioseguridad"]
    e.caja(bi["x0"] * 1000, bi["y0"] * 1000, 0, bi["x1"] * 1000, bi["y1"] * 1000, bi["h"] * 1000, "revoque", "BIO",
           "Edificio de bioseguridad: vestuario sucio, duchas y vestuario limpio (cruza el cerco)")
    e.caja(bi["x0"] * 1000 - 400, bi["y0"] * 1000 - 400, bi["h"] * 1000, bi["x1"] * 1000 + 400, bi["y1"] * 1000 + 400,
           bi["h"] * 1000 + 150, "chapa_techo", "BIO", "")
    es = a["estacionamiento"]
    e.caja(es["x0"] * 1000, es["y0"] * 1000, -20, es["x1"] * 1000, es["y1"] * 1000, 30, "asfalto", "EST",
           "Estacionamiento del personal (afuera del cerco)")
    for xx in np.arange(es["x0"] * 1000 + 2500, es["x1"] * 1000, 2500):
        e.caja(xx - 50, es["y0"] * 1000 + 500, 30, xx + 50, es["y1"] * 1000 - 500, 33, "plastico_blanco", "EST", "")
    # cerco sanitario interno alrededor de la zona sucia (planta) con tranquera en C1
    zs = (-21000.0, 54000.0, -23000.0, 40000.0)
    c1 = next(c for c in D["caminos"] if c["id"] == "C1")
    tramos = [((zs[0], zs[2]), (c1["x0"] * 1000, zs[2])), ((c1["x1"] * 1000, zs[2]), (zs[1], zs[2])),
              ((zs[1], zs[2]), (zs[1], zs[3])), ((zs[1], zs[3]), (zs[0], zs[3])), ((zs[0], zs[3]), (zs[0], zs[2]))]
    for (pa, pb) in tramos:
        pa, pb = np.array(pa), np.array(pb)
        Lt = np.linalg.norm(pb - pa)
        u = (pb - pa) / Lt
        for t in np.arange(0, Lt + 1, 3000):
            p = pa + u * min(t, Lt)
            e.add(k_poste, "galv", T(p[0], p[1], 0), "CERCO-INT", "")
        e.caja_rot(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, 900), (Lt, 6, 1600), math.degrees(math.atan2(u[1], u[0])),
                   "malla", "CERCO-INT", "Cerco sanitario interno de la zona sucia (planta de secado)")
    e.caja(c1["x0"] * 1000, zs[2] - 60, 0, c1["x1"] * 1000, zs[2] + 60, 1500, "amarillo", "CERCO-INT",
           "Tranquera de la zona sucia con rodiluvio")


def servicios(e):
    e.en("Predio - servicios")
    for s in D["servicios"]:
        if s["id"] == "TQ-AGUA":
            x, y, R, h = s["x"] * 1000, s["y"] * 1000, s["D"] * 500, s["h"] * 1000
            e.tubo((x, y, 0), (x, y, h), R, R - 6, "galv", cod=s["id"], nom="Tanque australiano de agua 150 m³")
            e.cil((x, y, 0), (x, y, h - 300), R - 10, "agua", cod=s["id"], nom="")
            e.caja(x - R - 200, y - 2000, 0, x - R + 600, y + 2000, 2400, "revoque", s["id"], "Casilla de bombeo y cloración")
        elif s["id"] == "TQ-EF":
            x, y, R, h = s["x"] * 1000, s["y"] * 1000, s["D"] * 500, s["h"] * 1000
            e.cil((x, y, -1200), (x, y, h - 1200), R, "plastico_gris", cod=s["id"],
                  nom="Tanque de efluentes 15 m³ (lavado y lixiviados; retira un camión atmosférico)")
            e.cil((x, y, h - 1200), (x, y, h - 1100), 350, "negro", cod=s["id"], nom="Boca de inspección y succión")
        elif s["id"] == "MORT":
            x0, x1, y0, y1 = s["x0"] * 1000, s["x1"] * 1000, s["y0"] * 1000, s["y1"] * 1000
            e.caja(x0, y0, -100, x1, y1, 0, "hormigon", s["id"], "Platea de la compostera de mortandad")
            for k in range(4):
                xx = x0 + (x1 - x0) * k / 3
                e.caja(xx - 100, y0, 0, xx + 100, y1, 1500, "hormigon", s["id"], "Tabique de las celdas de compostaje")
            e.caja(x0, y1 - 200, 0, x1, y1, 1500, "hormigon", s["id"], "")
            e.caja(x0 - 300, y0 - 300, 2600, x1 + 300, y1 + 300, 2700, "chapa_techo", s["id"], "Techo de la compostera")
            for (xx, yy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                e.barra((xx, yy, 0), (xx, yy, 2600), "RHS 80", "estructura", cod=s["id"], nom="Columna del techo")
    # subestación transformadora (afuera del cerco)
    st = D["acceso"]["set"]
    x0, x1, y0, y1 = (st[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
    e.en("Predio - subestación")
    e.caja(x0, y0, -100, x1, y1, 0, "ripio", "SET", "Playa de la subestación con piedra partida")
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    e.caja(xc - 1800, yc - 800, 0, xc - 300, yc + 800, 400, "hormigon", "SET", "Base del transformador")
    e.caja(xc - 1700, yc - 650, 400, xc - 400, yc + 650, 2200, "gris_motor", "SET", "Transformador 13,2/0,4 kV 315 kVA (preliminar)")
    for k in range(3):
        e.cil((xc - 1500 + 400 * k, yc, 2200), (xc - 1500 + 400 * k, yc, 2700), 60, "plastico_blanco", cod="SET", nom="Aislador de MT")
    C.tablero(e, xc + 600, yc - 400, 0, 1600, 2000, 600, rotz=0, tag="TGBT", nombre="Tablero general de baja tensión TGBT (preliminar)")
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        a, b = np.array(a), np.array(b)
        Lt = np.linalg.norm(b - a)
        e.caja_rot(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 1100), (Lt, 6, 2200), math.degrees(math.atan2(*(b - a)[::-1])),
                   "malla", "SET", "Cerco de la subestación")
    for k, xx in enumerate((x0 - 6000, x0 - 26000)):
        e.cil((xx, y0 - 3000, 0), (xx, y0 - 3000, 10000), 150, "hormigon", cod="LMT", nom="Poste de H° de la línea de 13,2 kV")
        e.barra((xx - 1000, y0 - 3000, 9500), (xx + 1000, y0 - 3000, 9500), "L 63", "galv", cod="LMT", nom="Ménsula")
    e.cil((x0 - 26000, y0 - 3000, 9550), (x0 - 6000, y0 - 3000, 9550), 8, "cobre", cod="LMT", nom="Línea aérea de MT")


def forestacion(e):
    """Cortina forestal (casuarinas) 8 m adentro del cerco, salvo en el frente del acceso."""
    e.en("Predio - forestación")
    pr = D["predio"]
    x0, x1, y0, y1 = (pr[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
    k_tronco = proto(("arbol_tronco",), lambda: wp().circle(180).extrude(3500))
    k_copa = proto(("arbol_copa",), lambda: wp().circle(2200).workplane(offset=8000).circle(300).loft())
    pts = []
    for x in np.arange(x0 + 8000, x1 - 7000, 7000):
        pts.append((x, y1 - 8000))
    for y in np.arange(y0 + 30000, y1 - 7000, 7000):
        pts += [(x0 + 8000, y), (x1 - 8000, y)]
    for (x, y) in pts:
        e.add(k_tronco, "tronco", T(x, y, 0), "ARB", "Casuarina (cortina forestal)")
        e.add(k_copa, "follaje", T(x, y, 2500), "ARB", "")


def alumbrado(e):
    e.en("Predio - alumbrado exterior")
    k_col = proto(("columna_luz",), lambda: wp().circle(70).extrude(9000))
    k_braz = proto(("brazo_luz",), lambda: wp().rect(1200, 60).extrude(60).translate((600, 0, 0)))
    for c in D["caminos"]:
        horiz = (c["x1"] - c["x0"]) > (c["y1"] - c["y0"])
        L = (c["x1"] - c["x0"]) if horiz else (c["y1"] - c["y0"])
        for t in np.arange(10, L, 30):
            if horiz:
                x, y, rz = (c["x0"] + t) * 1000, c["y0"] * 1000 - 600, 90
            else:
                x, y, rz = c["x0"] * 1000 - 600, (c["y0"] + t) * 1000, 0
            e.add(k_col, "galv", T(x, y, 0), "ALU", "Columna de alumbrado 9 m con LED 120 W" if t == 10 else "")
            e.add(k_braz, "galv", T(x, y, 8900) @ Rz(rz), "ALU", "")
            e.caja_rot((x + (0 if horiz else 1150), y + (1150 if horiz else 0), 8850), (500, 250, 80), 0, "luz", "ALU", "")


def ampliacion(e):
    """Lugares reservados para G0 y G5 (replanteo pintado en el terreno)."""
    e.en("Predio - ampliación futura")
    g1 = D["galpones"][0]
    for a in D["ampliacion"]:
        x = a["x"] * 1000
        x0, x1 = x - D["galpon"]["A"] * 500, x + D["galpon"]["A"] * 500
        y0, y1 = g1["y0"] * 1000, g1["y1"] * 1000
        for (pa, pb) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            e.caja(min(pa[0], pb[0]) - 75, min(pa[1], pb[1]) - 75, -10, max(pa[0], pb[0]) + 75, max(pa[1], pb[1]) + 75, 5,
                   "amarillo", "AMP", f"Replanteo del {a['id']}")


def construir(e):
    terreno(e)
    caminos(e)
    cerco(e)
    servicios(e)
    forestacion(e)
    alumbrado(e)
    ampliacion(e)
