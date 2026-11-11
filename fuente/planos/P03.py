"""P03 - Tambor motriz del secador: eje, apoyos UCF 212 y transmisión por cadena.

Redibujo vectorial de la lámina aprobada (Rev. C, PNG). Vistas:
  A  corte por el eje del tambor motriz, 1:10
  B  transmisión del lado Sur, 1:20
  C  diagramas de cargas, flector y torsor del eje (sin escala)
  D  sección por la chaveta del cubo de la corona Z75, 1:2
  E  tensor del tambor de reenvío, 1:5
más la tabla de datos y verificaciones del tambor motriz.
Radio del tambor motriz (158 mm) y de reenvío (125 mm) tomados de fuente/datos/layout_planta.json.
"""
import json
import math
import os

from lamina_secadora import (COL, FECHA, circulo, cota, exportar_lamina, factor, flecha, globo,
                             lamina, linea, poli, rayado, rect, relleno, relleno_rect, subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
R_MOTRIZ = G["secador"]["r_motriz"] * 1000      # 158 mm (Ø316 con el engomado)
_RES = json.load(open(os.path.join(AQUI, "..", "calculos", "resultados.json"), encoding="utf-8"))["fatiga"]
FAT, REE = _RES["eje_motriz"], _RES["eje_reenvio"]


def coma(x, d=1):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

GRIS_PANEL = (150, 150, 150)
GRIS_GOMA = (60, 60, 60)
AZUL_MF = (220, 228, 240)
ROSA_MT = (240, 224, 212)


# ---------------------------------------------------------------- helpers propios

def cota_txt(msp, p1, p2, base, texto_en, escala, valor="<>", vertical=False):
    """Cota lineal (horizontal o vertical) con el texto corrido a texto_en (para no cruzar ejes)."""
    dim = msp.add_linear_dim(base=base, p1=p1, p2=p2, location=texto_en, text=valor,
                             angle=90 if vertical else 0, dimstyle="IRAM",
                             override={"dimlfac": 1.0 / escala, "dimtmove": 2},
                             dxfattribs={"layer": "COTAS"})
    dim.render()
    return dim


def rotura_v(msp, x, y, alto=2.6):
    """Símbolo de rotura (zigzag) sobre una línea vertical, centrado en (x, y)."""
    poli(msp, [(x, y + alto), (x, y + 0.5), (x + 0.9, y + 0.9), (x - 0.9, y - 0.9), (x, y - 0.5),
               (x, y - alto)], "CONTORNO")


def eje_h(msp, x0, x1, y):
    linea(msp, (x0, y), (x1, y), "EJES")


def eje_v(msp, x, y0, y1):
    linea(msp, (x, y0), (x, y1), "EJES")


def cajon_rayado(msp, x0, y0, x1, y1, esc=0.25):
    rayado(msp, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], escala=esc)
    rect(msp, x0, y0, x1, y1)


# ---------------------------------------------------------------- A - corte por el eje (1:10)

def vista_a(msp):
    k = factor("1:10")
    XC, YA = 188.1, 232.0                     # centro del tambor, eje del árbol
    X = lambda u: XC + u * k                 # u: mm reales a lo largo del eje (Norte < 0 < Sur)
    Y = lambda v: YA + v * k                 # v: mm reales radiales
    titulo_vista(msp, "A - CORTE POR EL EJE DEL TAMBOR MOTRIZ (mirando al Este)  -  ESC. 1:10", 28, 279.5, 3.3)

    # paneles de la cámara (80 mm, cortados) con sellos de laberinto
    for u0, u1 in ((-1300, -1220), (1220, 1300)):
        relleno_rect(msp, X(u0), Y(-330), X(u1), Y(330), GRIS_PANEL)
        linea(msp, (X(u0), Y(-330)), (X(u0), Y(330)))
        linea(msp, (X(u1), Y(-330)), (X(u1), Y(330)))
        for v in (-330, 330):
            linea(msp, (X(u0 - 12), Y(v)), (X(u1 + 12), Y(v)), "FINO")
            rotura_v(msp, X((u0 + u1) / 2), Y(v))
        um = (u0 + u1) / 2
        relleno_rect(msp, X(um - 47), Y(-60), X(um + 47), Y(60), (255, 255, 255))
        rect(msp, X(um - 47), Y(-60), X(um + 47), Y(60))
        t(msp, "panel 80 mm", (X(um), Y(330) + 3.0), 2.0, "BOTTOM_CENTER")

    # árbol Ø60 (Ø50 en el extremo de la corona)
    rect(msp, X(-1440), Y(-30), X(1455), Y(30))
    rect(msp, X(1455), Y(-25), X(1560), Y(25))

    # tambor Ø300 + engomado 8 mm (Ø316), discos de 12 mm y bujes de fijación cónicos
    for s in (1, -1):
        relleno(msp, [(X(-1050), Y(s * 150)), (X(1050), Y(s * 150)), (X(1050), Y(s * R_MOTRIZ)),
                      (X(-1050), Y(s * R_MOTRIZ))], GRIS_GOMA)
        linea(msp, (X(-1050), Y(s * R_MOTRIZ)), (X(1050), Y(s * R_MOTRIZ)))
        linea(msp, (X(-1050), Y(s * 150)), (X(1050), Y(s * 150)), "FINO")
    for ud in (-1050, 1038):
        for s in (1, -1):
            v0, v1 = sorted((s * 58, s * 150))
            cajon_rayado(msp, X(ud), Y(v0), X(ud + 12), Y(v1), 0.2)
        linea(msp, (X(ud), Y(-R_MOTRIZ)), (X(ud), Y(R_MOTRIZ)))
    linea(msp, (X(1050), Y(-R_MOTRIZ)), (X(1050), Y(R_MOTRIZ)))
    for uh in (-1044, 1044):
        for s in (1, -1):
            v0, v1 = sorted((s * 30, s * 58))
            cajon_rayado(msp, X(uh - 40), Y(v0), X(uh + 40), Y(v1), 0.2)

    # apoyos UCF 212 sobre ménsulas PL 12 (fuera de la cámara)
    for s in (-1, 1):
        ub = 1370 * s
        uf0, uf1 = sorted((ub - 21 * s, ub + 18 * s))          # brida
        um0, um1 = sorted((ub + 18 * s, ub + 30 * s))          # ménsula PL 12
        relleno_rect(msp, X(um0), Y(-260), X(um1), Y(110), (255, 255, 255))
        rect(msp, X(um0), Y(-260), X(um1), Y(110))
        rect(msp, X(uf0), Y(-88), X(uf1), Y(88))
        for sv in (1, -1):
            v0, v1 = sorted((sv * 30, sv * 46))
            cajon_rayado(msp, X(ub - 34), Y(v0), X(ub + 34), Y(v1), 0.2)
        rect(msp, X(ub - 34), Y(-46), X(ub + 34), Y(46))
        for v in (71, -71):                                     # bulones de la brida
            linea(msp, (X(ub - 34), Y(v)), (X(ub + 30), Y(v)), "EJES")
        tn(msp, "UCF 212", (X(ub), Y(140)), 2.2, "BOTTOM_CENTER")

    # corona Z75 (cubo Ø100) y protector de la cadena
    cajon_rayado(msp, X(1469), Y(25), X(1541), Y(50), 0.2)
    cajon_rayado(msp, X(1469), Y(-50), X(1541), Y(-25), 0.2)
    cajon_rayado(msp, X(1499), Y(50), X(1511), Y(235), 0.2)
    cajon_rayado(msp, X(1499), Y(-235), X(1511), Y(-50), 0.2)
    linea(msp, (X(1499), Y(-235)), (X(1499), Y(-546)), "FINO")       # ramales de la cadena
    linea(msp, (X(1511), Y(-235)), (X(1511), Y(-546)), "FINO")
    linea(msp, (X(1499), Y(-546)), (X(1511), Y(-546)), "FINO")
    rect(msp, X(1475), Y(-569), X(1535), Y(254))
    t(msp, "protector", (X(1575), Y(-150)), 2.0, "MIDDLE_LEFT")
    # motorreductor 1:300 sobre base con colisos
    rect(msp, X(1535), Y(-520), X(1565), Y(-480))                   # salida del reductor
    rect(msp, X(1565), Y(-610), X(1780), Y(-390))
    rect(msp, X(1565), Y(-627), X(1780), Y(-610))
    for ux in (1575, 1750):
        rect(msp, X(ux), Y(-627), X(ux + 20), Y(-612), "FINO")
    circulo(msp, (X(1672), Y(-548)), 5.8)
    t(msp, "REDUCTOR\n1:300", (X(1672), Y(-405)), 2.0, "TOP_CENTER")
    t(msp, "M 0,75 kW", (X(1672), Y(-548)), 1.6, "MIDDLE_CENTER")
    eje_h(msp, X(1470), X(1790), Y(-500))
    t(msp, "base con colisos (tensado)", (X(1672), Y(-645)), 1.9, "TOP_CENTER")

    eje_h(msp, X(-1490), X(1600), YA)

    # textos y referencias
    tn(msp, "NORTE", (40.1, 262.0), 2.4, "MIDDLE_CENTER")
    tn(msp, "SUR (accionamiento)", (348.1, 271.5), 2.4, "MIDDLE_CENTER")
    tn(msp, "INTERIOR DE LA CÁMARA (65-135 °C, NH3)", (XC, 263.2), 2.2, "MIDDLE_CENTER")
    t(msp, "ménsula PL 12", (X(-1400), 203.7), 1.8, "MIDDLE_CENTER")
    t(msp, "ménsula\nPL 12", (X(1385), 205.6), 1.8, "TOP_CENTER")
    t(msp, "buje de fijación cónico", (90.5, 212.6), 2.0, "MIDDLE_LEFT")
    linea(msp, (90.0, 212.6), (X(-1044), Y(-58)), "COTAS")
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc((X(-1044), Y(-58)), 0.55, 0, 360)
    globo(msp, "4.4", (37.1, 250.7), (X(-1380), Y(88)))
    globo(msp, "4.2", (263.1, 253.7), (X(700), Y(R_MOTRIZ)))
    globo(msp, "C75", (326.6, 259.5), (X(1505), Y(235)))
    globo(msp, "4.5", (369.5, 199.0), (X(1700), Y(-390)))

    # cotas
    cota(msp, (X(-1440), Y(-30)), (X(-1440), Y(30)), 8.0, k, "Ø<> k6")
    cota(msp, (X(1560), Y(-25)), (X(1560), Y(25)), -8.0, k, "Ø<> k6")
    cota(msp, (122.0, Y(-150)), (122.0, Y(150)), 0.0, k, "Ø<>")
    cota(msp, (142.0, Y(-R_MOTRIZ)), (142.0, Y(R_MOTRIZ)), 0.0, k, "Ø<>")
    cota(msp, (X(1515), Y(-227.5)), (X(1515), Y(227.5)), -(363.3 - X(1515)), k, "Ø<> (Z75)")
    cota(msp, (X(1785), Y(-500)), (X(1785), Y(0)), -(378.1 - X(1785)), k)
    cota(msp, (X(-1050), Y(R_MOTRIZ) + 1.0), (X(1050), Y(R_MOTRIZ) + 1.0), 8.0, k, "<> (tambor)")
    cota(msp, (X(-1000), Y(-R_MOTRIZ) - 1.0), (X(1000), Y(-R_MOTRIZ) - 1.0), -8.0, k, "<> (banda)")
    cota(msp, (X(-1220), Y(-330)), (X(1220), Y(-330)), -8.0, k, "<> (interior)")
    cota(msp, (X(-1370), 200.0), (X(1370), 200.0), -15.0, k, "<> (apoyos)")
    cota(msp, (X(-1440), Y(-30)), (X(1560), Y(-30)), -(Y(-30) - 179.0), k, "<> (eje)")


# ---------------------------------------------------------------- B - transmisión (1:20)

def tangentes_ext(c1, r1, c2, r2):
    """Las dos tangentes exteriores entre dos círculos (ramales de la cadena)."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    base = math.atan2(dy, dx)
    a = math.acos((r1 - r2) / d)
    res = []
    for s in (1, -1):
        ang = base + s * a
        res.append(((c1[0] + r1 * math.cos(ang), c1[1] + r1 * math.sin(ang)),
                    (c2[0] + r2 * math.cos(ang), c2[1] + r2 * math.sin(ang))))
    return res


def vista_b(msp):
    k = factor("1:20")
    titulo_vista(msp, "B - TRANSMISIÓN (lado Sur)  -  ESC. 1:20", 25.0, 170.5, 3.2)
    cx, cy = 58.0, 134.0
    cy2 = cy - 500 * k
    # protector (doble chapa)
    gp = [(-8.4, 11.7), (8.5, 11.7), (12.8, 2.9), (12.8, -2.8), (3.9, -25.9), (-3.9, -25.9),
          (-12.6, -2.8), (-12.6, 2.9)]
    poli(msp, [(cx + a, cy + b) for a, b in gp], cerrada=True)
    poli(msp, [(cx + a * 0.93, cy + 0.6 + (b - 0.6) * 0.95) for a, b in gp], "FINO", cerrada=True)
    # reductor y motor
    relleno_rect(msp, cx - 7.4, cy - 30.5, cx + 5.6, cy - 19.3, (255, 255, 255))
    rect(msp, cx - 7.4, cy - 30.5, cx + 5.6, cy - 19.3)
    rect(msp, cx + 5.6, cy - 27.9, cx + 16.6, cy - 21.8)
    tn(msp, "M", (cx + 11.1, cy - 24.85), 2.2, "MIDDLE_CENTER")
    # corona Z75, tambor detrás, brida UCF 212 y piñón Z15
    circulo(msp, (cx, cy), 7.9, "CONTORNO")
    circulo(msp, (cx, cy), 11.75, "CONTORNO", lw=70)
    rect(msp, cx - 4.4, cy - 4.4, cx + 4.4, cy + 4.4)
    circulo(msp, (cx, cy), 2.29)
    circulo(msp, (cx, cy), 1.25)
    circulo(msp, (cx, cy2), 2.29, "CONTORNO", lw=70)
    circulo(msp, (cx, cy2), 1.1)
    for a, b in tangentes_ext((cx, cy), 455 / 2 * k, (cx, cy2), 91.6 / 2 * k):
        linea(msp, a, b)
    eje_h(msp, cx - 13.6, cx + 13.6, cy)
    eje_v(msp, cx, cy + 13.6, cy - 28.6)
    eje_h(msp, cx - 4.0, cx + 4.0, cy2)
    cota(msp, (cx + 17.5, cy2), (cx + 17.5, cy), -4.5, k)
    t(msp, "cadena ASA 60 simple, paso 19,05\nZ1 = 15 (Ø91,6) - Z2 = 75 (Ø454,9)\nreductor doble sinfín-corona 1:300",
      (27.1, 95.8), 2.0, "TOP_LEFT")


# ---------------------------------------------------------------- C - diagramas (S/E)

def vista_c(msp):
    titulo_vista(msp, "C - DIAGRAMAS DEL EJE  -  ESC. S/E", 120.0, 170.5, 3.2)
    t(msp, "P = (T1 + T2)/2 = 3.489 N (plano H) + 450 N (peso)", (118.0, 160.9), 2.1)
    t(msp, "Fc = T / r corona = 2.069 N (plano V)", (118.0, 157.6), 2.1)
    yb = 140.1
    linea(msp, (121.9, yb), (224.3, yb), lw=50)
    for x, nom in ((124.4, "A"), (217.5, "B")):
        poli(msp, [(x, yb), (x - 2.0, yb - 2.8), (x + 2.0, yb - 2.8)], cerrada=True)
        tn(msp, nom, (x, yb - 6.6), 2.4, "MIDDLE_CENTER")
    for x in (135.4, 206.4):
        flecha(msp, (x, 150.2), (x, yb), color=COL["rojo"], tam=2.0)
        t(msp, "P", (x, 152.0), 2.1, "BOTTOM_CENTER")
    flecha(msp, (222.2, 150.2), (222.2, yb), color=(90, 95, 110), tam=2.0)
    t(msp, "Fc", (223.4, 149.0), 2.1, "MIDDLE_LEFT")
    # momento flector
    ym = 120.1
    pts = [(124.4, ym), (135.4, 108.0), (206.4, 107.9), (217.6, 116.8), (222.2, ym)]
    relleno(msp, pts, AZUL_MF)
    poli(msp, pts, "CONTORNO")
    linea(msp, (121.9, ym), (224.3, ym))
    tn(msp, "Mf", (119.5, ym), 2.1, "MIDDLE_RIGHT")
    t(msp, "M máx = 1.142 N·m", (205.4, 105.7), 2.0, "TOP_RIGHT")
    # momento torsor
    yt = 98.2
    relleno_rect(msp, 206.4, 91.8, 222.2, yt, ROSA_MT)
    rect(msp, 206.4, 91.8, 222.2, yt)
    linea(msp, (121.9, yt), (224.3, yt))
    tn(msp, "Mt", (119.5, yt), 2.1, "MIDDLE_RIGHT")
    t(msp, "T = 471 N·m", (205.4, 95.0), 2.0, "MIDDLE_RIGHT")


# ---------------------------------------------------------------- D - chaveta (1:2)

def vista_d(msp):
    k = factor("1:2")
    titulo_vista(msp, "D - CHAVETA  -  ESC. 1:2", 24.2, 72.5, 3.2)
    cx, cy = 52.0, 40.5
    r_cubo, r_eje = 50 * k, 25 * k
    yk0, yk1 = cy + (25 - 5.5) * k, cy + (25 - 5.5 + 9) * k        # chaveta 14×9, t1 = 5,5
    xk0, xk1 = cx - 7 * k, cx + 7 * k
    # eje cortado (con el chavetero) y chaveta
    n = 48
    a_ch = math.asin(7 / 25)
    pts = []
    for i in range(n + 1):
        a = math.pi / 2 + a_ch + (2 * math.pi - 2 * a_ch) * i / n
        pts.append((cx + r_eje * math.cos(a), cy + r_eje * math.sin(a)))
    pts += [(xk1, cy + math.sqrt(r_eje ** 2 - (7 * k) ** 2)), (xk1, yk0), (xk0, yk0)]
    rayado(msp, pts, escala=0.35)
    poli(msp, pts, cerrada=True)
    rayado(msp, [(xk0, yk0), (xk1, yk0), (xk1, yk1), (xk0, yk1)], escala=0.12, patron="ANSI37", angulo=45)
    rect(msp, xk0, yk0, xk1, yk1)
    circulo(msp, (cx, cy), r_cubo)
    eje_h(msp, cx - r_cubo - 3, cx + r_cubo + 3, cy)
    eje_v(msp, cx, cy - r_cubo - 3, cy + r_cubo + 2.5)
    # cotas
    cota_txt(msp, (xk0, yk1), (xk1, yk1), (cx, yk1 + 6.0), (cx - 4.6, yk1 + 7.4), k)
    cota(msp, (xk1, yk0), (xk1, yk1), -9.0, k)
    cota_txt(msp, (cx, cy + r_eje), (cx, cy - r_eje), (cx - 19.0, cy), (cx - 20.4, cy + 6.5), k, "Ø<>",
             vertical=True)
    # referencias
    a = math.radians(-35)
    pc = (cx + r_cubo * math.cos(a), cy + r_cubo * math.sin(a))
    linea(msp, pc, (77.0, 26.0), "COTAS")
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc(pc, 0.55, 0, 360)
    t(msp, "cubo de la corona Z75 (Ø100)", (78.0, 26.0), 1.8, "MIDDLE_LEFT")
    t(msp, "chaveta paralela 14×9×63\nDIN 6885 A - acero C45", (78.0, 22.6), 2.0, "TOP_LEFT")


# ---------------------------------------------------------------- E - tensor del reenvío (1:5)

def vista_e(msp):
    titulo_vista(msp, "E - TENSOR DEL TAMBOR DE REENVÍO  -  ESC. 1:5", 86.6, 72.5, 3.2)
    cx, cy = 128.4, 45.8
    rect(msp, 86.6, 38.3, 170.1, 53.3)                 # bastidor
    rect(msp, 89.1, 42.4, 167.5, 49.2)                 # colisa
    relleno_rect(msp, 120.8, 35.0, 135.9, 56.7, (255, 255, 255))
    rect(msp, 120.8, 35.0, 135.9, 56.7)                # caja de la unidad UCT 210
    circulo(msp, (cx, cy), 6.2)
    circulo(msp, (cx, cy), 5.0)                         # Ø50 a 1:5
    rect(msp, 135.9, cy - 2.0, 183.5, cy + 2.0)         # tornillo M20
    for x0 in (172.2, 176.3):
        relleno_rect(msp, x0, cy - 3.2, x0 + 3.0, cy + 3.2, (255, 255, 255))
        rect(msp, x0, cy - 3.2, x0 + 3.0, cy + 3.2)
    eje_v(msp, cx, 32.4, 59.0)
    eje_h(msp, 118.2, 138.6, cy)
    tn(msp, "UCT 210 (muñón Ø50)", (cx, 60.3), 2.1, "BOTTOM_CENTER")
    t(msp, "eje de reenvío SAE 1045: Ø60 entre cubos,\nmuñones Ø50 k6, escalón r = 2 (Rev. E)", (88.0, 66.0), 1.8, "TOP_LEFT")
    t(msp, "tornillo M20 + contratuerca", (162.0, 56.2), 1.9, "BOTTOM_LEFT")
    # carrera del tensor: 150 mm a 1:5
    c = 150 * factor("1:5")
    flecha(msp, (cx, 30.0), (cx - c / 2, 30.0), "COTAS", tam=1.8)
    flecha(msp, (cx, 30.0), (cx + c / 2, 30.0), "COTAS", tam=1.8)
    t(msp, "carrera 150", (cx, 28.4), 2.0, "TOP_CENTER")


# ---------------------------------------------------------------- tabla

def tabla_datos(msp):
    subtitulo(msp, "DATOS Y VERIFICACIONES (por tambor motriz)", 232.2, 163.0, 3.0)
    filas = [
        ["Magnitud", "Criterio / fórmula", "Resultado"],
        ["Tensión efectiva Fe", "μ·g·(m carg + m ret)·1,15", "2.978 N"],
        ["Tensión mínima lado flojo", "Fe / (exp(μθ) - 1), μ = 0,35", "1.487 N"],
        ["T2 (ajuste del tensor) / T1", "T1 = Fe + T2", "2.000 / 4.978 N"],
        ["Tensión máx. de la malla", "T1 / B (adm. 4.000 N/m)", "2.489 N/m - CS 1,6"],
        ["Par en el tambor", "Fe · r (r = 158 mm)", "471 N·m"],
        ["Velocidad del tambor", "v / (π·D) con v = 0,37 m/min", "0,373 rpm"],
        ["Relación total / frecuencia", "300 × 5 = 1.500 → 0,93 m/min a 50 Hz", "f = 20 Hz"],
        ["Tiro de la cadena", "T / (Dp2/2)", "2.069 N - CS 15"],
        ["Reacciones en apoyos", "planos H y V combinados", "RA 3.506 / RB 4.364 N"],
        ["Momento flector máx.", "en el cubo lado Sur", "1.142 N·m"],
        ["Diámetro requerido", "ASME: Km 1,5 - Kt 1,0 - τadm 70 MPa", "50,6 mm"],
        ["Diámetro adoptado", "SAE 1045 - Ø60 (Ø50 corona)", "τ = 42 MPa - CS 2,2"],
        ["Chaveta 14×9×63", "corte / aplastamiento", "21 / 85 MPa"],
        ["Vida rodamiento UCF 212", "L10 = (C/P)³ ; C = 52,5 kN; s0 = C0/P", "> 10⁷ h ; s0 = 8,2"],
        ["Fatiga eje (Rev. E)", "DE-Goodman, Shigley cap. 6-7; S1 cubo", f"n = {coma(FAT['n_min'], 2)} (≥ 1,5)"],
        ["Asiento del cubo (Rev. E)", "rectificado Ra 0,8 µm; escalón r = 2", "Se = " + coma(FAT['secciones'][0]['Se'], 0) + " MPa"],
        ["Límite de par del VFD", "1,5 × T contra atascamiento", f"{FAT['atasco']['T_limite_VFD']} N·m (n = {coma(FAT['atasco']['n_limite'], 1)})"],
        ["Eje de reenvío (Rev. E)", "Ø60 entre cubos, muñones Ø50", f"n = {coma(REE['casos'][1]['n'], 2)} (Ø50: {coma(REE['casos'][0]['n'], 2)})"],
    ]
    tabla(msp, 232.2, 161.0, [47.8, 72.1, 54.9], filas, h_fila=3.8, altura=1.9,
          sombras={i: (243, 245, 248) for i in range(2, 18, 2)})


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "UCF 212 fuera de la cámara; eje Ø60 a flexotorsión (Ø50 corona); Z75 = Ø455 prim"),
            ("C", "09/2026", "Detalle D dentro del recuadro (eje cruzaba el margen); rotulado cubo de corona"),
            ("D", "10/2026", "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24"),
            ("E", FECHA, "Fatiga: asiento de cubo rectificado, límite de par VFD, reenvío Ø60/Ø50")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(3, "TAMBOR MOTRIZ, EJE, APOYOS\nY TRANSMISIÓN", "1:10 / 1:5 / 1:2", revs)
    vista_a(msp)
    vista_b(msp)
    vista_c(msp)
    vista_d(msp)
    vista_e(msp)
    tabla_datos(msp)
    exportar_lamina(doc, 3)


if __name__ == "__main__":
    main()
