"""P17 - Nave y equipos: seguridad, accesos y mantenimiento (agregados Rev. D), esc. 1:150.

Redibujo vectorial de la lámina Rev. D más el ítem 16 (Rev. E): puesta a tierra, barra
equipotencial principal y pararrayos. Geometría en metros de fuente/datos/layout_planta.json
(clave G) y posiciones del código Rev. D del visor (visor.html, ítems D1 a D22 y D16).
"""
import json
import math
import os

from lamina_secadora import (COL, FECHA, circulo, escala_grafica, exportar_lamina, factor, lamina,
                             linea, norte, poli, rayado, rect, relleno, relleno_circulo, relleno_rect,
                             subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

S = factor("1:150") * 1000.0          # mm de papel por metro
OX, OY = 34.0, 94.9                   # vértice SO de la nave en el papel

AMARILLO = (243, 194, 41)
ORO = (190, 150, 20)
AZUL = (31, 95, 168)
CELESTE = (60, 150, 200)
GRIS_EX = (136, 136, 136)
GRIS_NU = (51, 51, 51)
ROJO_PE = (215, 38, 30)
COBRE = (184, 100, 40)
CREMA = (255, 243, 214)


def P(x, y):
    return (OX + x * S, OY + y * S)


def R(x0, y0, x1, y1):
    return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]


def trazos(doc):
    """Tipos de línea de trazos en mm de papel (la plantilla trae DASHED en pulgadas y $LTSCALE 0,5:
    los patrones se definen al doble)."""
    for nombre, (a, b) in {"TR_BAND": (2.2, 1.0), "TR_FINO": (1.2, 0.7), "TR_PAT": (2.8, 0.8)}.items():
        if nombre not in doc.linetypes:
            doc.linetypes.add(nombre, pattern=[2 * (a + b), 2 * a, -2 * b], description=nombre)


def caja(msp, x0, y0, x1, y1, rgb, lw=35, capa="CONTORNO", tipo=None):
    relleno(msp, R(x0, y0, x1, y1), rgb)
    rect(msp, *P(x0, y0), *P(x1, y1), capa, lw=lw, tipo=tipo)


def disco(msp, x, y, r, rgb, lw=35):
    relleno_circulo(msp, P(x, y), r * S, rgb)
    circulo(msp, P(x, y), r * S, "CONTORNO", lw=lw)


def sector_anillo(cx, cy, r0, r1, a0, a1, n=24):
    ext = [P(cx + r1 * math.cos(a0 + (a1 - a0) * i / n), cy + r1 * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inn = [P(cx + r0 * math.cos(a1 - (a1 - a0) * i / n), cy + r0 * math.sin(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
    return ext + inn


def plataforma(msp, pts):
    relleno(msp, pts, (246, 236, 200))
    rayado(msp, pts, escala=0.35, angulo=-45, color=ORO)
    poli(msp, pts, "CONTORNO", cerrada=True, color=ORO, lw=35)


# ------------------------------------------------------------------ símbolos (mm de papel)

def registro(msp, c, r=0.95):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "FINO", lw=25)
    tn(msp, "R", c, 1.2, "MIDDLE_CENTER")


def escalera(msp, c, r=1.0):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "FINO", color=ORO, lw=25)
    t(msp, "E", c, 1.1, "MIDDLE_CENTER", color=ORO)


def lubric(msp, c):
    relleno_rect(msp, c[0] - 1.1, c[1] - 0.75, c[0] + 1.1, c[1] + 0.75, (255, 255, 255))
    rect(msp, c[0] - 1.1, c[1] - 0.75, c[0] + 1.1, c[1] + 0.75, "FINO", lw=25)
    tn(msp, "L", c, 1.1, "MIDDLE_CENTER")


def tapa(msp, c, a=0.8):
    relleno_rect(msp, c[0] - a / 2, c[1] - a / 2, c[0] + a / 2, c[1] + a / 2, (201, 164, 0), capa="CONTORNO")


def parada(msp, c, tag=None, lado="R"):
    a = 1.15
    relleno_rect(msp, c[0] - a, c[1] - a, c[0] + a, c[1] + a, (232, 185, 35))
    rect(msp, c[0] - a, c[1] - a, c[0] + a, c[1] + a, "FINO", lw=25)
    relleno_circulo(msp, c, 0.75, ROJO_PE, capa="CONTORNO")
    circulo(msp, c, 0.75, "FINO")
    if tag:
        if lado == "R":
            tn(msp, tag, (c[0] + 1.7, c[1]), 1.8, "MIDDLE_LEFT")
        else:
            tn(msp, tag, (c[0] - 1.7, c[1]), 1.8, "MIDDLE_RIGHT")


def advertencia(msp, c, lado=2.6):
    x, y = c
    h = lado * 0.866
    pts = [(x - lado / 2, y - h / 3), (x + lado / 2, y - h / 3), (x, y + 2 * h / 3)]
    relleno(msp, pts, AMARILLO, capa="CONTORNO")
    poli(msp, pts, "FINO", cerrada=True, lw=25)
    tn(msp, "!", (x, y - h / 3 + 0.25), 1.1, "BOTTOM_CENTER")


def prohibicion(msp, c, r=1.2):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "CONTORNO", color=(200, 16, 46), lw=40)
    d = r * 0.7071
    linea(msp, (c[0] - d, c[1] + d), (c[0] + d, c[1] - d), "CONTORNO", color=(200, 16, 46), lw=40)


def obligacion(msp, c, r=1.2):
    relleno_circulo(msp, c, r, (35, 95, 170), capa="CONTORNO")


def globo_n(msp, txt, c, apunta=None, rgb=(255, 255, 255), r=2.6):
    if apunta:
        dx, dy = apunta[0] - c[0], apunta[1] - c[1]
        d = math.hypot(dx, dy)
        linea(msp, (c[0] + dx / d * r, c[1] + dy / d * r), apunta, "FINO", lw=25)
        relleno_circulo(msp, apunta, 0.45, (0, 0, 0), capa="CONTORNO")
    relleno_circulo(msp, c, r, rgb)
    circulo(msp, c, r, "CONTORNO", lw=35)
    tn(msp, txt, c, 1.9 if len(txt) <= 2 else 1.8, "MIDDLE_CENTER")


def zs(msp, xc, y, tag, arriba):
    a, b = P(xc - 0.35, y), P(xc + 0.35, y)
    linea(msp, a, b, "CONTORNO", color=AZUL, lw=70)
    relleno_rect(msp, b[0] - 0.1, b[1] - 0.4, b[0] + 0.6, b[1] + 0.4, AMARILLO, capa="CONTORNO")
    if arriba:
        t(msp, tag, (a[0] + 2.3, b[1] + 1.8), 1.8, "BOTTOM_CENTER")
    else:
        t(msp, tag, (a[0] + 2.3, P(0, 6.35)[1]), 1.8, "MIDDLE_CENTER", fondo=True)


def camara_pat(msp, c, a=1.4):
    relleno_rect(msp, c[0] - a, c[1] - a, c[0] + a, c[1] + a, (255, 255, 255))
    rect(msp, c[0] - a, c[1] - a, c[0] + a, c[1] + a, "CONTORNO", color=COBRE, lw=35)
    linea(msp, (c[0] - a, c[1] - a), (c[0] + a, c[1] + a), "FINO", color=COBRE)
    linea(msp, (c[0] - a, c[1] + a), (c[0] + a, c[1] - a), "FINO", color=COBRE)
    relleno_circulo(msp, c, 0.6, COBRE, capa="CONTORNO")


def pararrayos(msp, c, r=1.5):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "CONTORNO", color=COBRE, lw=40)
    relleno(msp, [(c[0] - r * 0.55, c[1] - r * 0.45), (c[0] + r * 0.55, c[1] - r * 0.45), (c[0], c[1] + r * 0.75)],
            COBRE, capa="CONTORNO")


def bep(msp, c, w=4.0, h=1.0):
    relleno_rect(msp, c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, COBRE, capa="CONTORNO")
    rect(msp, c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, "FINO")
    for i in range(5):
        xb = c[0] - w / 2 + w * (i + 0.5) / 5
        relleno_circulo(msp, (xb, c[1]), 0.22, (255, 255, 255))


def anillo(msp, pts_m):
    poli(msp, [P(*p) for p in pts_m], "CONTORNO", color=COBRE, lw=35, tipo="TR_PAT")


# ------------------------------------------------------------------ planta

def muro(msp, pts):
    poli(msp, [P(*p) for p in pts], "CONTORNO", lw=80)


def planta(msp):
    nave, an = G["nave"], G["anexo"]
    relleno(msp, R(0, 0, 9.5, 18), COL["zona_recepcion"])
    relleno(msp, R(26, 0, 33, 9), COL["zona_recepcion"])
    relleno(msp, R(26, 9, 33, 18), (228, 234, 240))
    relleno(msp, R(9.5, 0, 26, 5), (250, 250, 250))
    # cámara de lixiviados (26) y caño PVC Ø110 desde la canaleta del secador (D20)
    cl = G["camara_lix"]
    caja(msp, cl["x"] - cl["a"] / 2, cl["y"] - cl["a"] / 2, cl["x"] + cl["a"] / 2, cl["y"] + cl["a"] / 2, (224, 236, 242))
    tn(msp, "26", P(cl["x"] - 0.2, cl["y"] + 1.6), 1.9, "BOTTOM_CENTER")
    # exteriores Norte
    caja(msp, 0.5, 20.2, 9.0, 24.7, (199, 166, 126))
    for (x, y, r, rgb) in ((14.6, 23.9, 0.9, (223, 234, 242)), (17.3, 23.7, 0.62, (255, 255, 255)),
                           (18.6, 23.7, 0.4, (170, 170, 170)), (21.6, 25.2, 0.25, (170, 170, 170))):
        disco(msp, x, y, r, rgb)
    cy, sc = G["ciclon"], G["scrubber"]
    plataforma(msp, sector_anillo(cy["x"], cy["y"], 0.92, 1.7, math.pi * 0.62, math.pi * 1.3))
    plataforma(msp, sector_anillo(sc["x"], sc["y"], sc["D"] / 2 + 0.02, sc["D"] / 2 + 0.8, -math.pi * 0.95, -math.pi * 0.05))
    caja(msp, 14.1, 9.3, 14.9, 20.2, (236, 246, 238), lw=25, capa="FINO")
    disco(msp, cy["x"], cy["y"], cy["D"] / 2, (238, 241, 242))
    disco(msp, sc["x"], sc["y"], sc["D"] / 2, (232, 240, 228))
    relleno(msp, R(21.9, 11.2, 23.1, 18.0), (249, 222, 220))
    poli(msp, R(21.9, 11.2, 23.1, 18.0), "FINO", cerrada=True, color=(220, 50, 50))
    poli(msp, [P(15.25, 22.1), P(19.9, 22.1), P(19.9, 20.55)], "CONTORNO", color=(225, 120, 30), lw=70)
    caja(msp, 19.5, 18.6, 20.2, 20.55, (244, 217, 191), lw=25, capa="FINO")

    # --- anexo
    relleno(msp, R(an["x0"], an["y0"], an["x1"], an["y1"]), (241, 225, 214))
    ic, ho = an["intercambiador"], an["hogar"]
    caja(msp, ic["x0"], ic["y0"], ic["x1"], ic["y1"], (225, 225, 225))
    caja(msp, ho["x0"], ho["y0"], ho["x1"], ho["y1"], (225, 165, 122))
    for v in an["ventiladores"]:
        disco(msp, v["x"], v["y"], 0.62, (255, 255, 255))
    ch = an["ciclon_humos"]
    circulo(msp, P(ch["x"], ch["y"]), 0.4 * S, "FINO", lw=25)
    rect(msp, *P(26.7, 23.1), *P(27.7, 24.1), "FINO", lw=25)
    for pts in ([(25.3, 19.9), (25.3, 19.25), (26.2, 19.25)], [(27.0, 19.25), (28.42, 19.25), (28.42, 19.9)]):
        poli(msp, [P(*p) for p in pts], "CONTORNO", color=ORO, lw=50)
    linea(msp, P(ho["x1"], 21.3), P(29.2, 21.3), "FINO")
    muro(msp, [(an["x0"], an["y0"]), (an["x0"], an["y1"]), (an["x1"], an["y1"]), (an["x1"], an["y0"])])
    si = G["silo"]
    disco(msp, si["x"], si["y"], si["D"] / 2, (230, 230, 230), lw=50)

    # --- dentro de la nave
    pg = G["pila_guano"]
    relleno_circulo(msp, P(pg["x"], pg["y"]), pg["r"] * S, (209, 180, 142))
    circulo(msp, P(pg["x"], pg["y"]), pg["r"] * S, "FINO")
    rect(msp, *P(4.4, 12.6), *P(9.2, 16.9), "FINO", tipo="TR_FINO")
    ps = G["pila_seca"]
    relleno_circulo(msp, P(ps["x"], ps["y"]), ps["r"] * S, (222, 200, 166))
    circulo(msp, P(ps["x"], ps["y"]), ps["r"] * S, "FINO")
    caja(msp, 0.92, 8.92, 12.3, 9.68, (233, 225, 212), lw=25, capa="FINO")
    tv = G["tolva"]
    caja(msp, tv["x0"], tv["y0"], tv["x1"], tv["y1"], (216, 199, 168))
    sec = G["secador"]
    x0s, y0s, x1s, y1s = sec["x0"], sec["y0"], sec["x0"] + sec["L"], sec["y0"] + sec["A"]
    caja(msp, x0s, y0s, x1s, y1s, (244, 244, 244), lw=50)
    pas = R(11.8, 8.05, 24.2, 8.85)
    relleno(msp, pas, (246, 236, 205))
    rayado(msp, pas, escala=0.35, angulo=-45, color=ORO)
    poli(msp, pas, "FINO", cerrada=True, color=ORO)
    for yy in (8.35, 10.25):
        poli(msp, [P(x0s + 0.3, yy), P(x1s - 0.3, yy)], "FINO", color=(90, 90, 90), tipo="TR_FINO")
    caja(msp, 24.05, 9.2, 25.35, 9.4, (225, 225, 225), lw=25, capa="FINO")
    caja(msp, 25.35, 8.8, 26.25, 9.8, (204, 204, 204))
    # plataforma del cabezal del elevador (+5,70) y plataforma de la zaranda (+3,00)
    plataforma(msp, R(25.05, 9.8, 26.55, 10.9))
    plataforma(msp, R(26.6, 10.2, 29.4, 14.2))
    esc = R(29.4, 13.35, 30.9, 14.15)
    relleno(msp, esc, (246, 236, 200))
    poli(msp, esc, "FINO", cerrada=True, color=ORO, lw=35)
    for i in range(1, 8):
        xx = 29.4 + 1.5 * i / 8
        linea(msp, P(xx, 13.35), P(xx, 14.15), "FINO", color=ORO)
    caja(msp, 27.55, 10.6, 28.45, 13.6, (216, 221, 219), lw=25, capa="FINO")
    caja(msp, 27.7, 11.4, 31.0, 12.1, (240, 240, 240), lw=25, capa="FINO")
    caja(msp, 29.0, 16.0, 30.2, 17.2, (221, 221, 238))

    # --- muros, locales y columnas
    for x in (13, 17.5, 22.5):
        linea(msp, P(x, 0), P(x, 5), "FINO", lw=25)
    poli(msp, [P(9.5, 0), P(9.5, 5), P(26, 5), P(26, 0)], "FINO", lw=35)
    muro(msp, [(9.5, 11.2), (9.5, 18)])
    linea(msp, P(26, 0), P(26, 9), "FINO")
    muro(msp, [(26, 9), (33, 9)])
    huecos = {"O": [(2, 3.2), (12.6, 16.6)], "S": [(19, 20), (28, 32)], "E": [(12.4, 14.9), (15, 16.2)],
              "N": [(26.2, 27.2)]}

    def tramo(lado, a, b):
        return {"S": [(a, 0), (b, 0)], "N": [(a, 18), (b, 18)], "O": [(0, a), (0, b)], "E": [(33, a), (33, b)]}[lado]

    for lado, largo in (("S", 33), ("N", 33), ("O", 18), ("E", 18)):
        a = 0
        for h0, h1 in huecos[lado]:
            muro(msp, tramo(lado, a, h0))
            a = h1
        muro(msp, tramo(lado, a, largo))
    for x in nave["porticos"]:
        for y in (0, 18):
            c = P(x, y)
            relleno_rect(msp, c[0] - 1.1, c[1] - 1.1, c[0] + 1.1, c[1] + 1.1, (0, 0, 0), capa="CONTORNO")


def instalaciones(msp):
    # canaleta de lavado con rejilla (D20) y caño PVC a la cámara de lixiviados
    caja(msp, 11.7, 7.32, 24.4, 7.6, (255, 255, 255), lw=25, capa="FINO")
    poli(msp, [P(9.5, 7.4), P(6.0, 8.2), P(2.5, 9.2), P(-0.55, 10.25)], "FINO", color=CELESTE, lw=35, tipo="TR_BAND")
    # bandejas (D15): existente (gris), nueva de potencia (gris oscuro), instrumentación (azul de trazos)
    gr = dict(capa="CONTORNO", lw=100)
    poli(msp, [P(11.4, 7.25), P(24.6, 7.25)], color=GRIS_EX, **gr)
    poli(msp, [P(20.0, 7.25), P(20.0, 0.5)], color=GRIS_EX, **gr)
    poli(msp, [P(9.6, 0.5), P(26.0, 0.5)], color=GRIS_EX, **gr)
    for pts in ([(4.0, 7.9), (4.0, 7.25), (11.4, 7.25)],
                [(24.6, 7.25), (26.6, 7.25), (26.6, 18.8), (21.2, 18.8)],
                [(18.75, 7.25), (18.75, 22.6), (16.5, 22.6)]):
        poli(msp, [P(*p) for p in pts], color=GRIS_NU, **gr)
    az = dict(capa="CONTORNO", color=AZUL, lw=50, tipo="TR_BAND")
    poli(msp, [P(4.4, 7.75), P(27.1, 7.75)], **az)
    poli(msp, [P(20.45, 7.75), P(20.45, 0.85), P(25.15, 0.85)], **az)
    poli(msp, [P(27.1, 7.75), P(27.1, 18.35), P(21.2, 18.35)], **az)


def seguridad(msp):
    sec = G["secador"]
    X = lambda s: sec["x0"] + s
    # puertas de inspección con microinterruptor (D1)
    n = 1
    for xd in (4.875, 8.125, 1.655):
        zs(msp, X(xd), 7.98, f"ZS-0{n}", False)
        zs(msp, X(xd), 10.62, f"ZS-0{n + 1}", True)
        n += 2
    # tapas cubre-eje (D2)
    for x in (11.8, 12.05, 23.95, 24.2):
        tapa(msp, P(x, 10.95))
    for x in (11.8, 12.05, 24.2):
        tapa(msp, P(x, 7.95 - 0.12))
    # lubricación remota (D21)
    lubric(msp, P(12.5, 7.94))
    lubric(msp, P(23.5, 7.94))
    # escaleras marineras con jaula (D3)
    escalera(msp, P(10.6, 8.45))
    escalera(msp, P(13.25, 21.1))
    escalera(msp, P(21.6, 25.68))
    escalera(msp, P(26.0, 10.92))
    tn(msp, "+5,70", P(25.8, 10.3), 1.8, "MIDDLE_CENTER")
    tn(msp, "+3,00", P(28.0, 10.4), 1.8, "MIDDLE_CENTER", fondo=True)
    t(msp, "pasarela 4.13 existente (+3,40)", P(18.0, 8.45), 1.8, "MIDDLE_CENTER", fondo=True)
    # registros y bocas (D9)
    for xy in ((3.81, 9.3), (14.5, 13.7), (22.5, 15.0), (24.6, 9.3), (15.45, 21.1), (16.42, 20.22),
               (21.0, 21.3), (27.2, 22.85), (29.1, 20.7)):
        registro(msp, P(*xy))
    # paradas de emergencia (D4)
    for xy, tag in (((4.4, 7.95), "PE-01"), ((11.3, 6.85), "PE-02"), ((18.2, 6.85), "PE-03"),
                    ((30.7, 10.25), "PE-07"), ((23.55, 24.25), "PE-06")):
        parada(msp, P(*xy), tag)
    parada(msp, P(24.75, 6.85), "PE-04", "L")
    parada(msp, P(26.7, 17.8))
    tn(msp, "PE-05", P(27.3, 18.55), 1.8, "MIDDLE_LEFT")
    # carteles (D15, D18)
    for xy in ((12.6, 7.94), (23.6, 7.94), (17.5, 7.94), (3.3, 8.3), (24.0, 17.6), (31.5, 8.7), (14.0, 6.95),
               (25.9, 24.85), (25.25, 0.3)):
        advertencia(msp, P(*xy))
    for xy in ((23.3, 24.9), (20.5, -0.3)):
        prohibicion(msp, P(*xy))
    for xy in ((1.2, -0.3), (18.5, -0.3)):
        obligacion(msp, P(*xy))

    # globos
    globo_n(msp, "4", P(18.0, 9.55))
    globo_n(msp, "5", P(12.85, 5.7))
    globo_n(msp, "29", P(14.0, 5.7))
    globo_n(msp, "7", P(25.85, 8.3))
    globo_n(msp, "22", P(24.25, 2.5))
    globo_n(msp, "9", P(26.8, 21.3))
    globo_n(msp, "13", P(31.0, 21.85))
    globo_n(msp, "18", P(14.5, 21.1))
    globo_n(msp, "19", P(17.3, 21.1))
    for txt, x in (("25", 11.25), ("23", 15.25), ("24", 21.1)):
        tn(msp, txt, P(x, 2.5), 2.5, "MIDDLE_CENTER")
    globo_n(msp, "E3", P(7.3, 18.9), P(6.9, 16.5), CREMA)
    globo_n(msp, "E6", P(31.4, 17.0), P(29.6, 16.6), CREMA)
    globo_n(msp, "E4", P(29.2, 15.6), P(28.0, 12.1), CREMA)
    globo_n(msp, "E5", P(31.4, 12.9), P(28.6, 11.7), CREMA)


def puesta_a_tierra(msp):
    """Ítem 16 (D16): anillo Cu desnudo 50 mm², jabalinas PAT-1 a PAT-8, BEP y pararrayos."""
    pat = {1: (-0.6, -0.6), 2: (33.6, -0.6), 3: (-0.6, 18.6), 4: (20.0, 25.0), 5: (29.2, 25.0),
           6: (33.6, 18.6), 7: (24.0, -0.6), 8: (16.4, 25.6)}
    anillo(msp, [pat[1], pat[7], pat[2], pat[6], (29.2, 18.6), pat[5], pat[4], (20.0, 18.6), pat[3], pat[1]])
    anillo(msp, [pat[4], pat[8]])
    # BEP en la sala de control (22), unida al anillo en PAT-7
    anillo(msp, [(23.3, 0.15), (23.3, -0.6)])
    bep(msp, P(23.3, 0.15))
    tn(msp, "BEP", P(23.72, 0.22), 1.8, "MIDDLE_LEFT", color=COBRE)
    # pararrayos Franklin con bajada de Cu 50 mm² y guardacable
    an, ex, si = G["anexo"]["chimenea"], G["extractor"], G["silo"]
    for (cx, cy), baj, union in (((an["x"], an["y"]), (an["x"] - an["D"] / 2 - 0.04, an["y"]), (an["x"] - 0.29, 25.0)),
                                 ((ex["chim_x"], ex["chim_y"]), (ex["chim_x"] + ex["chim_D"] / 2 + 0.04, ex["chim_y"]), pat[4]),
                                 ((si["x"], 20.75), (si["x"], si["y"] - si["D"] / 2 - 0.04), (si["x"], 18.6))):
        if union != baj:
            anillo(msp, [baj, union])
        linea(msp, P(cx, cy), P(*baj), "CONTORNO", color=COBRE, lw=35)
        b = P(*baj)
        relleno_rect(msp, b[0] - 0.5, b[1] - 0.5, b[0] + 0.5, b[1] + 0.5, COBRE, capa="CONTORNO")
    pararrayos(msp, P(an["x"], an["y"]))
    pararrayos(msp, P(ex["chim_x"], ex["chim_y"]))
    pararrayos(msp, P(si["x"], 20.75))
    for n, (x, y) in pat.items():
        c = P(x, y)
        camara_pat(msp, c)
        if n in (1, 7, 2):
            tn(msp, f"PAT-{n}", (c[0] + 2.0, c[1] - 1.6), 1.8, "TOP_LEFT", color=COBRE)
        elif n == 3:
            tn(msp, f"PAT-{n}", (c[0] - 0.5, c[1] + 2.0), 1.8, "BOTTOM_LEFT", color=COBRE)
        elif n == 6:
            tn(msp, f"PAT-{n}", (c[0] - 2.0, c[1] + 2.0), 1.8, "BOTTOM_RIGHT", color=COBRE)
        elif n == 8:
            tn(msp, f"PAT-{n}", (c[0] - 2.0, c[1]), 1.8, "MIDDLE_RIGHT", color=COBRE)
        elif n == 4:
            tn(msp, f"PAT-{n}", (c[0] + 2.0, c[1] - 1.75), 1.8, "MIDDLE_LEFT", color=COBRE)
        else:
            tn(msp, f"PAT-{n}", (c[0] + 2.0, c[1] + 1.2), 1.8, "BOTTOM_LEFT", color=COBRE)


# ------------------------------------------------------------------ leyenda, tabla y notas

def leyenda(msp):
    x, y = 268.0, 267.0
    subtitulo(msp, "LEYENDA", x, y, 2.6)
    filas = ["parada de emergencia tipo hongo (PE)", "puerta 700 × 600 con microinterruptor ZS",
             "plataforma nueva con baranda 1,0 m y rodapié", "escalera marinera con jaula guardahombre",
             "registro, boca de limpieza o tapa (ítem 9)", "bloque de lubricación remoto (ítem 21)",
             "tapa cubre-eje (ítem 2)", "bandeja de potencia existente", "bandeja de potencia nueva 300 mm",
             "bandeja de instrumentación 150 mm", "canaleta de lavado con rejilla", "caño PVC Ø110 a cámara de lixiviados",
             "cartel de advertencia (IRAM 10005)", "cartel de prohibición", "cartel de obligación (EPP)",
             "cámara de inspección de PAT con jabalina (ítem 16)", "anillo de tierra Cu desnudo 50 mm² enterrado",
             "barra equipotencial principal BEP (ítem 16)", "pararrayos Franklin con bajada (ítem 16)"]
    paso = 4.05
    for i, txt in enumerate(filas):
        yy = y - 4.0 - i * paso
        c = (x + 3.0, yy)
        simbolo(msp, i, c)
        t(msp, txt, (x + 7.5, yy), 1.8, "MIDDLE_LEFT")
    return y - 4.0 - (len(filas) - 1) * paso


def simbolo(msp, i, c):
    x, y = c
    if i == 0:
        parada(msp, c)
    elif i == 1:
        linea(msp, (x - 2.8, y), (x + 1.6, y), "CONTORNO", color=AZUL, lw=70)
        relleno_rect(msp, x + 1.6, y - 0.6, x + 2.4, y + 0.6, AMARILLO, capa="CONTORNO")
    elif i == 2:
        plataforma(msp, [(x - 2.8, y - 1.0), (x + 2.8, y - 1.0), (x + 2.8, y + 1.0), (x - 2.8, y + 1.0)])
    elif i == 3:
        escalera(msp, c)
    elif i == 4:
        registro(msp, c)
    elif i == 5:
        lubric(msp, c)
    elif i == 6:
        tapa(msp, c)
    elif i in (7, 8):
        linea(msp, (x - 2.8, y), (x + 2.8, y), "CONTORNO", color=GRIS_EX if i == 7 else GRIS_NU, lw=100)
    elif i == 9:
        poli(msp, [(x - 2.8, y), (x + 2.8, y)], "CONTORNO", color=AZUL, lw=50, tipo="TR_BAND")
    elif i == 10:
        relleno_rect(msp, x - 2.8, y - 0.8, x + 2.8, y + 0.8, (255, 255, 255))
        rect(msp, x - 2.8, y - 0.8, x + 2.8, y + 0.8, "FINO")
        linea(msp, (x - 2.8, y), (x + 2.8, y), "FINO")
    elif i == 11:
        poli(msp, [(x - 2.8, y), (x + 2.8, y)], "FINO", color=CELESTE, lw=35, tipo="TR_BAND")
    elif i == 12:
        advertencia(msp, (x, y - 0.2))
    elif i == 13:
        prohibicion(msp, c)
    elif i == 14:
        obligacion(msp, c)
    elif i == 15:
        camara_pat(msp, c)
    elif i == 16:
        poli(msp, [(x - 2.8, y), (x + 2.8, y)], "CONTORNO", color=COBRE, lw=35, tipo="TR_PAT")
    elif i == 17:
        bep(msp, c)
    elif i == 18:
        pararrayos(msp, c)


AGREGADOS = [
    ("1", "Manijas, levas, ZS-01..06 y cajas de conexión", "6"),
    ("2", "Tapas cubre-eje, cubreacoples, rejillas de aspiración", "18"),
    ("3", "Jaulas, plataformas, barandas y escaleras", "9"),
    ("4", "Paradas de emergencia PE-01 a PE-07", "7"),
    ("9", "Registros, bocas de hombre y tapas", "12"),
    ("11-14", "Ciclón, generador, silo y cenizas", "gl."),
    ("15", "Bandejas y bajadas a motores", "gl."),
    ("16", "Puesta a tierra: anillo Cu 50 mm², 8 jabalinas, BEP y 3 pararrayos", "12"),
    ("17", "Luces de emergencia y proyectores LED", "12"),
    ("18", "Carteles de seguridad", "20"),
    ("20", "Canaletas, rejillas y cámaras", "4"),
    ("21-22", "Lubricación remota y tensores M20 visibles", "gl."),
]


def tabla_agregados(msp, y):
    subtitulo(msp, "RESUMEN DE AGREGADOS", 268.0, y, 2.6)
    filas = [["Ítem", "Agregado (modelo 3D)", "Cant."]] + [list(f) for f in AGREGADOS]
    yb = tabla(msp, 268.0, y - 1.8, [12, 110, 14], filas, h_fila=3.27, altura=1.7, alin=["C", "L", "C"],
               sombras={8: (250, 236, 220)})
    return yb


NOTA16 = [
    "Ítem 16 (Rev. E): anillo de Cu desnudo 50 mm² enterrado a 0,6 m alrededor de la nave y del anexo, con 8 jabalinas",
    "Cu-Ac 5/8\" × 3 m en cámaras de inspección PAT-1 a PAT-8 (R ≤ 10 Ω; IRAM 2281, AEA 90364). BEP en la sala de",
    "control (22): PE del TGF y del TG2, estructura, bandejas, ductos y cañerías. Pararrayos Franklin en la chimenea de",
    "humos, la chimenea del lavador y el silo, con bajada de Cu 50 mm² y guardacable de 2 m (IRAM 2184).",
    "PAT-9 y PAT-10: malla propia de la zona de biogás (fuera de esta lámina, plano 20), unida al anillo.",
]


def main():
    revs = [("D", "09/2026", "Emisión original: ítems 1-4, 9, 11-15, 17, 18 y 20-22 de los agregados 3D"),
            ("E", FECHA, "Se agrega el ítem 16: puesta a tierra, barra equipotencial y pararrayos")]
    doc, msp, z = lamina(17, "NAVE: SEGURIDAD, ACCESOS\nY MANTENIMIENTO", "1:150", revs)
    trazos(doc)
    titulo_vista(msp, "NAVE Y EQUIPOS: SEGURIDAD, ACCESOS Y MANTENIMIENTO - ESC. 1:150", 26, 278, 3.5)
    planta(msp)
    instalaciones(msp)
    seguridad(msp)
    puesta_a_tierra(msp)
    norte(msp, 262.0, 258.0, 4.5)
    escala_grafica(msp, 26.0, 76.0, "1:150", 10, 2)
    y = leyenda(msp)
    yb = tabla_agregados(msp, y - 8.0)
    y = yb - 4.0
    for r in NOTA16:
        t(msp, r, (268.0, y), 1.8, "TOP_LEFT")
        y -= 2.6
    exportar_lamina(doc, 17)


if __name__ == "__main__":
    main()
