"""P01 - Implantación y distribución en planta de la nave de proceso (1:150).

Geometría en metros desde fuente/datos/layout_planta.json (origen en el vértice SO de la nave,
x al Este, y al Norte). Los textos, globos y la distribución de la hoja copian la lámina Rev. C.
"""
import json
import math
import os

from lamina_secadora import (FECHA, arco, circulo, cota, escala_grafica, exportar_lamina,
                             factor, flecha, flecha_poli, globo, lamina, linea, norte, poli, rayado,
                             rect, relleno, relleno_circulo, relleno_rect, subtitulo, t,
                             tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

ESC = "1:150"
k = factor(ESC)                 # mm reales -> mm de papel
KM = k * 1000.0                 # metros -> mm de papel
OX, OY = 60.3, 104.5            # vértice SO de la nave en la hoja (igual que la Rev. C)

ROJO_EJE = (220, 0, 0)
C_PLAYA = (236, 222, 200)
C_SECTOR = (246, 238, 226)
C_ACOPIO = (240, 232, 214)
C_PALA = (255, 236, 170)
C_PUESTO = (255, 214, 64)
C_RUEDA = (60, 60, 60)
C_GRIS = (231, 230, 229)
C_LIX = (104, 148, 156)          # lixiviados / solución
C_COMB = (90, 150, 160)          # aire de combustión
C_HUMOS = (77, 77, 77)
C_GUANO = (136, 92, 48)
C_CAL = (190, 40, 40)
C_AGOT = (40, 140, 90)


def M(x, y):
    """Metros del modelo -> mm de papel."""
    return (OX + x * KM, OY + y * KM)


def D(px, py):
    """Coordenadas de la Rev. C vista a 2000 px de ancho -> mm de papel (para ubicar textos y globos)."""
    s = 3307 / 2000 / (3307 / 420)
    return (px * s, 297 - py * s)


def rect_m(msp, x0, y0, x1, y1, capa="CONTORNO", color=None, lw=None):
    return rect(msp, *M(x0, y0), *M(x1, y1), capa, color, lw)


def relleno_m(msp, x0, y0, x1, y1, rgb):
    return relleno_rect(msp, *M(x0, y0), *M(x1, y1), rgb)


def muro(msp, x0, y0, x1, y1, patron="ANSI31"):
    """Muro en planta (corte): contorno grueso y rayado."""
    a, b = M(x0, y0), M(x1, y1)
    pts = [a, (b[0], a[1]), b, (a[0], b[1])]
    relleno(msp, pts, (255, 255, 255))
    if patron == "ANSI31":
        rayado(msp, pts, escala=0.12)
    else:
        rayado(msp, pts, escala=0.03, patron=patron, angulo=0)
    poli(msp, pts, "CONTORNO", cerrada=True)


def muro_con_vanos(msp, eje, fijo, a, b, e, vanos, hacia, patron="ANSI31"):
    """Muro recto entre a y b (sobre x si eje='x', sobre y si eje='y') con vanos [(a, b), ...].
    hacia: +1 si el espesor crece hacia + desde 'fijo', -1 hacia -."""
    cortes = sorted(vanos)
    tramos, p = [], a
    for va, vb in cortes:
        if va > p:
            tramos.append((p, va))
        p = max(p, vb)
    if p < b:
        tramos.append((p, b))
    for p0, p1 in tramos:
        f0, f1 = sorted((fijo, fijo + hacia * e))
        if eje == "x":
            muro(msp, p0, f0, p1, f1, patron)
        else:
            muro(msp, f0, p0, f1, p1, patron)


def puesto(msp, n, c, s=3.4):
    x, y = c
    pts = [(x, y + s), (x + s, y), (x, y - s), (x - s, y)]
    relleno(msp, pts, C_PUESTO)
    poli(msp, pts, "CONTORNO", cerrada=True)
    tn(msp, str(n), (x, y), s * 0.62, "MIDDLE_CENTER")


def puesto_ley(msp, n, c, s=1.9):
    x, y = c
    pts = [(x, y + s), (x + s, y), (x, y - s), (x - s, y)]
    relleno(msp, pts, (0, 0, 0))
    pi = [(x, y + s * 0.7), (x + s * 0.7, y), (x, y - s * 0.7), (x - s * 0.7, y)]
    relleno(msp, pi, C_PUESTO)
    tn(msp, str(n), (x, y), 1.8, "MIDDLE_CENTER")


def puerta(msp, bisagra, radio, a0, a1):
    """Puerta batiente: hoja recta (en a0) y arco de giro de a0 a a1 (grados)."""
    c = M(*bisagra)
    r = radio * KM
    hx, hy = c[0] + r * math.cos(math.radians(a0)), c[1] + r * math.sin(math.radians(a0))
    linea(msp, c, (hx, hy), "FINO")
    arco(msp, c, r, min(a0, a1), max(a0, a1), "FINO")


def camion(msp, x_frente, yc):
    """Camión volcador rígido de 2 ejes entrando marcha atrás (frente hacia el Oeste)."""
    cm = G["camion"]
    A = cm["A"]
    x0 = x_frente
    # ruedas
    for e in (cm["eje_del"], cm["eje_tras"]):
        for s in (-1, 1):
            relleno_m(msp, x0 + e - 0.55, yc + s * A / 2 - 0.22, x0 + e + 0.55, yc + s * A / 2 + 0.22, C_RUEDA)
            rect_m(msp, x0 + e - 0.55, yc + s * A / 2 - 0.22, x0 + e + 0.55, yc + s * A / 2 + 0.22, "FINO")
    # cabina
    relleno_m(msp, x0 + 0.1, yc - A / 2 + 0.15, x0 + 2.05, yc + A / 2 - 0.15, (250, 250, 250))
    rect_m(msp, x0 + 0.1, yc - A / 2 + 0.15, x0 + 2.05, yc + A / 2 - 0.15)
    rect_m(msp, x0 + 0.35, yc - A / 2 + 0.4, x0 + 1.25, yc + A / 2 - 0.4, "FINO")
    # caja volcadora con chevrones
    c0, c1 = x0 + cm["caja"][0], x0 + cm["caja"][1]
    relleno_m(msp, c0, yc - A / 2, c1, yc + A / 2, (250, 250, 250))
    rect_m(msp, c0, yc - A / 2, c1, yc + A / 2)
    rect_m(msp, c0 + 0.12, yc - A / 2 + 0.12, c1 - 0.12, yc + A / 2 - 0.12, "FINO")
    for i in range(5):
        xa = c0 + 0.6 + i * 0.95
        poli(msp, [M(xa + 0.45, yc + 0.8), M(xa, yc), M(xa + 0.45, yc - 0.8)], "CONTORNO")
    rect_m(msp, x0 + 2.05, yc - 0.9, c0, yc + 0.9, "FINO")
    return c1


def pala(msp):
    """Pala cargadora frente a la tolva (cuchara hacia el Oeste)."""
    # cuchara
    relleno_m(msp, 4.1, 10.0, 4.85, 12.4, C_GRIS)
    rect_m(msp, 4.1, 10.0, 4.85, 12.4)
    linea(msp, M(4.85, 10.7), M(5.25, 10.7), "CONTORNO")
    linea(msp, M(4.85, 11.7), M(5.25, 11.7), "CONTORNO")
    # cuerpo delantero y trasero articulados
    for x0, x1 in ((5.25, 6.95), (7.15, 9.4)):
        relleno_m(msp, x0, 10.25, x1, 12.15, C_PALA)
        rect_m(msp, x0, 10.25, x1, 12.15)
    rect_m(msp, 6.95, 10.9, 7.15, 11.5, "FINO")
    for xc in (6.0, 8.1):
        for y0 in (9.85, 12.0):
            relleno_m(msp, xc - 0.75, y0, xc + 0.75, y0 + 0.45, C_RUEDA)
            rect_m(msp, xc - 0.75, y0, xc + 0.75, y0 + 0.45, "FINO")


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Anexo generador; ciclón y lavador afuera; P1 al NO; muro, tacos, puestos"),
            ("C", "09/2026", "Puerta RF-60 al anexo a x 26,2-27,2 (chocaba con pórtico 6); textos"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    doc, msp, z = lamina(1, "IMPLANTACIÓN Y DISTRIBUCIÓN EN PLANTA", ESC, revs)
    tit = "IMPLANTACIÓN Y DISTRIBUCIÓN EN PLANTA  -  ESC. 1:150"
    tn(msp, tit, (28, 279), 3.8, "BOTTOM_LEFT")
    largo = 0.775 * 3.8 * len(tit)
    linea(msp, (28, 278.0), (28 + largo, 278.0), "CONTORNO")
    linea(msp, (28, 277.2), (28 + largo, 277.2), "FINO")
    norte(msp, 43.8, 258.0, 6.3)

    nave = G["nave"]
    L, A = nave["L"], nave["A"]
    e = 0.2

    # ------------------------------------------------ superficies (rellenos primero)
    relleno_m(msp, 0, 0, 9.5, A, C_SECTOR)
    relleno_m(msp, 0.3, 11.55, 9.4, A - e, C_PLAYA)
    relleno_m(msp, 26, 0, L, 9, C_ACOPIO)
    pg = G["pila_guano"]
    relleno_circulo(msp, M(pg["x"], pg["y"]), pg["r"] * KM, C_PLAYA)

    # ------------------------------------------------ ejes de pórticos (1-7) y de muros (A, B)
    for i, xp in enumerate(nave["porticos"], start=1):
        p = M(xp, 0)
        linea(msp, (p[0], p[1] - 2), (p[0], 89.6), color=ROJO_EJE, capa="EJES")
        circulo(msp, (p[0], 85.8), 3.6, "CONTORNO")
        tn(msp, str(i), (p[0], 85.8), 3.2, "MIDDLE_CENTER")
    for letra, yy in (("A", 0), ("B", A)):
        p = M(L, yy)
        linea(msp, (p[0] + 1, p[1]), (288.8, p[1]), color=ROJO_EJE, capa="EJES")
        circulo(msp, (292.4, p[1]), 3.6, "CONTORNO")
        tn(msp, letra, (292.4, p[1]), 3.2, "MIDDLE_CENTER")

    # ------------------------------------------------ muros de la nave (e = 0,20 m, hacia adentro)
    pt = {p["id"]: p for p in G["portones"]}
    pu = {p["id"]: p for p in G["puertas"]}
    muro_con_vanos(msp, "x", 0, 0, L, e, [(pt["P2"]["a"], pt["P2"]["b"]), (pu["PP1"]["a"], pu["PP1"]["b"])], +1)
    muro_con_vanos(msp, "x", A, 0, L, e, [(pu["PC1"]["a"], pu["PC1"]["b"]),
                                          (G["ducto_caliente"]["x0"], G["ducto_caliente"]["x1"])], -1)
    muro_con_vanos(msp, "y", 0, e, A - e, e, [(pt["P1"]["a"], pt["P1"]["b"]), (pu["SE2"]["a"], pu["SE2"]["b"])], +1)
    muro_con_vanos(msp, "y", L, e, A - e, e, [(pu["SE1"]["a"], pu["SE1"]["b"])], -1)
    # columnas de los pórticos
    for xp in nave["porticos"]:
        xc = min(max(xp, 0.2), L - 0.2)
        for yc in (0.1, A - 0.1):
            relleno_m(msp, xc - 0.2, yc - 0.2, xc + 0.2, yc + 0.2, (40, 40, 40))
    # puertas
    puerta(msp, (pu["PP1"]["a"], 0), 1.0, 270, 360)                   # acceso personal, abre afuera
    puerta(msp, (0, pu["SE2"]["a"]), 1.2, 180, 90)                    # salida de emergencia O
    puerta(msp, (L, pu["SE1"]["a"]), 1.2, 0, 90)                      # salida de emergencia E
    puerta(msp, (pu["PC1"]["a"], A), 1.0, 270, 360)                   # RF-60 al anexo
    # portón P2 corredizo (hoja estacionada afuera)
    rect_m(msp, 28.0, -0.5, 30.2, -0.35, "CONTORNO")
    t(msp, "P2 (4,0 m)", M(29.1, -1.1), 1.8, "MIDDLE_CENTER")

    # ------------------------------------------------ locales sobre el muro Sur
    loc = G["locales"]
    linea(msp, M(9.5, 5), M(26, 5))
    for l in loc:
        linea(msp, M(l["x0"], e), M(l["x0"], 5))
    linea(msp, M(26, e), M(26, 5))
    for xb in (11.0, 15.05, 20.05, 22.75):          # puertas de los locales al pasillo
        puerta(msp, (xb, 5), 0.9, 90, 0)
    linea(msp, M(23.9, 5), M(26.0, 5), "CONTORNO", lw=100)   # ventana de la sala de control
    t(msp, "ventana", D(1078, 747), 1.8, "MIDDLE_CENTER")
    nombres = {25: ("25  DEPÓSITO DE", "REPUESTOS"), 23: ("23  TALLER", None),
               24: ("24  VESTUARIO,", "BAÑOS Y OFICINA"), 22: ("22  SALA", "DE CONTROL")}
    for l in loc:
        xc = (l["x0"] + l["x1"]) / 2
        if l["n"] == 24:
            xc = 21.3      # el texto no cruza la senda peatonal (x = 19,5)
        a, b = nombres[l["n"]]
        hl = 1.5 if l["n"] == 24 else 1.7
        if l["n"] == 24:
            xc = 20.98
        if b:
            tn(msp, a, M(xc, 3.9), hl, "MIDDLE_CENTER")
            tn(msp, b, M(xc, 3.15), hl, "MIDDLE_CENTER")
        else:
            tn(msp, a, M(xc, 3.5), 1.7, "MIDDLE_CENTER")

    # ------------------------------------------------ separaciones de reserva y acopio
    linea(msp, M(26, 9), M(26, A - e))
    linea(msp, M(31.7, 9), M(31.7, A - e))
    t(msp, "S.E.", M(32.35, 15.7), 1.8, "MIDDLE_CENTER")
    for m in G["muros_acopio"]:
        if m["y0"] == m["y1"]:
            muro(msp, m["x0"], m["y0"] - 0.1, m["x1"] - e, m["y0"] + 0.1, "AR-CONC")
        else:
            muro(msp, m["x0"] - 0.1, m["y0"], m["x0"] + 0.1, m["y1"] - 0.1, "AR-CONC")
    t(msp, "muro H° h = 2,0 m", M(29.4, 9.6), 1.6, "MIDDLE_CENTER")
    tn(msp, "28  RESERVA 2ª ETAPA", M(28.55, 13.3), 1.8, "MIDDLE_CENTER")
    t(msp, "(peletizado y ensacado)", M(28.55, 12.3), 1.6, "MIDDLE_CENTER")

    # ------------------------------------------------ acopio de producto seco (8)
    ps = G["pila_seca"]
    circulo(msp, M(ps["x"], ps["y"]), ps["r"] * KM)
    circulo(msp, M(ps["x"], ps["y"]), 0.25 * KM, "FINO")
    t(msp, "pila (38°)", M(ps["x"] + 0.4, ps["y"] - 1.45), 1.8, "MIDDLE_CENTER")
    tn(msp, "8  ACOPIO DE PRODUCTO SECO", M(29.5, 0.95), 1.9, "MIDDLE_CENTER")

    # ------------------------------------------------ playa de descarga (1), pila, muro y canaleta
    mc = G["muro_contencion"]
    muro(msp, mc["x"] - mc["e"] / 2, mc["y0"], mc["x"] + mc["e"] / 2, mc["y1"] - e, "AR-CONC")
    t(msp, "muro H°A° h 1,8 m", M(mc["x"] + 0.5, 14.6), 1.6, "MIDDLE_CENTER", rotacion=90)
    circulo(msp, M(pg["x"], pg["y"]), pg["r"] * KM)
    circulo(msp, M(pg["x"], pg["y"]), 0.82 * KM)
    t(msp, "pila de descarga", M(pg["x"] + 0.3, pg["y"] - 1.25), 1.6, "MIDDLE_CENTER")
    t(msp, "≈ 8 m³", M(pg["x"] + 0.3, pg["y"] - 1.85), 1.6, "MIDDLE_CENTER")
    tn(msp, "1  PLAYA DE DESCARGA", M(2.0, 17.5), 1.9, "MIDDLE_LEFT")
    t(msp, "piso H°A°", M(0.8, 12.8), 1.6, "MIDDLE_LEFT")
    t(msp, "pend. 1 % a canaleta", M(0.8, 12.1), 1.6, "MIDDLE_LEFT")
    cn = G["canaleta"]
    y0c, y1c = cn["y"] - cn["ancho"] / 2, cn["y"] + cn["ancho"] / 2
    relleno_m(msp, cn["x0"], y0c, cn["x1"], y1c, (255, 255, 255))
    rect_m(msp, cn["x0"], y0c, cn["x1"], y1c, "CONTORNO")
    xg = cn["x0"] + 0.3
    while xg < cn["x1"]:
        linea(msp, M(xg, y0c), M(xg, y1c), "FINO")
        xg += 0.3
    # pala cargadora
    pala(msp)

    # camión volcador entrando marcha atrás por P1
    yc_p1 = (pt["P1"]["a"] + pt["P1"]["b"]) / 2
    camion(msp, -2.0, yc_p1)
    t(msp, "camión volcador\n(entra marcha atrás)", D(213, 362), 1.8, "MIDDLE_RIGHT")
    poli(msp, [D(217, 366), M(-1.5, 15.0)], "COTAS")
    relleno_circulo(msp, M(-1.5, 15.0), 0.55, (0, 0, 0))
    # cota del portón P1
    for yy in (pt["P1"]["a"], pt["P1"]["b"]):
        linea(msp, M(-0.1, yy), (D(205, 0)[0], M(0, yy)[1]), "COTAS")
    cota(msp, (D(210, 0)[0], M(0, pt["P1"]["a"])[1]), (D(210, 0)[0], M(0, pt["P1"]["b"])[1]),
         distancia=0, escala=k, valor="4000 (P1)")
    tn(msp, "P1 4,0 m", D(250, 531), 1.9, "MIDDLE_CENTER")

    # cámara de lixiviados (26) y conexión desde la canaleta
    cl = G["camara_lix"]
    h = cl["a"] / 2
    relleno_m(msp, cl["x"] - h, cl["y"] - h, cl["x"] + h, cl["y"] + h, (255, 255, 255))
    rect_m(msp, cl["x"] - h, cl["y"] - h, cl["x"] + h, cl["y"] + h)
    linea(msp, M(cl["x"] - h, cl["y"] - h), M(cl["x"] + h, cl["y"] + h), "FINO")
    linea(msp, M(cl["x"] - h, cl["y"] + h), M(cl["x"] + h, cl["y"] - h), "FINO")
    linea(msp, M(cl["x"] + h, cl["y"] + 0.3), M(cn["x0"], cn["y"]), color=C_LIX, lw=50)

    # ------------------------------------------------ tolva (2) y cinta con tacos (3)
    cnt = G["cinta"]
    yb0, yb1 = cnt["y"] - cnt["B"] / 2, cnt["y"] + cnt["B"] / 2
    relleno_m(msp, cnt["x_cola"], yb0, cnt["x_cabeza"], yb1, (255, 255, 255))
    rect_m(msp, cnt["x_cola"], yb0, cnt["x_cabeza"], yb1)
    rect_m(msp, cnt["x_cola"] + 0.1, cnt["y"] - cnt["b_util"] / 2, cnt["x_cabeza"] - 0.1,
           cnt["y"] + cnt["b_util"] / 2, "FINO")
    xt = cnt["x_cola"] + 0.3
    while xt < cnt["x_cabeza"] - 0.2:
        linea(msp, M(xt, cnt["y"] - 0.13), M(xt, cnt["y"] + 0.13), color=(140, 140, 140), capa="FINO")
        xt += cnt["paso"]
    tv = G["tolva"]
    relleno_m(msp, tv["x0"], tv["y0"], tv["x1"], tv["y1"], (255, 255, 255))
    rect_m(msp, tv["x0"], tv["y0"], tv["x1"], tv["y1"])
    poli(msp, [M(tv["x0"], tv["y0"]), M(tv["ranura_x"][0] + 0.15, cnt["y"] - 0.2),
               M(tv["ranura_x"][1] - 0.15, cnt["y"] - 0.2), M(tv["x1"], tv["y0"])], "FINO")
    poli(msp, [M(tv["x0"], tv["y1"]), M(tv["ranura_x"][0] + 0.15, cnt["y"] + 0.2),
               M(tv["ranura_x"][1] - 0.15, cnt["y"] + 0.2), M(tv["x1"], tv["y1"])], "FINO")
    rect_m(msp, tv["x0"] - 0.35, tv["y1"] - 0.3, tv["x0"], tv["y1"], "FINO")
    t(msp, "cinta 30° (+0,65 a +4,35) - plano 12", M(6.0, 8.2), 1.5, "MIDDLE_LEFT")

    # ------------------------------------------------ secador de cinta (4), sinfín (6), elevador (7)
    sc = G["secador"]
    sx0, sy0, sx1, sy1 = sc["x0"], sc["y0"], sc["x0"] + sc["L"], sc["y0"] + sc["A"]
    relleno_m(msp, sx0, sy0, sx1, sy1, (255, 255, 255))
    rect_m(msp, sx0, sy0, sx1, sy1, lw=100)
    linea(msp, M(sx0 + 0.15, sc["yc"] - 0.3), M(sx1 - 0.15, sc["yc"] - 0.3), "FINO")
    for cx in sc["columnas_x"]:
        for yy in (sy0, sy1):
            relleno_m(msp, sx0 + cx - 0.06, yy - 0.06, sx0 + cx + 0.06, yy + 0.06, (40, 40, 40))
    rect_m(msp, sx0 + 0.15, 9.75, sx0 + 0.6, 10.25, "CONTORNO")            # boca de alimentación
    tn(msp, "4  SECADOR DE CINTA - 3 PISOS", M(19.3, 9.6), 2.2, "MIDDLE_CENTER")
    t(msp, "13,0 x 2,6 m - H 3,4 m", M(19.3, 8.55), 1.6, "MIDDLE_CENTER")
    for xm in (11.6, 24.0):                                             # motorreductores (lado Sur)
        rect_m(msp, xm, 7.75, xm + 0.45, 8.0, "FINO")
    sf = G["sinfin_desc"]
    rect_m(msp, sf["x0"], sf["y"] - 0.12, sf["x1"], sf["y"] + 0.12, "CONTORNO")
    el = G["elevador"]
    rect_m(msp, el["x"] - el["ax"] / 2, el["y"] - el["ay"] / 2, el["x"] + el["ax"] / 2, el["y"] + el["ay"] / 2)
    linea(msp, M(el["x"] - el["ax"] / 2, el["y"] - el["ay"] / 2), M(el["x"] + el["ax"] / 2, el["y"] + el["ay"] / 2), "FINO")
    pc = G["pico"]
    for d in (-0.12, 0.12):
        linea(msp, M(pc["x0"] + d, pc["y0"] + d), M(pc["x1"] + d, pc["y1"] + d), color=C_GUANO, lw=50)
    ts = G["ts1"]
    rect_m(msp, ts["x"] - 0.5, ts["y"] - 0.12, ts["x"] + 0.5, ts["y"] + 0.12)
    t(msp, "TS-1", M(ts["x"] + 0.7, ts["y"]), 1.6, "MIDDLE_LEFT")
    t(msp, "motorreductores (lado Sur)", M(19.3, 7.25), 1.8, "MIDDLE_CENTER")

    # senda peatonal demarcada
    poli(msp, [M(8.4, 7.6), M(9.8, 7.6), M(9.8, 6.8), M(25.5, 6.8)], "CONTORNO", lw=50)
    linea(msp, M(19.5, 6.8), M(19.5, e), "CONTORNO", lw=50)

    # ------------------------------------------------ sector de alimentación
    tn(msp, "SECTOR DE ALIMENTACIÓN", M(0.7, 6.0), 2.0, "MIDDLE_LEFT")
    t(msp, "acceso peatonal a la cola", M(0.7, 5.2), 1.8, "MIDDLE_LEFT")
    t(msp, "de la cinta (mantenimiento)", M(0.7, 4.6), 1.8, "MIDDLE_LEFT")

    # ------------------------------------------------ anexo del generador (muro RF-120 hacia afuera)
    ax = G["anexo"]
    ea = 0.2
    acceso = (24.0, 25.2)
    muro_con_vanos(msp, "y", ax["x0"], ax["y0"], ax["y1"] + ea, ea, [], -1)
    muro_con_vanos(msp, "y", ax["x1"], ax["y0"], ax["y1"] + ea, ea, [], +1)
    muro_con_vanos(msp, "x", ax["y1"], ax["x0"] - ea, ax["x1"] + ea, ea, [acceso], +1)
    puerta(msp, (acceso[0], ax["y1"] + ea), 0.6, 0, 90)
    puerta(msp, (acceso[1], ax["y1"] + ea), 0.6, 180, 90)
    t(msp, "acceso", M(24.6, 23.85), 1.6, "MIDDLE_CENTER")
    relleno_m(msp, ax["x0"] - ea - 0.05, 18.8, ax["x0"] + 0.05, 20.4, (30, 30, 30))   # toma de aire
    t(msp, "toma de aire", M(ax["x0"] - 0.45, 19.5), 1.6, "MIDDLE_RIGHT")
    # intercambiador (10)
    ic = ax["intercambiador"]
    relleno_m(msp, ic["x0"], ic["y0"], ic["x1"], ic["y1"], (255, 255, 255))
    rect_m(msp, ic["x0"], ic["y0"], ic["x1"], ic["y1"])
    for xx in ic["xts"]:
        linea(msp, M(xx, ic["y0"]), M(xx, ic["y1"]))
    n = 9
    for i in range(1, n):
        yy = ic["y0"] + i * (ic["y1"] - ic["y0"]) / n
        linea(msp, M(ic["xts"][0], yy), M(ic["xts"][1], yy), "FINO")
    tn(msp, "10  intercambiador", M(23.4, 22.95), 1.8, "MIDDLE_CENTER")
    # ducto de salida de aire caliente (sobre el intercambiador)
    ds = ax["ducto_salida"]
    rect_m(msp, ds["x0"], 18.0, ds["x1"], 21.3, "CONTORNO")
    # ventiladores de impulsión (11)
    for v in ax["ventiladores"]:
        rect_m(msp, v["x"] - 0.25, v["y"] + 0.5, v["x"] + 0.25, ic["y0"], "CONTORNO")
        relleno_circulo(msp, M(v["x"], v["y"]), 0.58 * KM, (255, 255, 255))
        circulo(msp, M(v["x"], v["y"]), 0.58 * KM)
    tn(msp, "11", M(23.6, 19.0), 2.0, "MIDDLE_CENTER")
    # hogar (9)
    hg = ax["hogar"]
    o = [M(hg["x0"], hg["y0"]), M(hg["x1"], hg["y0"]), M(hg["x1"], hg["y1"]), M(hg["x0"], hg["y1"])]
    rayado(msp, o, escala=0.12)
    relleno_m(msp, hg["ix0"], hg["iy0"], hg["ix1"], hg["iy1"], (255, 255, 255))
    poli(msp, o, "CONTORNO", cerrada=True)
    rect_m(msp, hg["ix0"], hg["iy0"], hg["ix1"], hg["iy1"])
    tn(msp, "9", M(26.8, 21.75), 2.4, "MIDDLE_CENTER")
    t(msp, "hogar", M(26.8, 20.85), 1.8, "MIDDLE_CENTER")
    # ventilador de aire de combustión, ciclón de humos, chimenea (15), cenizas (16)
    vc, ch, cz, cm_ = ax["vent_comb"], ax["ciclon_humos"], ax["cenizas"], ax["chimenea"]
    linea(msp, M(vc["x"], vc["y"] - 0.4), M(vc["x"], hg["y1"]), color=C_COMB, lw=50)
    circulo(msp, M(vc["x"], vc["y"]), 0.4 * KM)
    rect_m(msp, cz["x"] - 0.5, cz["y"] - 0.5, cz["x"] + 0.5, cz["y"] + 0.5)
    tn(msp, "16", M(cz["x"], cz["y"]), 1.8, "MIDDLE_CENTER")
    linea(msp, M(cz["x"], cz["y"] - 0.5), M(cz["x"], hg["y1"]), "FINO")
    linea(msp, M(ch["x"], ch["y"] - 0.4), M(ic["xts"][0], ic["y1"]), color=C_HUMOS, lw=50)
    circulo(msp, M(ch["x"], ch["y"]), ch["D"] / 2 * KM)
    linea(msp, M(ch["x"], ch["y"] + 0.4), M(cm_["x"], cm_["y"]), color=C_HUMOS, lw=50)
    relleno_circulo(msp, M(cm_["x"], cm_["y"]), cm_["D"] / 2 * KM, (255, 255, 255))
    circulo(msp, M(cm_["x"], cm_["y"]), cm_["D"] / 2 * KM, lw=70)
    circulo(msp, M(cm_["x"], cm_["y"]), cm_["D"] / 4 * KM)
    tn(msp, "ANEXO GENERADOR", M(26.85, 19.6), 1.5, "MIDDLE_CENTER")
    t(msp, "8,0 x 6,5 m", M(26.95, 19.0), 1.5, "MIDDLE_CENTER")
    t(msp, "muro RF-120", M(26.95, 18.45), 1.5, "MIDDLE_CENTER")
    # silo de cáscara (13) y sinfín (14)
    si = G["silo"]
    circulo(msp, M(si["x"], si["y"]), si["D"] / 2 * KM)
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        relleno_m(msp, si["x"] + dx * 1.15 - 0.12, si["y"] + dy * 1.15 - 0.12,
                  si["x"] + dx * 1.15 + 0.12, si["y"] + dy * 1.15 + 0.12, (40, 40, 40))
    sk = G["sinfin_cascara"]
    rect_m(msp, sk["x1"], sk["y"] - 0.1, sk["x0"], sk["y"] + 0.1, "CONTORNO")
    linea(msp, M(sk["x1"] + 0.6, sk["y"]), M(sk["x1"] + 1.3, sk["y"]), color=C_GUANO, lw=70)
    rect_m(msp, sk["x1"] + 0.05, sk["y"] - 0.2, sk["x1"] + 0.5, sk["y"] + 0.2, "FINO")
    circulo(msp, M(sk["x0"], sk["y"]), 0.2 * KM)
    tn(msp, "13  SILO", M(si["x"] + 0.2, si["y"] + 0.75), 2.0, "MIDDLE_CENTER")
    t(msp, "70 m³", M(si["x"], si["y"] - 0.75), 1.8, "MIDDLE_CENTER")

    # ------------------------------------------------ ductos de aire caliente (12) y agotado (17)
    dc = G["ducto_caliente"]
    rect_m(msp, dc["x0"], 10.6, dc["x1"], A - e, color=C_CAL, lw=50)
    rect_m(msp, dc["x0"], 10.6, dc["x1"], 11.5, color=C_CAL, lw=50)
    linea(msp, M(dc["x0"], 10.6), M(dc["x1"], 11.5), color=C_CAL)
    linea(msp, M(dc["x0"], 11.5), M(dc["x1"], 10.6), color=C_CAL)
    rect_m(msp, dc["x0"], A - e, dc["x1"], A, color=C_CAL, lw=50)
    flecha(msp, M(22.5, 15.4), M(22.5, 13.9), color=C_CAL, tam=2.0)
    tn(msp, "12", M(23.5, 14.6), 2.0, "MIDDLE_LEFT")
    t(msp, "ducto 1200x600", M(23.5, 13.75), 1.6, "MIDDLE_LEFT")
    t(msp, "a +3,50", M(23.5, 13.1), 1.6, "MIDDLE_LEFT")
    t(msp, "compuerta cortafuego", M(21.5, 17.3), 1.6, "MIDDLE_RIGHT")
    da = G["ducto_agotado"]
    r_a = da["D"] / 2
    xa = da["recorrido"][0][0]
    rect_m(msp, xa - r_a, 9.3, xa + r_a, G["ciclon"]["y"] - 0.9, color=C_AGOT, lw=50)
    relleno_circulo(msp, M(xa, 9.3), r_a * KM, (255, 255, 255))
    circulo(msp, M(xa, 9.3), r_a * KM)
    flecha(msp, M(xa, 13.4), M(xa, 15.0), color=C_AGOT, tam=2.0)
    tn(msp, "17", M(xa + 0.8, 14.9), 2.0, "MIDDLE_LEFT")
    t(msp, "Ø800 a +6,5", M(xa + 0.8, 13.75), 1.6, "MIDDLE_LEFT")

    # ------------------------------------------------ tratamiento de aire: ciclón (18), lavador (19), extractor (20), tanque (21)
    cc, sb, ex, tq, bb = G["ciclon"], G["scrubber"], G["extractor"], G["tanque_sol"], G["bomba"]
    dl = G["ducto_lavador"]["recorrido"]
    # ducto ciclón -> lavador (verde)
    poli(msp, [M(cc["x"] - r_a, cc["y"]), M(cc["x"] - r_a, 22.1 + r_a), M(15.8 + r_a, 22.1 + r_a),
               M(15.8 + r_a, 22.1 - r_a), M(cc["x"] + r_a, 22.1 - r_a)], color=C_AGOT, lw=50)
    circulo(msp, M(dl[2][0], dl[2][1]), r_a / 2 * KM, color=C_AGOT)
    linea(msp, M(15.8 + 0.2, 22.1 - 0.25), M(dl[4][0], dl[4][1]), color=C_AGOT, lw=50)
    linea(msp, M(sb["x"], sb["y"]), M(ex["x"], ex["y"]), color=C_AGOT, lw=50)
    linea(msp, M(ex["x"] + 0.6, ex["y"]), M(ex["chim_x"] - ex["chim_D"] / 2, ex["chim_y"]), color=C_AGOT, lw=50)
    # lixiviados / solución
    linea(msp, M(bb["x"], bb["y"] - 0.25), M(sb["x"] - 0.2, sb["y"] + 0.4), color=C_LIX, lw=50)
    linea(msp, M(bb["x"] - 0.4, bb["y"]), M(tq["x"] + 0.9, tq["y"] + 0.2), color=C_LIX, lw=50)
    for c, D_ in ((cc, cc["D"]), (sb, sb["D"])):
        relleno_circulo(msp, M(c["x"], c["y"]), D_ / 2 * KM, (255, 255, 255))
        circulo(msp, M(c["x"], c["y"]), D_ / 2 * KM)
    circulo(msp, M(cc["x"], cc["y"]), 0.4 * KM)
    circulo(msp, M(sb["x"], sb["y"]), 0.4 * KM)
    circulo(msp, M(tq["x"], tq["y"]), tq["D"] / 2 * KM)
    rect_m(msp, ex["x"] - 0.6, ex["y"] - 0.5, ex["x"] + 0.6, ex["y"] + 0.5)
    circulo(msp, M(ex["chim_x"], ex["chim_y"]), ex["chim_D"] / 2 * KM)
    rect_m(msp, bb["x"] - 0.4, bb["y"] - 0.3, bb["x"] + 0.4, bb["y"] + 0.3)

    # ------------------------------------------------ TGF (22) y alimentación desde el pilar
    tb = G["tablero"]
    rect_m(msp, tb["x"] - tb["a"] / 2, tb["y"] - tb["p"] / 2, tb["x"] + tb["a"] / 2, tb["y"] + tb["p"] / 2)
    tn(msp, "TGF", M(tb["x"] - 0.25, 1.0), 1.6, "MIDDLE_CENTER")
    linea(msp, M(tb["x"], tb["y"] - tb["p"] / 2), M(tb["x"], -1.6), "FINO")
    t(msp, "alimentación desde\nel pilar (40 m)",M(tb["x"] - 0.2, -0.95), 1.5, "MIDDLE_RIGHT")

    # ------------------------------------------------ flujos de guano y producto
    flecha(msp, M(4.8, 12.5), M(3.4, 10.5), color=C_GUANO, tam=2.0, lw=35)          # pala -> tolva
    flecha_poli(msp, [M(24.75, 7.6), M(26.3, 7.6), M(27.25, 6.95)], color=C_GUANO, tam=2.0, lw=35)
    flecha(msp, M(31.25, 0.65), M(31.25, -0.9), color=C_GUANO, tam=2.0, lw=35)      # despacho por P2

    # ------------------------------------------------ cortes A-A
    yA = 10.65
    for xs in (-4.1, 34.5):
        p = M(xs, yA)
        linea(msp, (p[0] - 2.5, p[1] - 6), (p[0] + 2.5, p[1] - 6), "CONTORNO", lw=70)
        flecha(msp, (p[0], p[1] - 6), (p[0], p[1] - 1.5), "CONTORNO", tam=2.2)
        tn(msp, "A", (p[0], p[1] + 0.5), 4.0, "BOTTOM_CENTER")

    # ------------------------------------------------ puestos de trabajo
    for op in G["operarios"]:
        if op["id"] == "OP7":
            continue
        puesto(msp, op["id"][2:], M(op["x"], op["y"]))

    # ------------------------------------------------ cotas
    yc = D(0, 975)[1]
    cota(msp, M(0, 0), M(L, 0), distancia=yc - OY, escala=k)
    cota(msp, M(L, 0), M(L, A), distancia=-4.0, escala=k)
    cota(msp, M(sx0 - 0.5, sy1), M(sx0, sy1), distancia=9.4, escala=k)
    cota(msp, M(sx0, sy1), M(sx1, sy1), distancia=9.4, escala=k)
    cota(msp, M(31.45, 9), M(31.45, A), distancia=0.0, escala=k, valor="9000 (anexo - acopio)")
    cota(msp, M(ax["x0"] - ea, ax["y1"] + ea), M(ax["x1"] + ea, ax["y1"] + ea),
         distancia=D(0, 95)[1] - M(0, ax["y1"] + ea)[1], escala=k)

    # ------------------------------------------------ globos
    R = 3.4
    for et, c, p in (
            ("1", D(570, 358), M(pg["x"] + 1.4, pg["y"] + 1.8)),
            ("2", D(305, 656), M(tv["x0"] + 0.3, tv["y0"] + 0.4)),
            ("3", M(4.6, 7.4), M(5.0, cnt["y"] - 0.2)),
            ("5", D(683, 680), M(sx0 + sc["esparcidor_x"], cnt["y"])),
            ("6", D(1057, 680), M(sf["x1"] - 0.2, sf["y"])),
            ("7", D(1141, 590), M(el["x"] + 0.2, el["y"] + 0.45)),
            ("14", D(1232, 163), M(sk["x0"] - 1.5, sk["y"])),
            ("15", D(929, 123), M(cm_["x"] - 0.3, cm_["y"])),
            ("18", D(692, 243), M(cc["x"] - cc["D"] / 2, cc["y"])),
            ("19", D(851, 318), M(sb["x"] + 0.6, sb["y"] - 0.9)),
            ("20", D(920, 161), M(ex["chim_x"] + 0.4, ex["chim_y"])),
            ("21", D(695, 155), M(tq["x"] - 0.9, tq["y"])),
            ("22", M(23.0, 1.9), M(tb["x"] - 0.5, tb["y"])),
            ("26", D(195, 596), M(cl["x"] - 0.75, cl["y"])),
            ("29", M(12.7, 6.2), M(ts["x"] - 0.4, ts["y"]))):
        globo(msp, et, c, p, radio=R, relleno_rgb=(255, 255, 255))

    # ------------------------------------------------ referencias, flujos y puestos (columna derecha)
    xr = 299.5
    subtitulo(msp, "REFERENCIAS", xr, 273.6, 3.2)
    refs = ["Playa de recepción de guano", "Tolva de recepción 3,1 m³", "Cinta de alimentación con tacos",
            "Secador de cinta de 3 pisos", "Esparcidor de paletas", "Sinfín de descarga", "Elevador de cangilones",
            "Acopio de producto seco", "Hogar de parrilla escalonada", "Intercambiador humos-aire",
            "Ventiladores de impulsión", "Ducto de aire caliente", "Silo de cáscara 70 m³",
            "Sinfín de cáscara + válvula rotativa", "Chimenea de humos", "Tolva de cenizas 1 m³",
            "Ducto de aire agotado", "Ciclón separador", "Lavador de gases (scrubber)",
            "Extractor y chimenea de aire tratado", "Tanque de solución y bomba", "Sala de control (TGF)",
            "Taller de mantenimiento", "Vestuario, baños y oficina", "Depósito de repuestos",
            "Cámara de lixiviados", "Tanque de agua contra incendio", "Reserva 2ª etapa",
            "Tablero secundario TS-1", "Báscula para camiones 40 t", "Garita de control y balanza",
            "Circulación y playones de camiones", "Cerco perimetral y portón de acceso",
            "Estacionamiento del personal"]
    y = 270.2
    for i, r in enumerate(refs, start=1):
        tn(msp, str(i), (xr + 4.2, y), 2.2, "MIDDLE_RIGHT")
        t(msp, r, (xr + 6.0, y), 2.1, "MIDDLE_LEFT")
        y -= 3.05
    subtitulo(msp, "FLUJOS", xr, 162.9, 3.2)
    flujos = [(C_GUANO, "guano / producto / cáscara"), (C_CAL, "aire caliente 135 °C"),
              (C_AGOT, "aire agotado a tratamiento"), (C_HUMOS, "humos de combustión"),
              (C_LIX, "lixiviados / solución"), (C_COMB, "aire de combustión")]
    y = 159.6
    for rgb, txt in flujos:
        linea(msp, (xr - 0.5, y), (xr + 9, y), color=rgb, lw=70)
        t(msp, txt, (xr + 10.8, y), 2.1, "MIDDLE_LEFT")
        y -= 3.25
    subtitulo(msp, "PUESTOS DE TRABAJO (1 turno)", xr, 136.3, 3.2)
    puestos = ["Maquinista de pala cargadora", "Recepción y señalero", "Operador de secado",
               "Operador de sala de control", "Foguista (generador y silo)", "Despacho y mantenimiento",
               "Portería y balanza (garita, pl. 11)"]
    y = 132.8
    for i, p in enumerate(puestos, start=1):
        puesto_ley(msp, i, (xr + 2.0, y))
        t(msp, p, (xr + 4.8, y), 2.1, "MIDDLE_LEFT")
        y -= 3.2
    linea(msp, (xr - 0.5, y - 0.2), (xr + 9, y - 0.2), lw=70)
    t(msp, "senda peatonal demarcada", (xr + 10.8, y - 0.2), 2.1, "MIDDLE_LEFT")

    escala_grafica(msp, 301.2, 87.0, ESC, 10, 2)

    # ------------------------------------------------ relaciones verificadas (SLP)
    subtitulo(msp, "RELACIONES VERIFICADAS (SLP)", 27.9, 77.2, 3.2)
    rel = ["A  recepción - tolva - secador contiguos; secador - generador: ducto de 12 m; silo junto al hogar.",
           "X  generador - acopio de producto seco: 9,0 m y muro cortafuego RF-120 (riesgo de incendio).",
           "X  recepción - vestuario/oficina: separados por depósito y taller (olores, riesgo biológico).",
           "E  sala de control - secador: ventana con vista directa; TGF a 7 m del secador.",
           "Superficie cubierta: nave 594 m² + anexo 52 m². Altura libre 7,0 m; corte A-A y vista Norte: plano 08.",
           "Camiones: entran marcha atrás por P1 y vuelcan en la playa; predio, báscula y circulación: plano 11. "
           "Cinta: plano 12.",
           "Tanque de incendio (27) y pilar de acometida sobre la línea municipal: plano 11."]
    y = 73.0
    for r in rel:
        t(msp, r, (27.9, y), 2.1, "MIDDLE_LEFT")
        y -= 3.4

    # el título del rótulo entra en su casillero (la biblioteca lo deja en 4,2 mm)
    for e in msp.query("TEXT"):
        if e.dxf.text == "IMPLANTACIÓN Y DISTRIBUCIÓN EN PLANTA" and e.dxf.layer == "ROTULO":
            e.dxf.height = 3.5
    exportar_lamina(doc, 1)


if __name__ == "__main__":
    main()
