"""P18 - Aire: recirculación, compuertas y ventilación de la recepción.

A: esquema del circuito de aire y humos con recirculación (S/E).
B: retorno de recirculación D7, mirando al Norte (1:100).
C: campana de recepción, extractor M23 y biofiltro E3, mirando al Oeste (1:150).
Geometría: layout_planta.json (G.ciclon, G.scrubber, G.ducto_lavador, G.anexo, G.pila_guano) y los
bloques D7 / E3 de la Rev. D en visor.html (recorrido del retorno, cámara de mezcla, campana, biofiltro).
"""
import json
import math
import os


from lamina_secadora import (fuente_pil, COL, circulo, exportar_lamina, factor, flecha, lamina, linea, poli, rayado,
                             rect, relleno, relleno_circulo, relleno_rect, subtitulo, t, tabla, tn)
from lamina_a3 import cota

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

K100, K150 = factor("1:100"), factor("1:150")
M100, M150 = K100 * 1000, K150 * 1000

NARANJA, ROJO, VERDE, GRIS = COL["recirc"], COL["aire_caliente"], COL["aire_agotado"], COL["humos"]
NAR_CL = (242, 200, 160)
GRIS_OSC = (85, 85, 85)

# ---------------------------------------------------------------- helpers propios de la lámina
def ancho_texto(texto, h, negrita=True):
    return fuente_pil(negrita).getlength(texto) / 1000.0 * h / 0.716


def trazos(msp, pts, capa="OCULTAS", color=None, lw=None, largo=1.6, hueco=0.9):
    """Línea de trazos explícita (el PDF no aplica tipos de línea): cada trazo es una LINE."""
    resto, dibujar = largo, True
    for a, b in zip(pts[:-1], pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d == 0:
            continue
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        s0 = 0.0
        while s0 < d:
            s1 = min(d, s0 + resto)
            if dibujar:
                linea(msp, (a[0] + ux * s0, a[1] + uy * s0), (a[0] + ux * s1, a[1] + uy * s1), capa, color, lw)
            resto -= s1 - s0
            s0 = s1
            if resto <= 1e-9:
                dibujar = not dibujar
                resto = largo if dibujar else hueco


def circulo_trazos(msp, c, r, capa="OCULTAS", n=24):
    for i in range(n):
        if i % 2 == 0:
            msp.add_arc(c, r, i * 360 / n, (i + 1) * 360 / n, dxfattribs={"layer": capa})


def rotulo(msp, texto, pos, h, alin="MIDDLE_LEFT", negrita=False, color=None):
    """Texto con fondo blanco (relleno) para que no lo crucen líneas."""
    w = ancho_texto(texto, h, negrita)
    x, y = pos
    x0 = x - (w / 2 if "CENTER" in alin else w if "RIGHT" in alin else 0)
    y0 = y - (h / 2 if "MIDDLE" in alin else h if "TOP" in alin else 0)
    relleno_rect(msp, x0 - 0.5, y0 - 0.5, x0 + w + 0.5, y0 + h + 0.5, (255, 255, 255))
    (tn if negrita else t)(msp, texto, pos, h, alin, color=color)


def titulo(msp, texto, x, y, h=3.5):
    tn(msp, texto, (x, y), h, "BOTTOM_LEFT")
    largo = ancho_texto(texto, h)
    linea(msp, (x, y - 1.0), (x + largo, y - 1.0), "CONTORNO")
    linea(msp, (x, y - 1.8), (x + largo, y - 1.8), "FINO")


def rect_redondeado(msp, x0, y0, x1, y1, r=1.0, fill=None, lw=50):
    """Caja del esquema con esquinas redondeadas (polilínea con bulge)."""
    b = math.tan(math.radians(90) / 4)
    pts = [(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b), (x1 - r, y1, 0),
           (x0 + r, y1, b), (x0, y1 - r, 0), (x0, y0 + r, b)]
    if fill:
        relleno(msp, [(x0 + r * 0.3, y0), (x1 - r * 0.3, y0), (x1, y0 + r * 0.3), (x1, y1 - r * 0.3),
                      (x1 - r * 0.3, y1), (x0 + r * 0.3, y1), (x0, y1 - r * 0.3), (x0, y0 + r * 0.3)], fill)
    e = msp.add_lwpolyline(pts, format="xyb", close=True, dxfattribs={"layer": "CONTORNO"})
    e.dxf.lineweight = lw
    return e


def valvula(msp, x, y, vertical=True):
    """Compuerta (mariposa) en el esquema: círculo chico con el eje de la hoja."""
    if vertical:
        linea(msp, (x, y - 2.2), (x, y + 2.2), "CONTORNO", lw=70)
    else:
        linea(msp, (x - 2.2, y), (x + 2.2, y), "CONTORNO", lw=70)
    relleno_circulo(msp, (x, y), 0.8, (255, 255, 255))
    circulo(msp, (x, y), 0.8, "CONTORNO", lw=35)


def actuador(msp, x, y, tag, h=1.8, desde=None):
    relleno_rect(msp, x, y, x + 2.5, y + 1.8, (215, 225, 240))
    rect(msp, x, y, x + 2.5, y + 1.8, "CONTORNO", lw=35)
    if desde:
        trazos(msp, [desde, (x, y)], largo=0.6, hueco=0.4)
    tn(msp, tag, (x + 3.0, y + 0.9), h, "MIDDLE_LEFT")


def banda(msp, pts, ancho, fill, borde=None):
    """Conducto dibujado como banda de ancho constante a lo largo de una polilínea ortogonal."""
    for a, b in zip(pts[:-1], pts[1:]):
        if abs(a[0] - b[0]) < 1e-6:
            x0, x1 = a[0] - ancho / 2, a[0] + ancho / 2
            y0, y1 = min(a[1], b[1]) - ancho / 2, max(a[1], b[1]) + ancho / 2
        else:
            y0, y1 = a[1] - ancho / 2, a[1] + ancho / 2
            x0, x1 = min(a[0], b[0]) - ancho / 2, max(a[0], b[0]) + ancho / 2
        relleno_rect(msp, x0, y0, x1, y1, fill)
    if borde:
        poli(msp, pts, "CONTORNO", color=borde, lw=35)


# ---------------------------------------------------------------- A - esquema
XS = [24.1, 57.1, 90.1, 123.1, 156.0, 189.0]
AW = 28.8
F1, F2, F3 = (251.2, 260.9), (225.2, 234.8), (203.1, 212.8)


def caja_esq(msp, col, fila, tit, sub, fill=None):
    x0 = XS[col]
    rect_redondeado(msp, x0, fila[0], x0 + AW, fila[1], 1.0, fill)
    ym = (fila[0] + fila[1]) / 2
    tn(msp, tit, (x0 + AW / 2, ym + 1.3), min(2.0, (AW - 1.6) / ancho_texto(tit, 1.0)), "MIDDLE_CENTER")
    t(msp, sub, (x0 + AW / 2, ym - 1.6), min(1.8, (AW - 1.6) / ancho_texto(sub, 1.0, False)), "MIDDLE_CENTER")


def esquema(msp):
    blanco, rosa, verde, gris = None, (253, 235, 235), (232, 243, 234), (236, 236, 236)
    fila1 = [("Aire ambiente", "18 °C · 8 g/kg", blanco), ("Cámara de mezcla", "CD-02 aire fresco", blanco),
             ("Ventiladores M1-M2", "2 × 15.400 m³/h", blanco), ("Intercambiador", "91 m² · 114 tubos", rosa),
             ("Ducto caliente", "CD-01 · TT-01", rosa), ("Secador 3 pisos", "plenum PT-01", blanco)]
    fila2 = [("Chimenea 10 m", "toma isocinética"), ("Extractor M3", "22 kW · VFD"), ("Lavador pH 3", "AT-01 · LS-03"),
             ("Ciclón Ø1800", "válvula rotativa"), ("Campana 800×800", "CD-04 · T/P")]
    fila3 = [("Cáscara 314 kg/h", "silo 70 m³"), ("Hogar 882 kW", "BE-01 · TT-06 · PS-01"),
             ("Tubos intercambiador", "850 → 200 °C"), ("Ciclón de humos", "cenizas"), ("Chimenea 12 m", "TT-07 · 2 tomas")]
    for i, (a, b, f) in enumerate(fila1):
        caja_esq(msp, i, F1, a, b, f)
    for i, (a, b) in enumerate(fila2):
        caja_esq(msp, i, F2, a, b, verde)
    for i, (a, b) in enumerate(fila3):
        caja_esq(msp, i, F3, a, b, gris)
    ym1, ym2, ym3 = sum(F1) / 2, sum(F2) / 2, sum(F3) / 2
    for i in range(5):
        col = (60, 60, 60) if i < 3 else ROJO
        flecha(msp, (XS[i] + AW, ym1), (XS[i + 1], ym1), "CONTORNO", color=col, tam=1.8, lw=50)
    for i in range(4):
        flecha(msp, (XS[i + 1], ym2), (XS[i] + AW, ym2), "CONTORNO", color=VERDE, tam=1.8, lw=50)
        flecha(msp, (XS[i] + AW, ym3), (XS[i + 1], ym3), "CONTORNO", color=GRIS, tam=1.8, lw=50)
    # aire agotado del secador a la campana (65 °C)
    flecha(msp, (XS[5] + AW / 2, F1[0]), (XS[4] + AW - 1.5, F2[1]), "CONTORNO", color=VERDE, tam=1.8, lw=50)
    tn(msp, "33-37 °C", (207.5, 243.7), 1.9, "MIDDLE_CENTER", color=VERDE)
    # calor a través de los tubos (línea de trazos entre humos e intercambiador)
    trazos(msp, [(XS[2] + AW / 2, F3[1]), (XS[3] + AW / 2, F1[0])], color=GRIS)
    t(msp, "calor a través de los tubos", (138.2, 216.6), 1.8, "MIDDLE_CENTER", color=(110, 110, 110))
    # recirculación 25 % desde la salida del ciclón a la cámara de mezcla
    xr0, xr1, yr = XS[3] + AW / 2, XS[1] + AW / 2, 241.1
    poli(msp, [(xr0, F2[1]), (xr0, yr), (xr1, yr)], "CONTORNO", color=NARANJA, lw=100)
    flecha(msp, (xr1, yr), (xr1, F1[0]), "CONTORNO", color=NARANJA, tam=2.2, lw=100)
    rotulo(msp, "RECIRCULACIÓN CD-03 · Ø500 · normalmente cerrada", (117.6, yr - 1.4), 1.8, "TOP_RIGHT", negrita=True, color=NARANJA)
    valvula(msp, 119.5, yr)
    actuador(msp, 121.2, 243.2, "CD-03", desde=(120.1, yr + 0.6))
    # by-pass de humos CD-05: hogar -> chimenea
    xb0, xb1, yb = XS[1] + AW / 2, XS[4] + AW / 2, 198.1
    trazos(msp, [(xb0, F3[0]), (xb0, yb), (xb1, yb)], color=GRIS, lw=70)
    flecha(msp, (xb1, yb), (xb1, F3[0]), "CONTORNO", color=GRIS, tam=1.8, lw=70)
    valvula(msp, 100.0, yb)
    actuador(msp, 101.2, 199.6, "CD-05 by-pass de humos (servomotor)", h=1.8, desde=(100.6, yb + 0.6))


# ---------------------------------------------------------------- B - retorno de recirculación, 1:100
def RB(x, z):
    return (265.2 + (x - 14.5) * M100, 178.9 + z * M100)


def vista_b(msp):
    cy, sc = G["ciclon"], G["scrubber"]
    # terreno
    linea(msp, RB(12.1, 0), RB(22.1, 0), "CONTORNO", lw=70)
    for i in range(26):
        x0 = RB(12.2, 0)[0] + i * 3.8
        linea(msp, (x0, 178.9), (x0 - 1.0, 177.6), "FINO")
    # pórtico de apoyo del retorno (gris)
    poli(msp, [RB(15.2, 0), RB(15.2, 7.8), RB(19.05, 7.8), RB(19.05, 0)], "CONTORNO", color=GRIS_OSC, lw=50)
    # ducto ciclón -> lavador (verde)
    dl = [RB(13.8, 7.5), RB(15.8, 7.5), RB(15.8, 1.0), RB(16.2, 1.0)]
    banda(msp, dl, 2.2, (184, 212, 194), borde=VERDE)
    # retorno Ø500 (naranja): salida del ciclón -> CD-03 -> cámara de mezcla
    rc = [RB(15.2, 7.5), RB(15.2, 8.05), RB(19.9, 8.05), RB(19.9, 2.45)]
    banda(msp, rc, 0.5 * M100, NAR_CL)
    poli(msp, rc, "CONTORNO", color=NARANJA, lw=35)
    # ciclón
    r = cy["D"] / 2
    cuerpo = [RB(cy["x"] - r, cy["z_cil1"]), RB(cy["x"] + r, cy["z_cil1"]), RB(cy["x"] + r, cy["z_cil0"]),
              RB(cy["x"] + 0.2, cy["z_cono0"]), RB(cy["x"] - 0.2, cy["z_cono0"]), RB(cy["x"] - r, cy["z_cil0"])]
    relleno(msp, cuerpo, (236, 240, 241))
    poli(msp, cuerpo, "CONTORNO", cerrada=True, lw=50)
    rect(msp, *RB(cy["x"] - 0.2, 1.1), *RB(cy["x"] + 0.2, cy["z_cono0"]), "CONTORNO", lw=35)
    relleno_rect(msp, *RB(cy["x"] - 0.2, 1.1), *RB(cy["x"] + 0.2, cy["z_cono0"]), (200, 200, 200))
    poli(msp, [RB(cy["x"] - 0.4, cy["z_cil1"]), RB(cy["x"] - 0.4, 7.5), RB(cy["x"], 7.5)], "CONTORNO", lw=35)
    linea(msp, RB(cy["x"] + 0.4, cy["z_cil1"]), RB(cy["x"] + 0.4, 7.45), "CONTORNO", lw=35)
    tn(msp, "ciclón", RB(cy["x"], 5.25), 1.9, "MIDDLE_CENTER")
    # lavador con relleno (zona hachurada)
    rs = sc["D"] / 2
    relleno_rect(msp, *RB(sc["x"] - rs, sc["z0"]), *RB(sc["x"] + rs, sc["z1"]), (230, 238, 226))
    rect(msp, *RB(sc["x"] - rs, sc["z0"]), *RB(sc["x"] + rs, sc["z1"]), "CONTORNO", lw=50)
    poli(msp, [RB(sc["x"] - rs, sc["z1"]), RB(sc["x"] - 0.39, 6.7), RB(sc["x"] + 0.39, 6.7), RB(sc["x"] + rs, sc["z1"])],
         "CONTORNO", lw=50)
    p, q = RB(sc["x"] - rs + 0.05, 2.31), RB(sc["x"] + rs - 0.05, 4.41)
    rayado(msp, [p, (q[0], p[1]), q, (p[0], q[1])], escala=0.15, color=(120, 180, 120))
    rect(msp, p[0], p[1], q[0], q[1], "FINO")
    tn(msp, "lavador", RB(sc["x"], 5.25), 1.9, "MIDDLE_CENTER")
    # cámara de mezcla con persianas de aire fresco CD-02
    a, b = RB(19.55, 0.45), RB(20.2, 2.45)
    relleno_rect(msp, a[0], a[1], b[0], b[1], (245, 218, 190))
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=50)
    for k in range(7):
        z = 0.6 + k * 0.27
        linea(msp, RB(19.55, z + 0.12), RB(19.4, z), "CONTORNO", lw=35)
    rotulo(msp, "CD-02", (310.2, 190.6), 1.8, "MIDDLE_CENTER", negrita=True)
    # ménsulas al muro del anexo, CD-03 y flechas de sentido
    for z in (6.2, 4.4):
        linea(msp, RB(19.9, z), RB(20.3, z), "CONTORNO", color=GRIS_OSC, lw=70)
    c = RB(19.9, 5.47)
    linea(msp, (c[0] - 2.4, c[1]), (c[0] + 2.4, c[1]), "CONTORNO", lw=70)
    relleno_circulo(msp, c, 0.6, (255, 255, 255))
    circulo(msp, c, 0.6, "CONTORNO", lw=35)
    actuador(msp, c[0] + 1.2, c[1] + 1.6, "CD-03", desde=(c[0] + 0.4, c[1] + 0.5))
    flecha(msp, RB(16.95, 8.46), RB(18.7, 8.46), "CONTORNO", color=NARANJA, tam=1.8, lw=50)
    flecha(msp, RB(20.6, 6.94), RB(20.6, 5.87), "CONTORNO", color=NARANJA, tam=1.8, lw=50)
    # sensor de temperatura del retorno (TT REC)
    c = RB(19.2, 4.8)
    relleno_circulo(msp, c, 3.0, (255, 255, 255))
    circulo(msp, c, 3.0, "CONTORNO", lw=35)
    linea(msp, (c[0] - 3.0, c[1]), (c[0] + 3.0, c[1]), "FINO")
    tn(msp, "TT", (c[0], c[1] + 1.4), 1.6, "MIDDLE_CENTER")
    t(msp, "REC", (c[0], c[1] - 1.3), 1.4, "MIDDLE_CENTER")
    # muro O del anexo y losa
    a, b = RB(20.3, 0), RB(20.5, 4.8)
    pts = [a, (b[0], a[1]), b, (a[0], b[1])]
    relleno(msp, pts, (255, 255, 255))
    rayado(msp, pts, escala=0.12, color=(190, 90, 70))
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=50)
    relleno_rect(msp, *RB(20.3, 4.8), *RB(22.0, 4.95), (200, 200, 200))
    rect(msp, *RB(20.3, 4.8), *RB(22.0, 4.95), "CONTORNO", lw=50)
    tn(msp, "anexo", RB(21.45, 3.36), 1.8, "MIDDLE_CENTER")
    # ventilador M1 (oculto, detrás del muro)
    c = RB(G["anexo"]["ventiladores"][0]["x"], 0.74)
    circulo_trazos(msp, c, 0.63 * M100)
    # cotas
    cota(msp, (244.2, 178.9), (244.2, RB(0, 7.5)[1]), distancia=0, escala=K100, valor="7.500")
    linea(msp, (239.5, RB(0, 7.5)[1]), (245.5, RB(0, 7.5)[1]), "FINO")
    cota(msp, (336.2, 178.9), (336.2, RB(0, 8.05)[1]), distancia=0, escala=K100, valor="8.050")
    linea(msp, (337.5, RB(0, 8.05)[1]), (341.0, RB(0, 8.05)[1]), "FINO")


# ---------------------------------------------------------------- C - campana y biofiltro, 1:150
def RC(y, z):
    """Mirando al Oeste: el Norte queda a la derecha."""
    return (289.5 + (y - 18.0) * M150, 91.0 + z * M150)


def vista_c(msp):
    pg = G["pila_guano"]
    linea(msp, (236.1, 91.0), (342.9, 91.0), "CONTORNO", lw=70)
    for i in range(29):
        x0 = 237.0 + i * 3.7
        linea(msp, (x0, 91.0), (x0 - 1.0, 89.7), "FINO")
    # cubierta y muro N
    linea(msp, (236.1, RC(0, 7.0)[1]), RC(18.1, 7.0), "CONTORNO", lw=70)
    linea(msp, RC(18.0, 0), RC(18.0, 7.0), "CONTORNO", lw=100)
    tn(msp, "muro N", (291.5, 141.5), 1.8, "MIDDLE_CENTER")
    # pila de guano
    pila = [RC(pg["y"] - pg["r"], 0), RC(pg["y"], pg["h"] - 0.02), RC(pg["y"] + pg["r"], 0)]
    relleno(msp, pila, (200, 170, 125))
    poli(msp, pila, "CONTORNO", cerrada=True, lw=50)
    # caja del camión volcando (máx. 5,4 m)
    trazos(msp, [RC(12.4, 0.6), RC(13.2, 5.4), RC(15.8, 5.4)], color=(190, 100, 40), lw=35)
    t(msp, "caja del camión\nvolcando (máx. 5,4 m)", (231.0, 120.0), 1.8, "TOP_LEFT", color=(190, 100, 40))
    # campana (pirámide truncada 4,8 × 4,3 m) y ducto Ø600 al extractor M23
    camp = [RC(12.6, 5.95), RC(pg["y"] - 0.35, 6.5), RC(pg["y"] + 0.35, 6.5), RC(16.9, 5.95)]
    relleno(msp, camp, (225, 228, 230))
    poli(msp, camp, "CONTORNO", cerrada=True, lw=70)
    ducto = [RC(pg["y"], 6.5), RC(pg["y"], 6.72), RC(18.9, 6.72), RC(18.9, 1.6)]
    banda(msp, ducto, 1.5, (160, 166, 170))
    linea(msp, RC(18.0, 0), RC(18.0, 7.0), "CONTORNO", lw=100)
    tn(msp, "campana 4,8 × 4,3 m", (268.1, 140.8), 1.8, "MIDDLE_CENTER")
    flecha(msp, RC(pg["y"], 4.75), RC(pg["y"], 5.75), "CONTORNO", color=VERDE, tam=1.8, lw=50)
    # extractor M23 y biofiltro
    c = RC(19.4, 0.9)
    circulo(msp, c, 0.55 * M150, "CONTORNO", lw=50)
    tn(msp, "M23", (300.1, 105.4), 1.8, "MIDDLE_CENTER")
    a, b = RC(20.2, 0), RC(24.7, 1.5)
    relleno_rect(msp, a[0], a[1], b[0], b[1], (200, 165, 120))
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=70)
    p, q = RC(20.5, 0.2), RC(24.4, 1.38)
    rayado(msp, [p, (q[0], p[1]), q, (p[0], q[1])], escala=0.15, color=(120, 90, 60))
    rect(msp, p[0], p[1], q[0], q[1], "FINO")
    flecha(msp, RC(22.45, 1.6), RC(22.45, 2.6), "CONTORNO", color=VERDE, tam=1.8, lw=50)
    tn(msp, "biofiltro 38 m²", (319.2, 112.8), 1.8, "MIDDLE_CENTER")
    # cota de la campana
    cota(msp, (286.2, 91.0), (286.2, RC(0, 5.95)[1]), distancia=0, escala=K150, valor="5.950")
    linea(msp, RC(16.9, 5.95), (287.5, RC(0, 5.95)[1]), "FINO")


def main():
    revs = [("D", "09/2026", "Emisión orig.: ítems 6-8 y 24; campana recepción, biofiltro, extractores eólicos"),
            ("E", "11/2026", "Estudio térmico: CD-03 por HR de la cámara de mezcla; balance del modelo")]
    assert all(len(r[2]) <= 80 for r in revs)
    doc, msp, z = lamina(18, "AIRE: RECIRCULACIÓN, COMPUERTAS\nY VENTILACIÓN DE RECEPCIÓN", "1:100 · S/E", revs)
    titulo(msp, "A - ESQUEMA DEL CIRCUITO DE AIRE Y HUMOS CON RECIRCULACIÓN - S/E", 26.0, 278.3, 3.4)
    esquema(msp)
    # balance con y sin recirculación
    subtitulo(msp, "CON Y SIN RECIRCULACIÓN: aire ajustado al 15 % (modelo térmico)", 24.1, 189.2, 2.4)
    tabla(msp, 24.1, 188.0, [51.9, 42.2, 49.8], [
        ["Punto (1.000 kg/h al 72 %)", "CD-03 cerrada", "CD-03 al 25 %"],
        ["Aire a los ventiladores", "18,0 °C · 7,8 g/kg", "23,0 °C · 16,2 g/kg · HR 91 %"],
        ["Entrada al secador", "99,5 °C", "102,2 °C"],
        ["Salida del secador", "33,3 °C · 33,0 g/kg", "37,1 °C · 41,4 g/kg"],
        ["Calor del generador", "617 kW", "610 kW"],
        ["Cáscara a 18 °C · julio · enero", "219 · 228 · 193 kg/h", "−1,2 % · −1,9 % · +1,1 %"],
        ["Escape (HR)", "99 %: casi saturado", "99 %: casi saturado"],
    ], h_fila=3.4, altura=1.8)
    subtitulo(msp, "COMPUERTAS (señal 0-10 V desde el PLC)", 24.1, 152.4, 2.4)
    tabla(msp, 24.1, 151.1, [13.1, 59.6, 24.2, 51.0], [
        ["Tag", "Ubicación", "Actuador", "Posición / función"],
        ["CD-01", "entrada de aire caliente (ducto vertical)", "eléctrico 24 V", "regula el caudal al plenum"],
        ["CD-02", "cámara de mezcla, aire fresco", "eléctrico 24 V", "abre si CD-03 cierra"],
        ["CD-03", "retorno de recirculación Ø500", "eléctrico 24 V", "cerrada; abre 0-35 % si HR < 90 %"],
        ["CD-04", "salida del secador (ducto agotado)", "eléctrico 24 V", "balance de depresión"],
        ["CD-05", "by-pass de humos hogar → chimenea", "servomotor", "abre ante falla o > 950 °C"],
    ], h_fila=3.33, altura=1.8)
    subtitulo(msp, "PUNTOS DE MEDICIÓN (ítem 6)", 24.1, 124.4, 2.4)
    tabla(msp, 24.1, 123.1, [62.0, 30.2, 55.7], [
        ["Punto de medición", "Toma", "Uso"],
        ["Entrada de aire caliente (ducto vertical)", "2 × 1/2\" (T y P)", "verificar TT-01 y caudal"],
        ["Salida del secador (ducto agotado)", "2 × 1/2\"", "T, humedad y depresión"],
        ["Plenum inferior (cara Norte)", "1 × 1/2\"", "contraste de PT-01"],
        ["Ducto al lavador / retorno de recirculación", "1 + 1", "caudal recirculado (Pitot)"],
        ["Chimenea de humos a +8,35 m (plataforma)", "2 a 90° Ø100", "muestreo isocinético"],
        ["Chimenea del lavador", "1 × Ø100", "NH3 y olores a la salida"],
    ], h_fila=3.3, altura=1.8)
    for k, r in enumerate([
        "Ventilación de la nave: 6 extractores eólicos Ø600 en la cumbrera + lucernario y portones.",
        "Recepción: extractor M23 6.000 m³/h → biofiltro 38,2 m², carga 157 m³/m²·h, contacto 28 s.",
        "Puntos de medición: boquillas 1/2\" con tapón en entrada (2), salida (2), plenum, ducto al lavador, "
        "retorno y chimeneas.",
    ]):
        t(msp, r, (24.1, 70.6 - k * 2.9), 1.8, "MIDDLE_LEFT")
    titulo(msp, "B - RETORNO DE RECIRCULACIÓN (mirando al Norte) - ESC. 1:100", 232.2, 278.3, 2.7)
    vista_b(msp)
    titulo(msp, "C - CAMPANA DE RECEPCIÓN Y BIOFILTRO (mirando al Oeste) - ESC. 1:150", 232.2, 165.2, 2.7)
    vista_c(msp)
    exportar_lamina(doc, 18)


if __name__ == "__main__":
    main()
