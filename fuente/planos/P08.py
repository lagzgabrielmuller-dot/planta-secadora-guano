"""P08 - Corte general A-A (por el eje del secador, mirando al Norte) y vista Norte (exterior), 1:125.

Geometría: fuente/datos/layout_planta.json (clave G): nave, secador, cinta, tolva, sinfín, elevador,
ductos, anexo, silo, ciclón, lavador, extractor y chimeneas; camión tipo (G.camion).
"""
import json
import math
import os


from lamina_secadora import (fuente_pil, COL, FECHA, circulo, escala_grafica, exportar_lamina, factor, flecha,
                             lamina, linea, nivel, poli, rect, relleno, relleno_circulo, relleno_rect,
                             subtitulo, suelo, t, tn)
from lamina_a3 import cota

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

K = factor("1:125")
M = K * 1000.0                      # 8 mm de papel por metro
XA, ZA = 40.0, 204.4               # corte A-A: x = 0 (muro O), z = 0
XN, ZN = 40.0, 83.6                # vista Norte: x = 33 (muro E) a la izquierda, z = 0

VERDE, ROJO, GRIS = COL["aire_agotado"], COL["aire_caliente"], COL["humos"]
GRIS_CL = (130, 130, 130)
MARRON = (110, 90, 75)

# ---------------------------------------------------------------- helpers propios de la lámina
def ancho_texto(texto, h, negrita=True):
    return fuente_pil(negrita).getlength(texto) / 1000.0 * h / 0.716


def titulo(msp, texto, x, y, h=3.5):
    tn(msp, texto, (x, y), h, "BOTTOM_LEFT")
    largo = ancho_texto(texto, h)
    linea(msp, (x, y - 1.0), (x + largo, y - 1.0), "CONTORNO")
    linea(msp, (x, y - 1.8), (x + largo, y - 1.8), "FINO")


def rotulo(msp, texto, pos, h, alin="MIDDLE_LEFT", negrita=False):
    """Texto con fondo blanco (relleno) para que no lo crucen columnas ni nervios."""
    w = ancho_texto(texto, h, negrita)
    x, y = pos
    x0 = x - (w / 2 if "CENTER" in alin else w if "RIGHT" in alin else 0)
    y0 = y - (h / 2 if "MIDDLE" in alin else h if "TOP" in alin else 0)
    relleno_rect(msp, x0 - 0.6, y0 - 0.6, x0 + w + 0.6, y0 + h + 0.6, (255, 255, 255))
    (tn if negrita else t)(msp, texto, pos, h, alin)


def A(x, z):
    return (XA + x * M, ZA + z * M)


def N(x, z):
    """Vista Norte: el Este queda a la izquierda."""
    return (XN + (G["nave"]["L"] - x) * M, ZN + z * M)


def caja(msp, p, q, capa="CONTORNO", fill=None, color=None, lw=None):
    if fill:
        relleno_rect(msp, min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1]), fill)
    return rect(msp, p[0], p[1], q[0], q[1], capa, color, lw)


def persona(msp, P, x, h=1.75):
    """Figura humana de 1,75 m (referencia de escala)."""
    cab = P(x, h - 0.15)
    circulo(msp, cab, 0.15 * M, "CONTORNO", lw=50)
    poli(msp, [P(x - 0.25, h - 0.32), P(x + 0.25, h - 0.32), P(x + 0.12, 0), P(x - 0.12, 0)], "CONTORNO",
         cerrada=True, lw=50)
    linea(msp, P(x, 0), P(x, 0.9), "CONTORNO", lw=50)


# ---------------------------------------------------------------- corte A-A
def corte_aa(msp):
    nave = G["nave"]
    L = nave["L"]
    suelo(msp, 29.0, 313.0, ZA)
    # muros O y E (chapa) y columnas de los pórticos intermedios
    for x0, x1 in ((-0.2, 0.0), (L, L + 0.2)):
        caja(msp, A(x0, 0), A(x1, nave["h_alero"]), "CONTORNO", fill=(205, 205, 205), lw=50)
    for x in nave["porticos"]:
        for dx in (-0.15, 0.15):
            xx = min(max(x + dx, 0.0), L)
            if 0 < x < L or (x == 0 and dx > 0) or (x == L and dx < 0):
                linea(msp, A(xx, 0), A(xx, nave["h_alero"]), "CONTORNO", lw=50)
    # alero, cumbrera y cabriadas cortadas
    linea(msp, A(-0.2, nave["h_alero"]), A(L + 0.2, nave["h_alero"]), "CONTORNO", lw=70)
    for z in (nave["h_cumbrera"] - 0.08, nave["h_cumbrera"]):
        linea(msp, A(-0.42, z), A(L + 0.42, z), "CONTORNO", lw=70)
    for x in nave["porticos"]:
        linea(msp, A(x, nave["h_alero"]), A(x, nave["h_cumbrera"] - 0.08), "CONTORNO", lw=70)
        for z in (nave["h_alero"], nave["h_cumbrera"] - 0.08):
            c = A(x, z)
            relleno_rect(msp, c[0] - 1.1, c[1] - 1.1, c[0] + 1.1, c[1] + 1.1, (60, 60, 60))
    t(msp, "cabriada (cortada)", A(5.62, 7.65), 2.0, "MIDDLE_LEFT")

    # camión volcador (al fondo, en P1), con la cabina hacia el Oeste
    ca = G["camion"]
    xf = -0.9 - ca["eje_del"]                        # frente de la cabina
    poli(msp, [A(xf, 0.9), A(xf, 2.85), A(xf + 0.3, ca["H_cab"] - 0.04), A(-0.375, ca["H_cab"] - 0.04),
               A(-0.375, 1.16)], "CONTORNO", lw=50)
    caja(msp, A(-1.91, 1.95), A(-1.13, 2.73), "CONTORNO", lw=50)
    linea(msp, A(xf + 0.2, 1.16), A(5.25, 1.16), "CONTORNO", lw=50)
    linea(msp, A(xf, 0.9), A(5.4, 0.9), "CONTORNO", lw=50)
    for xr in (-0.9, -0.9 + ca["entre_ejes"]):
        c = A(xr, 0.51)
        relleno_circulo(msp, c, 0.51 * M, (255, 255, 255))
        circulo(msp, c, 0.51 * M, "CONTORNO", lw=50)
        circulo(msp, c, 0.24 * M, "CONTORNO", lw=50)
    poli(msp, [A(1.91, 5.29), A(2.71, 5.98), A(6.08, 1.98), A(5.25, 1.31)], "CONTORNO", cerrada=True, lw=50)
    linea(msp, A(0.04, 1.16), A(2.23, 5.05), "CONTORNO", lw=50)
    rotulo(msp, "camión volcador descargando (al fondo, en P1)", A(0.32, 6.37), 2.0)

    # tolva baja 2 (boca a +2,00) y muro de contención (al fondo)
    tv = G["tolva"]
    poli(msp, [A(tv["x0"], tv["z_boca"]), A(tv["ranura_x"][0], tv["z_ranura"]), A(tv["ranura_x"][1], tv["z_ranura"]),
               A(tv["x1"], tv["z_boca"])], "CONTORNO", lw=70)
    for x in tv["ranura_x"]:
        linea(msp, A(x, 0), A(x, tv["z_ranura"]), "CONTORNO", lw=50)
    t(msp, "rejilla", A(2.5, 2.3), 1.8, "BOTTOM_CENTER")
    tn(msp, "2", A(2.5, 1.39), 2.2, "MIDDLE_CENTER")
    mc = G["muro_contencion"]
    caja(msp, A(mc["x"], 0), A(mc["x"] + mc["e"], mc["h"] - 0.16), "CONTORNO", lw=50)

    # cinta con tacos a 30° (perfil del modelo), tambores y apoyos
    ci = G["cinta"]
    perfil = ci["perfil"]
    poli(msp, [A(x, z) for x, z in perfil], "CONTORNO", lw=100)
    ret = []
    for i, (x, z) in enumerate(perfil):
        j = min(i + 1, len(perfil) - 1)
        k = max(i - 1, 0)
        dx, dz = perfil[j][0] - perfil[k][0], perfil[j][1] - perfil[k][1]
        d = math.hypot(dx, dz) or 1.0
        ret.append(A(x + dz / d * 0.38, z - dx / d * 0.38))
    poli(msp, ret[3:], "CONTORNO", lw=50)
    for i in range(1, 12):           # tacos
        x0 = ci["x_cola"] + 0.25 + i * 0.35
        linea(msp, A(x0, ci["z_carga"]), A(x0, ci["z_carga"] + 0.05), "CONTORNO", lw=50)
    for i in range(5):               # tacos de la curva (en marrón, como el guano)
        x, z = perfil[22 + i]
        linea(msp, A(x - 0.05, z + 0.25), A(x + 0.25, z - 0.6), "FINO", color=MARRON, lw=50)
    relleno_circulo(msp, A(ci["x_cola"], ci["z_carga"] - 0.13), ci["D_cola"] / 2 * M, (255, 255, 255))
    circulo(msp, A(ci["x_cola"], ci["z_carga"] - 0.13), ci["D_cola"] / 2 * M, "CONTORNO", lw=70)
    caja(msp, A(ci["x_cabeza"] - 0.2, ci["z_cabeza"] - 0.37), A(ci["x_cabeza"] + 0.2, ci["z_cabeza"]), "CONTORNO", lw=100)
    circulo(msp, A(ci["x_cabeza"], ci["z_cabeza"] - 0.18), ci["D_motriz"] / 2 * M, "CONTORNO", lw=70)
    # campana de alimentación sobre el secador
    poli(msp, [A(11.85, 3.8), A(11.85, 4.85), A(12.64, 4.85), A(12.6, 3.42)], "CONTORNO", lw=50)
    for xa in ci["apoyos_x"]:
        z = next(z for x, z in perfil if x >= xa)
        linea(msp, A(xa, 0), A(xa, max(z - 0.45, 0.2)), "CONTORNO", lw=50)
    poli(msp, [A(6.41, 1.45), A(7.28, 1.41), A(9.19, 0.21)], "CONTORNO", lw=50)
    t(msp, "cinta con tacos a 30°", A(6.4, 3.2), 1.9, "MIDDLE_LEFT")
    tn(msp, "3", A(9.55, 3.2), 2.2, "MIDDLE_LEFT")

    # secador de 3 pisos 4
    se = G["secador"]
    x0, x1 = se["x0"], se["x0"] + se["L"]
    relleno_rect(msp, *A(x0, se["h_patas"]), *A(x1, se["H"]), (255, 255, 255))
    linea(msp, A(x0, se["h_patas"]), A(x0, se["H"]), "CONTORNO", lw=50)
    linea(msp, A(x1, se["h_patas"]), A(x1, se["H"]), "CONTORNO", lw=50)
    for z in (se["h_patas"], se["H"]):
        linea(msp, A(x0, z), A(x1, z), "CONTORNO", color=(150, 150, 150), lw=100)
    for xc in se["columnas_x"]:
        linea(msp, A(x0 + xc, 0), A(x0 + xc, se["h_patas"]), "CONTORNO", lw=50)
    for p in se["pisos"]:
        zc = p["zc"] - 0.16
        rc, rk = se["r_motriz"], se["r_reenvio"]
        cab, col = p["cabeza"], p["cola"]
        for xx, r in ((cab, rc), (col, rk)):
            relleno_circulo(msp, A(x0 + xx, zc), r * M, (255, 255, 255))
            circulo(msp, A(x0 + xx, zc), r * M, "CONTORNO", lw=70)
        linea(msp, A(x0 + col, zc + rk), A(x0 + cab, zc + rc), "CONTORNO", lw=70)
        linea(msp, A(x0 + col, zc - rk), A(x0 + cab, zc - rc), "CONTORNO", lw=70)
        xa, xb = 17.45, 18.45
        if p["sentido"] < 0:
            xa, xb = xb, xa
        flecha(msp, A(xa, p["zc"] + 0.27), A(xb, p["zc"] + 0.27), "CONTORNO", color=MARRON, tam=1.4, lw=70)
    rotulo(msp, "4", A(14.5, 1.39), 2.2, "MIDDLE_CENTER", negrita=True)
    persona(msp, A, 19.3)
    # sinfín de descarga 6, elevador 7 con pico al acopio, puerta RF-60 (al fondo)
    sd, el = G["sinfin_desc"], G["elevador"]
    caja(msp, A(sd["x0"] - 0.1, 0.06), A(el["x"] - el["ax"] / 2, 0.35), "CONTORNO", fill=(255, 255, 255), lw=50)
    linea(msp, A(sd["x0"] - 0.1, 0.25), A(sd["x0"] + 0.4, 0.25), "CONTORNO", lw=50)
    tn(msp, "6", A(24.9, 0.55), 2.0, "BOTTOM_CENTER")
    caja(msp, A(el["x"] - el["ax"] / 2, 0), A(el["x"] + el["ax"] / 2, 6.25), "CONTORNO", lw=50)
    caja(msp, A(el["x"] - 0.3, 6.25), A(el["x"] + 0.53, 6.76), "CONTORNO", fill=(255, 255, 255), lw=70)
    rotulo(msp, "pico al acopio (hacia el Sur)", A(26.45, 6.5), 2.0)
    tn(msp, "7", A(26.48, 3.43), 2.2, "MIDDLE_LEFT")
    caja(msp, A(26.2, 0), A(27.2, 2.1), "CONTORNO", lw=50)
    t(msp, "RF-60", A(26.7, 2.4), 1.8, "BOTTOM_CENTER")
    # ducto de aire agotado 17 (verde) y ducto caliente 12 (rojo, en corte)
    ag = G["ducto_agotado"]
    r = ag["D"] / 2
    caja(msp, A(14.5 - r, se["H"]), A(14.5 + r, 6.5 + r), "CONTORNO", color=VERDE, lw=70)
    linea(msp, A(14.5 - r, 6.5 - r), A(14.5 + r, 6.5 - r), "CONTORNO", color=VERDE, lw=70)
    circulo(msp, A(14.5, 6.5), (r - 0.02) * M, "CONTORNO", lw=70)
    flecha(msp, A(14.5, 4.5), A(14.5, 5.5), "CONTORNO", color=VERDE, tam=1.4, lw=70)
    rotulo(msp, "17 al ciclón (hacia el Norte)", A(15.05, 6.5), 2.0)
    dc = G["ducto_caliente"]
    p, q = A(dc["x0"], 3.2), A(dc["x1"], 3.8)
    rect(msp, p[0], p[1], q[0], q[1], "CONTORNO", color=ROJO, lw=70)
    linea(msp, p, q, "CONTORNO", color=ROJO, lw=70)
    linea(msp, (p[0], q[1]), (q[0], p[1]), "CONTORNO", color=ROJO, lw=70)
    tn(msp, "12", A(23.3, 3.5), 2.0, "MIDDLE_LEFT")

    # niveles
    xn = 312.0
    for z, txt in ((8.35, "+8,35"), (7.0, "+7,00"), (6.30, "+6,30"), (4.35, "+4,35"), (3.40, "+3,40"), (0.0, "±0,00")):
        nivel(msp, xn, A(0, z)[1], txt)
    # cotas
    for a, b in ((0, 1.21), (1.21, se["x0"]), (se["x0"], x1), (x1, L)):
        cota(msp, A(a, 0), A(b, 0), distancia=-6.1, escala=K)
    cota(msp, A(0, 0), A(L, 0), distancia=-11.8, escala=K)


# ---------------------------------------------------------------- vista Norte
def ladrillos(msp, x0, y0, x1, y1, alto=0.3 * M, largo=0.6 * M):
    """Mampostería vista: hiladas de 0,30 m con juntas trabadas."""
    relleno_rect(msp, x0, y0, x1, y1, (225, 205, 175))
    n = int((y1 - y0) / alto) + 1
    for i in range(n + 1):
        y = y0 + i * alto
        if y < y1:
            linea(msp, (x0, y), (x1, y), "CONTORNO", lw=35)
        ya, yb = y, min(y + alto, y1)
        if yb <= ya:
            continue
        x = x0 + (largo / 2 if i % 2 else largo * 0.15)
        while x < x1 - 0.3:
            linea(msp, (x, ya), (x, yb), "CONTORNO", lw=35)
            x += largo


def vista_norte(msp):
    nave = G["nave"]
    L = nave["L"]
    suelo(msp, 27.0, 307.0, ZN)
    # nave: faldón de cubierta (7,00 a 8,35) con nervios y muro Norte de chapa
    relleno_rect(msp, 33.0, N(0, nave["h_alero"])[1], 305.4, N(0, nave["h_cumbrera"])[1], (236, 236, 236))
    rect(msp, 33.0, N(0, nave["h_alero"])[1], 305.4, N(0, nave["h_cumbrera"])[1], "CONTORNO", lw=70)
    x = 33.0 + 2.6
    while x < 305.0:
        linea(msp, (x, N(0, nave["h_alero"])[1]), (x, N(0, nave["h_cumbrera"])[1]), "CONTORNO", color=GRIS_CL, lw=50)
        x += 4.0
    for i in range(int(L) + 1):
        xx = L - i
        linea(msp, N(xx, 0.05), N(xx, nave["h_alero"] - 0.1), "CONTORNO", color=GRIS_CL, lw=50)
    linea(msp, N(0, 0), N(0, nave["h_alero"]), "CONTORNO", lw=50)
    rotulo(msp, "NAVE 33 x 18 m (cerramiento de chapa)", N(5.4, 4.08), 2.2, "MIDDLE_CENTER", negrita=True)

    # silo de cáscara 13 con caño de carga
    si = G["silo"]
    r = si["D"] / 2
    zc0 = si["z_boca"] + si["h_cono"]
    zc1 = zc0 + si["h_cil"]
    caja(msp, N(si["x"] + r + 0.3, 0.34), N(si["x"] + r + 0.72, zc1 + 0.36), "CONTORNO", fill=(255, 255, 255), lw=70)
    linea(msp, N(si["x"] + r + 0.62, 0), N(si["x"] + r + 0.62, 0.34), "CONTORNO", lw=50)
    caja(msp, N(si["x"] + r, zc0), N(si["x"] - r, zc1), "CONTORNO", fill=(220, 225, 230), lw=70)
    relleno(msp, [N(si["x"] + r, zc0), N(si["x"] - r, zc0), N(si["x"] - 0.16, si["z_boca"]), N(si["x"] + 0.16, si["z_boca"])],
            (255, 255, 255))
    poli(msp, [N(si["x"] + r, zc0), N(si["x"] + 0.16, si["z_boca"]), N(si["x"] - 0.16, si["z_boca"]), N(si["x"] - r, zc0)],
         "CONTORNO", lw=70)
    poli(msp, [N(si["x"] + r, zc1), N(si["x"], zc1 + si["h_techo"]), N(si["x"] - r, zc1)], "CONTORNO", lw=70)
    for k in range(1, 6):
        linea(msp, N(si["x"] + r, zc0 + k), N(si["x"] - r, zc0 + k), "CONTORNO", color=GRIS_CL, lw=50)
    for dx in (-1.25, 1.25):
        linea(msp, N(si["x"] + dx, 0), N(si["x"] + dx, zc0 + 0.2), "CONTORNO", lw=70)
    linea(msp, N(si["x"] + 1.25, 2.64), N(si["x"] - 1.25, 0.65), "CONTORNO", lw=70)
    linea(msp, N(si["x"] - 1.25, 2.64), N(si["x"] + 1.25, 0.65), "CONTORNO", lw=70)
    tn(msp, "13", N(si["x"], 7.04), 2.4, "MIDDLE_CENTER")
    rotulo(msp, "SILO 70 m³", N(si["x"], 6.25), 1.9, "MIDDLE_CENTER")

    # anexo del generador (mampostería vista) con acceso de 2 hojas
    an = G["anexo"]
    p, q = N(an["x1"] + 0.2, 0), N(an["x0"] - 0.2, an["h"] + 0.18)
    ladrillos(msp, p[0], p[1], q[0], q[1])
    a, b = N(25.2, 0), N(24.0, 2.15)
    caja(msp, a, b, "CONTORNO", fill=(255, 255, 255), lw=70)
    rect(msp, p[0], p[1], q[0], q[1], "CONTORNO", lw=70)
    rotulo(msp, "acceso", ((a[0] + b[0]) / 2, b[1] + 1.2), 1.8, "BOTTOM_CENTER")
    rotulo(msp, "ANEXO GENERADOR", (93.8, N(0, 4.35)[1]), 2.2, "MIDDLE_CENTER", negrita=True)
    persona(msp, N, 26.1)

    # chimenea del hogar 15 (h = 12 m) con sombrerete y plataforma de toma de muestra
    ch = an["chimenea"]
    cr = ch["D"] / 2
    caja(msp, N(ch["x"] + cr, 0), N(ch["x"] - cr, ch["h"]), "CONTORNO", fill=(170, 170, 170), lw=70)
    poli(msp, [N(ch["x"] + 0.62, 12.4), N(ch["x"], 12.66), N(ch["x"] - 0.62, 12.4)], "CONTORNO", cerrada=True, lw=70)
    caja(msp, N(ch["x"] + 0.62, 7.85), N(ch["x"] - 0.62, 7.95), "CONTORNO", fill=(255, 255, 255), lw=50)
    tn(msp, "15", N(ch["x"] - 0.5, 10.94), 2.2, "MIDDLE_LEFT")
    t(msp, "chimenea Ø500", N(ch["x"] - 0.34, 10.24), 1.8, "MIDDLE_LEFT")
    t(msp, "toma de muestra", N(ch["x"] + 0.45, 8.75), 1.8, "MIDDLE_RIGHT")

    # lavador 19, extractor 20, chimenea del lavador, ducto Ø800, ciclón 18 y descarga 21
    sc, ex, cy = G["scrubber"], G["extractor"], G["ciclon"]
    rs = sc["D"] / 2
    caja(msp, N(ex["chim_x"] + 0.45, 0.35), N(sc["x"] - rs, 0.48), "CONTORNO", lw=50)
    caja(msp, N(sc["x"] + rs, sc["z0"]), N(sc["x"] - rs, sc["z1"]), "CONTORNO", fill=(225, 236, 226), lw=70)
    poli(msp, [N(sc["x"] + rs, sc["z1"]), N(sc["x"] + 0.55, sc["z1"] + 0.45), N(sc["x"] - 0.55, sc["z1"] + 0.45),
               N(sc["x"] - rs, sc["z1"])], "CONTORNO", lw=70)
    # ducto del lavador al extractor (verde)
    for xx in (sc["x"] + 0.3, sc["x"] - 0.3):
        linea(msp, N(xx, 1.56), N(xx, nave["h_alero"]), "CONTORNO", color=VERDE, lw=70)
    linea(msp, N(sc["x"] + 0.3, nave["h_alero"]), N(sc["x"] - 0.3, nave["h_alero"]), "CONTORNO", color=VERDE, lw=70)
    # chimenea del lavador (h = 10 m)
    cc = ex["chim_D"] / 2
    caja(msp, N(ex["chim_x"] + cc, 0.45), N(ex["chim_x"] - cc, ex["chim_h"]), "CONTORNO", fill=(210, 210, 210), lw=70)
    # extractor 20
    caja(msp, N(sc["x"] + 0.6, 0.06), N(sc["x"] - 0.6, 1.56), "CONTORNO", fill=(240, 240, 240), lw=70)
    relleno_circulo(msp, N(sc["x"], 0.85), 0.5 * M, (240, 240, 240))
    circulo(msp, N(sc["x"], 0.85), 0.5 * M, "CONTORNO", lw=70)
    tn(msp, "20", N(sc["x"], 0.85), 1.9, "MIDDLE_CENTER")
    linea(msp, N(ex["chim_x"] - cc, 0.97), N(sc["x"] + 0.6, 0.97), "CONTORNO", color=VERDE, lw=70)
    tn(msp, "19", N(sc["x"], 4.1), 2.4, "MIDDLE_CENTER")
    rotulo(msp, "LAVADOR", N(sc["x"], 3.3), 1.8, "MIDDLE_CENTER")
    # ducto Ø800 del ciclón al lavador
    dl = [N(16.2, 0.6), N(16.2, 7.9), N(14.1, 7.9), N(14.1, 6.9), N(14.9, 6.9), N(14.9, 7.1), N(15.4, 7.1), N(15.4, 0.6)]
    relleno(msp, dl, (213, 222, 218))
    poli(msp, dl, "CONTORNO", cerrada=True, color=VERDE, lw=70)
    t(msp, "Ø800", N(15.8, 3.6), 1.8, "MIDDLE_CENTER", rotacion=90)
    # ciclón 18 y tolva/rotativa 21
    rc = cy["D"] / 2
    caja(msp, N(cy["x"] + rc, cy["z_cil0"]), N(cy["x"] - rc, cy["z_cil1"]), "CONTORNO", fill=(230, 230, 235), lw=70)
    cono = [N(cy["x"] + rc, cy["z_cil0"]), N(cy["x"] + 0.3, 2.04), N(cy["x"] - 0.3, 2.04), N(cy["x"] - rc, cy["z_cil0"])]
    relleno(msp, cono, (230, 230, 235))
    poli(msp, cono, "CONTORNO", lw=70)
    for dx in (rc - 0.1, -rc + 0.05):
        linea(msp, N(cy["x"] + dx, 2.04), N(cy["x"] + dx, cy["z_cil0"] + 0.1), "CONTORNO", lw=70)
    relleno_circulo(msp, N(cy["x"] + 0.1, 6.5), 0.42 * M, (255, 255, 255))
    circulo(msp, N(cy["x"] + 0.1, 6.5), 0.42 * M, "CONTORNO", lw=70)
    caja(msp, N(cy["x"] + 0.95, 0.06), N(cy["x"] - 0.85, 2.04), "CONTORNO", fill=(235, 242, 250), lw=70)
    tn(msp, "18", N(cy["x"] + 0.1, 5.45), 2.4, "MIDDLE_CENTER")
    tn(msp, "21", N(cy["x"] + 0.2, 1.05), 2.2, "MIDDLE_CENTER")

    tn(msp, "ESTE", (26.5, 86.5), 2.0, "MIDDLE_LEFT")
    tn(msp, "OESTE", (N(0, 0)[0] + 1.5, 86.5), 2.0, "MIDDLE_LEFT")
    # niveles
    xn = 314.0
    for z, txt in ((12.0, "+12,00"), (10.70, "+10,70"), (10.0, "+10,00"), (8.35, "+8,35"), (7.0, "+7,00"),
                   (4.95, "+4,95")):
        nivel(msp, xn, N(0, z)[1], txt)


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Lám. nueva: alturas nave/equipos ext. B1: cinta c/tacos, camión volcando, pala"),
            ("C", "09/2026", "Puerta RF-60 a x 26,2-27,2 (como plano 01); rótulos c/fondo sobre las columnas"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    for r in revs:
        assert len(r[2]) <= 80, (len(r[2]), r[2])
    doc, msp, z = lamina(8, "CORTE GENERAL A-A Y VISTA NORTE", "1:125", revs)
    titulo(msp, "CORTE A-A (por el eje del secador, mirando al Norte)  -  ESC. 1:125", 25, 279.5, 3.6)
    corte_aa(msp)
    titulo(msp, "VISTA NORTE (exterior)  -  ESC. 1:125", 25, 185.4, 3.6)
    vista_norte(msp)
    subtitulo(msp, "NOTAS", 25, 67.8, 2.6)
    for k, r in enumerate([
        "- La tolva baja (boca a +2,00) se carga con pala; la cinta con tacos sube a 30° y descarga por el techo del secador.",
        "- Rev. A: la tolva estaba a +4,30 m (no se podía cargar). B1: el sinfín se cambió por cinta (el guano húmedo resbalaba).",
        "- Ciclón (5,4 m) y lavador (6,0 m) no entraban bajo la cabriada (+7,00): ahora están al exterior.",
        "- Chimeneas por encima de la cumbrera (+8,35) para buena dispersión.",
        "- Figura humana de 1,75 m como referencia de escala.",
    ]):
        t(msp, r, (25, 65.0 - k * 3.2), 1.9, "MIDDLE_LEFT")
    escala_grafica(msp, 109.8, 31.0, "1:125", 10, 2)
    exportar_lamina(doc, 8)


if __name__ == "__main__":
    main()
