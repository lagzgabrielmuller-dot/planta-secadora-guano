"""P15 - Protección contra incendios y medios de escape (nave, anexo y silo), esc. 1:250.

Redibujo vectorial de la lámina Rev. D. Geometría en metros de fuente/datos/layout_planta.json
(clave G) y posiciones de los elementos de seguridad del código Rev. D del visor (visor.html,
ítems D17, D18 y D19).
"""
import json
import math
import os

from lamina_secadora import (COL, circulo, escala_grafica, exportar_lamina, factor, flecha, lamina,
                             linea, norte, poli, rayado, rect, relleno, relleno_circulo, relleno_rect,
                             subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

S = factor("1:250") * 1000.0          # mm de papel por metro
OX, OY = 41.9, 159.0                  # vértice SO de la nave en el papel

ROJO = COL["incendio"]
VERDE = COL["salida"]
ORO = (200, 160, 30)


def P(x, y):
    return (OX + x * S, OY + y * S)


def trazos(doc):
    """Tipos de línea de trazos en mm de papel (la plantilla trae DASHED en pulgadas y $LTSCALE 0,5:
    los patrones se definen al doble)."""
    for nombre, (a, b) in {"TR_RED": (2.6, 1.2), "TR_ESC": (1.6, 1.0), "TR_FINO": (1.2, 0.7)}.items():
        if nombre not in doc.linetypes:
            doc.linetypes.add(nombre, pattern=[2 * (a + b), 2 * a, -2 * b], description=nombre)


def R(x0, y0, x1, y1):
    return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]


def circ_pts(cx, cy, r, n=72):
    return [P(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ símbolos (mm de papel)

def tri(msp, c, lado=3.0, lleno=True, letra=None, color=ROJO):
    x, y = c
    h = lado * 0.866
    pts = [(x - lado / 2, y - h / 3), (x + lado / 2, y - h / 3), (x, y + 2 * h / 3)]
    if lleno:
        relleno(msp, pts, color, capa="CONTORNO")
    else:
        relleno(msp, pts, (255, 255, 255))
        poli(msp, pts, "FINO", cerrada=True, color=color)
    if letra:
        t(msp, letra, (x, y - h / 3 + 0.25), lado * 0.36, "BOTTOM_CENTER", color=color)


def mf_nuevo(msp, xy, num, lado="R"):
    c = P(*xy)
    tri(msp, c, 3.0, True)
    _num(msp, c, num, lado)


def mf_exist(msp, xy, num, lado="R"):
    c = P(*xy)
    tri(msp, c, 3.0, False, "E")
    _num(msp, c, num, lado)


def _num(msp, c, num, lado):
    if lado == "R":
        tn(msp, num, (c[0] + 2.0, c[1] - 0.2), 1.8, "MIDDLE_LEFT", color=ROJO)
    else:
        tn(msp, num, (c[0] - 2.0, c[1] - 0.2), 1.8, "MIDDLE_RIGHT", color=ROJO)


def hidrante(msp, c, tag=None, pos_tag=(0, 3.0), alin="BOTTOM_CENTER"):
    relleno_circulo(msp, c, 1.8, (255, 255, 255))
    circulo(msp, c, 1.8, "CONTORNO", color=ROJO, lw=40)
    relleno_circulo(msp, c, 0.75, ROJO, capa="CONTORNO")
    linea(msp, (c[0] + 1.8, c[1]), (c[0] + 2.9, c[1]), "FINO", color=ROJO, lw=35)
    if tag:
        tn(msp, tag, (c[0] + pos_tag[0], c[1] + pos_tag[1]), 1.8, alin, color=ROJO)


def detector(msp, c, letra, r=1.15):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "FINO", lw=25)
    tn(msp, letra, c, r * 1.05, "MIDDLE_CENTER")


def sirena(msp, c):
    tri(msp, c, 2.4, False, "S")


def pulsador(msp, c, a=1.7):
    relleno_rect(msp, c[0] - a / 2, c[1] - a / 2, c[0] + a / 2, c[1] + a / 2, ROJO, capa="CONTORNO")
    relleno_rect(msp, c[0] - a * 0.22, c[1] - a * 0.22, c[0] + a * 0.22, c[1] + a * 0.22, (255, 255, 255))


def luz(msp, c, w=2.6, h=1.5):
    x0, y0, x1, y1 = c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2
    relleno_rect(msp, x0, y0, x1, y1, (255, 255, 255))
    rect(msp, x0, y0, x1, y1, "FINO", lw=25)
    linea(msp, (x0, y0), (x1, y1), "FINO")
    linea(msp, (x0, y1), (x1, y0), "FINO")


def rombo(msp, c, txt, r=2.8):
    pts = [(c[0], c[1] + r), (c[0] + r, c[1]), (c[0], c[1] - r), (c[0] - r, c[1])]
    relleno(msp, pts, (255, 255, 255))
    poli(msp, pts, "CONTORNO", cerrada=True, lw=35)
    tn(msp, txt, c, 1.9, "MIDDLE_CENTER")


def salida(msp, a, b, texto=None, pos=None, alin="MIDDLE_LEFT"):
    flecha(msp, a, b, "CONTORNO", VERDE, tam=2.2, lw=70)
    if texto:
        tn(msp, texto, pos, 1.8, alin, color=VERDE)


def recorrido(msp, pts_m, texto=None, pos_m=None):
    pts = [P(*p) for p in pts_m]
    poli(msp, pts, "FINO", color=VERDE, lw=35, tipo="TR_ESC")
    relleno_circulo(msp, pts[0], 0.9, VERDE, capa="CONTORNO")
    if texto:
        tn(msp, texto, P(*pos_m), 1.8, "MIDDLE_CENTER", color=VERDE)


def red_inc(msp, pts_m):
    poli(msp, [P(*p) for p in pts_m], "FINO", color=ROJO, lw=50, tipo="TR_RED")


# ------------------------------------------------------------------ planta

def muro(msp, pts):
    poli(msp, [P(*p) for p in pts], "CONTORNO", lw=80)


def planta(msp):
    nave, an = G["nave"], G["anexo"]
    # --- rellenos de zonas
    relleno(msp, R(0, 0, 9.5, 18), COL["zona_recepcion"])
    relleno(msp, R(26, 0, 33, 9), COL["zona_recepcion"])
    relleno(msp, R(26, 9, 33, 18), (228, 234, 240))
    relleno(msp, R(9.5, 0, 26, 5), (250, 250, 250))
    # sector S1 (rayado rojo) en la zona central de proceso
    rayado(msp, R(9.5, 5, 26, 18), escala=1.0, angulo=45, color=(235, 120, 120))
    # --- exteriores: biofiltro, ciclón, lavador, tanque, extractor
    relleno(msp, R(0.5, 20.2, 9.0, 24.7), (199, 166, 126))
    rect(msp, *P(0.5, 20.2), *P(9.0, 24.7), "CONTORNO", lw=35)
    for (x, y, r, rgb) in ((14.6, 23.9, 0.9, (223, 234, 242)), (17.3, 23.7, 0.62, (255, 255, 255)),
                           (18.6, 23.7, 0.4, (170, 170, 170)), (14.5, 21.1, 0.9, (238, 241, 242)),
                           (17.3, 21.1, 1.1, (232, 240, 228)), (21.6, 25.2, 0.25, (170, 170, 170))):
        relleno_circulo(msp, P(x, y), r * S, rgb)
        circulo(msp, P(x, y), r * S, "CONTORNO", lw=35)
    # ductos: aire agotado (verde) y aire caliente (rojo)
    relleno(msp, R(14.1, 9.3, 14.9, 20.2), (236, 246, 238))
    poli(msp, R(14.1, 9.3, 14.9, 20.2), "FINO", cerrada=True, color=(60, 160, 90))
    relleno(msp, R(21.9, 11.2, 23.1, 18.0), (249, 222, 220))
    poli(msp, R(21.9, 11.2, 23.1, 18.0), "FINO", cerrada=True, color=(220, 50, 50))
    # recirculación (D7): derivación desde el ciclón y bajada por el muro Oeste del anexo
    poli(msp, [P(15.25, 22.1), P(19.9, 22.1), P(19.9, 20.55)], "CONTORNO", color=(225, 120, 30), lw=70)
    relleno(msp, R(19.5, 18.6, 20.2, 20.55), (244, 217, 191))
    rect(msp, *P(19.5, 18.6), *P(20.2, 20.55), "FINO", lw=25)

    # --- anexo
    relleno(msp, R(an["x0"], an["y0"], an["x1"], an["y1"]), (241, 225, 214))
    ic, ho = an["intercambiador"], an["hogar"]
    relleno(msp, R(ic["x0"], ic["y0"], ic["x1"], ic["y1"]), (225, 225, 225))
    rect(msp, *P(ic["x0"], ic["y0"]), *P(ic["x1"], ic["y1"]), "CONTORNO", lw=35)
    relleno(msp, R(ho["x0"], ho["y0"], ho["x1"], ho["y1"]), (225, 165, 122))
    rect(msp, *P(ho["x0"], ho["y0"]), *P(ho["x1"], ho["y1"]), "CONTORNO", lw=35)
    for v in an["ventiladores"]:
        relleno_circulo(msp, P(v["x"], v["y"]), 0.62 * S, (255, 255, 255))
        circulo(msp, P(v["x"], v["y"]), 0.62 * S, "CONTORNO", lw=35)
    ch = an["ciclon_humos"]
    circulo(msp, P(ch["x"], ch["y"]), 0.4 * S, "FINO", lw=25)
    rect(msp, *P(26.7, 23.1), *P(27.7, 24.1), "FINO", lw=25)      # cenizas
    linea(msp, P(ho["x1"], 21.3), P(29.2, 21.3), "FINO")            # sinfín de cáscara
    muro(msp, [(an["x0"], an["y0"]), (an["x0"], an["y1"]), (an["x1"], an["y1"]), (an["x1"], an["y0"])])
    # muro cortafuego RF-120 (lado Sur del anexo) con el paso del ducto caliente
    relleno(msp, R(an["x0"], 17.9, an["x1"], 18.35), ROJO, capa="CONTORNO")
    relleno(msp, R(21.8, 17.95, 23.2, 18.3), (255, 255, 255))
    rect(msp, *P(21.8, 17.95), *P(23.2, 18.3), "FINO", color=(220, 50, 50))

    # --- S3: zona del silo (72 m² → r = 4,79 m) y silo con rociadores
    si = G["silo"]
    r3 = math.sqrt(72 / math.pi)
    rayado(msp, circ_pts(si["x"], si["y"], r3), escala=1.2, angulo=60, color=(212, 167, 0))
    poli(msp, circ_pts(si["x"], si["y"], r3), "FINO", cerrada=True, color=(200, 160, 30), lw=25, tipo="TR_FINO")
    rr = si["D"] / 2 + 0.17
    circulo(msp, P(si["x"], si["y"]), rr * S, "CONTORNO", color=ROJO, lw=50)
    relleno_circulo(msp, P(si["x"], si["y"]), si["D"] / 2 * S, (230, 230, 230))
    circulo(msp, P(si["x"], si["y"]), si["D"] / 2 * S, "CONTORNO", lw=60)
    for i in range(8):
        a = 2 * math.pi * i / 8 + math.pi / 2
        relleno_circulo(msp, P(si["x"] + rr * math.cos(a), si["y"] + rr * math.sin(a)), 0.45, ROJO, capa="CONTORNO")
    tn(msp, "TS-01", P(33.4, 22.7), 1.8, "MIDDLE_LEFT")
    relleno_rect(msp, *P(28.85, 22.48), *P(29.1, 22.73), ROJO, capa="CONTORNO")   # válvula de diluvio
    tn(msp, "VD", P(29.5, 25.75), 1.8, "MIDDLE_LEFT", color=ROJO)

    # --- equipos dentro de la nave
    pg = G["pila_guano"]
    relleno_circulo(msp, P(pg["x"], pg["y"]), pg["r"] * S, (209, 180, 142))
    circulo(msp, P(pg["x"], pg["y"]), pg["r"] * S, "FINO")
    rect(msp, *P(4.4, 12.6), *P(9.2, 16.9), "FINO", tipo="TR_FINO")    # campana E3
    ps = G["pila_seca"]
    relleno_circulo(msp, P(ps["x"], ps["y"]), ps["r"] * S, (222, 200, 166))
    circulo(msp, P(ps["x"], ps["y"]), ps["r"] * S, "FINO")
    # cinta de alimentación y tolva
    relleno(msp, R(0.92, 8.92, 12.3, 9.68), (233, 225, 212))
    rect(msp, *P(0.92, 8.92), *P(12.3, 9.68), "FINO", lw=25)
    tv = G["tolva"]
    relleno(msp, R(tv["x0"], tv["y0"], tv["x1"], tv["y1"]), (216, 199, 168))
    rect(msp, *P(tv["x0"], tv["y0"]), *P(tv["x1"], tv["y1"]), "CONTORNO", lw=35)
    # secador
    sec = G["secador"]
    x0s, y0s, x1s, y1s = sec["x0"], sec["y0"], sec["x0"] + sec["L"], sec["y0"] + sec["A"]
    relleno(msp, R(x0s, y0s, x1s, y1s), (244, 244, 244))
    rect(msp, *P(x0s, y0s), *P(x1s, y1s), "CONTORNO", lw=50)
    for yy in (8.35, 10.25):
        poli(msp, [P(x0s + 0.3, yy), P(x1s - 0.3, yy)], "FINO", color=(90, 90, 90), tipo="TR_FINO")
    # sinfín de descarga y elevador
    relleno(msp, R(24.05, 9.2, 25.35, 9.4), (225, 225, 225))
    rect(msp, *P(24.05, 9.2), *P(25.35, 9.4), "FINO")
    relleno(msp, R(25.35, 8.8, 26.25, 9.8), (204, 204, 204))
    rect(msp, *P(25.35, 8.8), *P(26.25, 9.8), "CONTORNO", lw=35)
    # zona 28: plataforma de la zaranda, trommel, cinta de salida, escalera y envasadora
    rect(msp, *P(26.6, 10.2), *P(29.4, 14.2), "FINO", lw=35, tipo="TR_FINO")
    relleno(msp, R(27.55, 10.6, 28.45, 13.6), (216, 221, 219))
    rect(msp, *P(27.55, 10.6), *P(28.45, 13.6), "FINO", lw=25)
    relleno(msp, R(27.7, 11.4, 31.0, 12.1), (255, 255, 255))
    rect(msp, *P(27.7, 11.4), *P(31.0, 12.1), "FINO", lw=25)
    relleno(msp, R(29.4, 13.35, 30.9, 14.15), (255, 255, 255))
    rect(msp, *P(29.4, 13.35), *P(30.9, 14.15), "FINO", lw=25)
    relleno(msp, R(29.0, 16.0, 30.2, 17.2), (221, 221, 238))
    rect(msp, *P(29.0, 16.0), *P(30.2, 17.2), "FINO", lw=25)

    # --- muros, locales y columnas
    for x in (13, 17.5, 22.5):
        linea(msp, P(x, 0), P(x, 5), "FINO", lw=25)
    poli(msp, [P(9.5, 0), P(9.5, 5), P(26, 5), P(26, 0)], "FINO", lw=35)
    linea(msp, P(9.5, 5), P(9.5, 11.2), "FINO", lw=25)
    muro(msp, [(9.5, 11.2), (9.5, 18)])                       # muro de contención
    muro(msp, [(26, 5), (26, 9), (33, 9)])                     # muros del acopio
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
            relleno_rect(msp, c[0] - 0.75, c[1] - 0.75, c[0] + 0.75, c[1] + 0.75, (0, 0, 0), capa="CONTORNO")


def seguridad(msp):
    # --- red de incendio enterrada (anillo) y ramal a la válvula de diluvio
    red_inc(msp, [(-1.3, 4.6), (-1.3, -1.0), (35.6, -1.0), (35.6, 26.5), (12.0, 26.5), (12.0, 19.2)])
    red_inc(msp, [(35.6, 19.2), (29.1, 19.2)])
    flecha(msp, P(-1.3, 3.5), P(-4.0, 3.5), "CONTORNO", ROJO, tam=2.0, lw=50)
    hidrante(msp, P(-1.3, 4.6), "HI-1", (-2.3, 1.6), "BOTTOM_RIGHT")
    hidrante(msp, P(12.0, 19.2), "HI-2", (-2.3, 1.6), "BOTTOM_RIGHT")
    hidrante(msp, P(35.6, 9.5), "HI-3", (2.3, 1.6), "BOTTOM_LEFT")

    # --- recorridos máximos a las salidas
    recorrido(msp, [(13.0, 17.3), (10.4, 11.0), (0.5, 14.6)], "17 m", (6.5, 11.35))
    recorrido(msp, [(16.0, 6.5), (9.4, 4.95), (0.5, 2.6)], "16 m", (8.6, 5.5))
    recorrido(msp, [(20.0, 17.3), (32.6, 15.6)], "13 m", (27.4, 16.85))
    recorrido(msp, [(24.5, 6.5), (24.5, 11.3), (32.6, 15.0)], "13 m", (25.4, 12.6))

    # --- salidas (ancho libre)
    salida(msp, P(-0.2, 14.6), (OX - 7.0, P(0, 14.6)[1]), "P1 4,00 m", (OX - 7.8, P(0, 14.6)[1]), "MIDDLE_RIGHT")
    salida(msp, P(-0.2, 2.6), (OX - 7.0, P(0, 2.6)[1]), "SE2 1,20 m", (OX - 7.8, P(0, 2.6)[1]), "MIDDLE_RIGHT")
    salida(msp, P(33.3, 15.6), P(34.8, 15.6), "SE1 1,20 m", (P(34.8, 15.6)[0] + 1.2, P(0, 15.6)[1]))
    salida(msp, P(33.3, 13.65), P(34.8, 13.65), "P3 2,50 m", (P(34.8, 13.65)[0] + 1.2, P(0, 13.65)[1]))
    salida(msp, P(24.6, 24.8), P(24.6, 26.4), "anexo 1,20 m", (P(24.6, 26.4)[0] + 1.0, P(0, 26.5)[1] + 1.6))
    salida(msp, P(30.0, -0.3), P(30.0, -2.0), "P2 4,00 m", (P(30.0, -2.0)[0], P(0, -2.0)[1] - 1.0), "TOP_CENTER")
    # luces de emergencia (D17)
    for xy in ((0.05, 14.6), (0.05, 2.6), (32.95, 15.6), (32.95, 13.65), (30.0, 0.05), (19.5, 0.05),
               (26.7, 17.75), (24.6, 24.25), (24.3, 4.8)):
        luz(msp, P(*xy))
    tn(msp, "muro RF-120", P(23.15, 17.45), 1.8, "MIDDLE_LEFT", color=ROJO)

    # --- matafuegos existentes (Rev. C) y nuevos (D19)
    for xy, n in (((0.2, 5.5), "01"), ((0.2, 11.0), "02"), ((5.5, 0.3), "03"), ((16.5, 0.3), "04"),
                  ((22.0, 0.3), "05"), ((11.0, 17.75), "06"), ((27.5, 17.75), "07"), ((32.75, 11.0), "08")):
        mf_exist(msp, xy, n)
    for xy, n in (((25.6, 1.6), "09"), ((32.75, 4.5), "10"), ((25.6, 24.4), "11"), ((20.6, 19.4), "12"),
                  ((29.3, 24.35), "13"), ((10.8, 24.2), "14")):
        mf_nuevo(msp, xy, n, "L" if n == "14" else "R")

    # --- detección y alarma
    for x in (11.25, 15.25, 20.0, 24.25):
        detector(msp, P(x, 2.2), "H")
    detector(msp, P(22.8, 21.3), "T")
    detector(msp, P(26.5, 23.5), "T")
    for pxy, sxy in (((32.55, 16.6), (32.55, 17.3)), ((0.45, 12.3), (0.45, 11.6)), ((0.45, 3.6), (0.45, 4.3)),
                     ((18.7, 0.4), (18.1, 0.4)), ((27.4, 0.4), (26.8, 0.4))):
        pulsador(msp, P(*pxy))
        sirena(msp, P(*sxy))
    c = P(25.4, 3.25)
    relleno_rect(msp, c[0] - 1.6, c[1] - 1.3, c[0] + 1.6, c[1] + 1.3, ROJO, capa="CONTORNO")
    tn(msp, "CI", P(24.85, 2.4), 1.8, "MIDDLE_LEFT", color=ROJO)

    # --- sectores
    rombo(msp, P(4.5, 5.45), "S1")
    rombo(msp, P(24.5, 23.2), "S2")
    rombo(msp, P(34.3, 25.3), "S3")
    t(msp, "PC1 RF-60", P(25.8, 19.0), 1.8, "MIDDLE_LEFT", color=ROJO)
    t(msp, "CCF", P(21.95, 19.97), 1.8, "MIDDLE_CENTER", color=ROJO)

    # --- notas al pie de la planta
    t(msp, "red de incendio PEAD Ø75 enterrada en anillo, desde el tanque de 20 m³ y las bombas M25/M26",
      (44.0, 151.6), 1.8, "MIDDLE_LEFT", color=ROJO)
    t(msp, "(x = -19,2 m, plano 13) · a HI-4 por R6", (44.0, 149.0), 1.8, "MIDDLE_LEFT", color=ROJO)
    circulo(msp, (110.7, 142.6), 2.3, "CONTORNO", color=VERDE, lw=35)
    tn(msp, "PR", (110.7, 142.6), 1.9, "MIDDLE_CENTER", color=VERDE)
    t(msp, "punto de reunión (estacionamiento 34)", (114.0, 142.6), 1.8, "MIDDLE_LEFT", color=VERDE)


# ------------------------------------------------------------------ leyenda, tabla y notas

def leyenda(msp):
    x0, x1, y = 196.0, 301.0, 267.0
    subtitulo(msp, "LEYENDA", x0, y, 2.6)
    paso = 4.4
    filas = [
        ("mfn", "matafuego nuevo (tipo en tabla)", "mfe", "matafuego existente Rev. C"),
        ("hid", "hidrante 45 mm con gabinete", "H", "detector óptico de humo"),
        ("T", "detector térmico-velocimétrico", "pul", "pulsador manual de alarma"),
        ("sir", "sirena con baliza", "luz", "luz de emergencia autónoma 3 h"),
        ("sal", "salida y ancho libre", "rec", "recorrido máximo a salida"),
        ("red", "red de incendio enterrada", "rf", "muro cortafuego RF-120"),
        ("s1", "S1 nave (R3, F 60)", "s2", "S2 anexo (R3, F 30)"),
        ("s3", "S3 silo (R3, rociadores)", "ci", "CI central de incendio"),
    ]
    for i, (a, ta, b, tb) in enumerate(filas):
        yy = y - 4.0 - i * paso
        for xs, s, tx in ((x0, a, ta), (x1, b, tb)):
            simbolo_ley(msp, s, xs + 2.6, yy)
            t(msp, tx, (xs + 7.0, yy), 1.8, "MIDDLE_LEFT")


def simbolo_ley(msp, s, x, y):
    if s == "mfn":
        tri(msp, (x, y - 0.2), 3.0, True)
    elif s == "mfe":
        tri(msp, (x, y - 0.2), 3.0, False, "E")
    elif s == "hid":
        hidrante(msp, (x - 0.4, y))
    elif s in ("H", "T"):
        detector(msp, (x, y), s)
    elif s == "pul":
        pulsador(msp, (x, y))
    elif s == "sir":
        sirena(msp, (x, y - 0.2))
    elif s == "luz":
        luz(msp, (x, y))
    elif s == "sal":
        flecha(msp, (x - 2.6, y), (x + 2.6, y), "CONTORNO", VERDE, tam=2.0, lw=70)
    elif s == "rec":
        poli(msp, [(x - 2.6, y), (x + 2.6, y)], "FINO", color=VERDE, lw=35, tipo="TR_ESC")
    elif s == "red":
        poli(msp, [(x - 2.6, y), (x + 2.6, y)], "FINO", color=ROJO, lw=50, tipo="TR_RED")
    elif s == "rf":
        relleno_rect(msp, x - 2.6, y - 0.7, x + 2.6, y + 0.7, ROJO, capa="CONTORNO")
    elif s == "ci":
        relleno_rect(msp, x - 2.6, y - 1.1, x + 2.6, y + 1.1, ROJO, capa="CONTORNO")
        rect(msp, x - 2.6, y - 1.1, x + 2.6, y + 1.1, "FINO")
    else:
        caja = [(x - 2.6, y - 1.1), (x + 2.6, y - 1.1), (x + 2.6, y + 1.1), (x - 2.6, y + 1.1)]
        if s == "s2":
            relleno(msp, caja, (241, 225, 214))
            rayado(msp, caja, escala=0.5, angulo=-30, color=(190, 140, 80))
        elif s == "s1":
            rayado(msp, caja, escala=1.0, angulo=45, color=(235, 120, 120))
        else:
            rayado(msp, caja, escala=1.0, angulo=60, color=(212, 167, 0))
        poli(msp, caja, "FINO", cerrada=True)


MATAFUEGOS = [
    ("MF-01", "ABC 10 kg", "S1", "recepción, muro Oeste", "existente"),
    ("MF-02", "ABC 10 kg", "S1", "recepción, junto a P1", "existente"),
    ("MF-03", "ABC 10 kg", "S1", "recepción, muro Sur", "existente"),
    ("MF-04", "ABC 10 kg", "S1", "taller de mantenimiento", "existente"),
    ("MF-05", "ABC 10 kg", "S1", "vestuario y oficina", "existente"),
    ("MF-06", "ABC 10 kg", "S1", "muro Norte, frente al secador", "existente"),
    ("MF-07", "ABC 10 kg", "S1", "zaranda y envasado", "existente"),
    ("MF-08", "ABC 10 kg", "S1", "muro Este, junto a P3", "existente"),
    ("MF-09", "CO2 5 kg", "S1", "junto al TGF (art. 178, clase C)", "nuevo"),
    ("MF-10", "Agua 10 l", "S1", "acopio de producto seco (clase A)", "nuevo"),
    ("MF-11", "ABC 10 kg", "S2", "acceso Norte del anexo", "nuevo"),
    ("MF-12", "ABC 10 kg", "S2", "ventiladores de impulsión", "nuevo"),
    ("MF-13", "ABC 10 kg (gab.)", "S3", "silo de cáscara", "nuevo"),
    ("MF-14", "ABC 10 kg (gab.)", "ext", "ciclón y lavador de gases", "nuevo"),
    ("MF-15", "ABC 10 kg", "S4", "depósito, junto al portón", "nuevo"),
    ("MF-16", "ABC 10 kg", "S4", "depósito, salida de emergencia SE3", "nuevo"),
    ("MF-17", "ABC 10 kg", "S4", "depósito, muro Norte", "nuevo"),
    ("MF-18", "Agua 10 l", "S4", "depósito (clase A)", "nuevo"),
    ("MF-19", "ABC 50 kg rodante", "S5", "acceso a la zona de biogás", "nuevo"),
    ("MF-20", "CO2 5 kg", "S5", "sala de cogeneración", "nuevo"),
    ("MF-21", "ABC 10 kg (gab.)", "S5", "tanque de digestato y separador", "nuevo"),
    ("MF-22", "ABC 5 kg", "ext", "garita de control", "nuevo"),
    ("MF-23", "ABC 10 kg (gab.)", "ext", "estación de desinfección de vehículos", "nuevo"),
]


def tabla_mf(msp):
    subtitulo(msp, "MATAFUEGOS (IRAM 3517: control semestral y recarga anual)", 196.0, 224.8, 2.6)
    filas = [["Tag", "Tipo", "Sector", "Ubicación", "Estado"]] + [list(f) for f in MATAFUEGOS]
    tabla(msp, 196.0, 223.0, [15, 38, 12, 116, 17], filas, h_fila=3.05, altura=1.6)


NOTAS = [
    "1. Carga de fuego, riesgo y potencial extintor: ver plano 16. Sector Este (S4 depósito y S5 biogás): ver planos 13 y 20.",
    "2. Matafuegos colgados con la parte superior a ≤ 1,50 m del piso, con chapa baliza, tarjeta de control y cartel (IRAM 10005).",
    "3. Hidrantes con gabinete, manguera de 25 m y lanza de 45 mm; red en anillo con válvulas de bloqueo; bomba M25 alimentada",
    "desde el pilar antes del QG (alimentación exclusiva) y jockey M26 para mantener presión.",
    "4. Detección y alarma: central CI en la sala de control (22), aviso sonoro y luminoso en toda la planta; el pulsador corta el",
    "dosificador y la cáscara (enclavamiento con el PLC) y deja en marcha el extractor 5 min.",
    "5. Silo: rociadores con válvula de diluvio (VD) comandada por TS-01 (> 60 °C) y manual; sin agua en el hogar ni en el TGF.",
    "6. Puertas de egreso con apertura hacia afuera y barra antipánico; pasillos y salidas libres de pallets y bolsas (art. 172).",
]


def main():
    revs = [("D", "09/2026", "Emisión original: sectores, matafuegos, hidrantes, detección, escape, rociadores")]
    doc, msp, z = lamina(15, "PROTECCIÓN CONTRA INCENDIOS\nY ESCAPE", "1:250", revs)
    trazos(doc)
    titulo_vista(msp, "PROTECCIÓN CONTRA INCENDIOS Y MEDIOS DE ESCAPE (NAVE, ANEXO Y SILO) - ESC. 1:250", 26, 278, 3.5)
    planta(msp)
    seguridad(msp)
    norte(msp, 186.0, 141.0, 5.0)
    escala_grafica(msp, 26.0, 125.0, "1:250", 20, 5)
    leyenda(msp)
    tabla_mf(msp)
    subtitulo(msp, "NOTAS", 26.0, 113.5, 2.6)
    y = 110.0
    for r in NOTAS:
        t(msp, r, (26.0, y), 1.8, "TOP_LEFT")
        y -= 2.7
    exportar_lamina(doc, 15)


if __name__ == "__main__":
    main()
