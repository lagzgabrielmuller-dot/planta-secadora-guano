"""P20 - Sistema de biogás: planta 1:250, corte 1:100, diagrama de proceso S/E y balance.

Redibujo vectorial de la lámina 20 (Rev. D, sin cambios de contenido).
Planta: coordenadas del modelo 3D Rev. D (visor.html, __revDBuild, partes E8.1 a E8.6), en m.
Balance: transcripto de la lámina original (ver control contra resultados.json -> biogas al final).
"""
import json
import math
import os

from lamina_secadora import (COL, FECHA, cota, escala_grafica, exportar_lamina, factor, flecha, lamina, linea,
                             norte, poli, rayado, rect, relleno, relleno_circulo, relleno_rect, subtitulo, t,
                             tabla, titulo_vista, tn, circulo)

AQUI = os.path.dirname(os.path.abspath(__file__))
BIO = json.load(open(os.path.join(AQUI, "..", "calculos", "resultados.json"), encoding="utf-8"))["biogas"]

GAS = COL["biogas"]
ROJO = (220, 40, 40)
GRIS = (128, 128, 128)
AZUL = (40, 140, 200)
ROJO_INC = (200, 16, 46)

# ---------------------------------------------------------------- A - planta 1:250
KA = factor("1:250") * 1000.0          # mm de papel por metro
OX, OY = 65.94 - 68 * KA, 236.5 - 31 * KA


def P(x, y):
    """Coordenadas del modelo (m) -> papel (mm)."""
    return (OX + x * KA, OY + y * KA)


def discontinua(msp, pts, capa="CONTORNO", color=None, lw=None, d=1.6, g=1.0):
    """Polilínea de trazos dibujada con segmentos (se ve igual en DXF, PDF y PNG)."""
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        s = 0.0
        while s < L - 1e-6:
            e = min(s + d, L)
            linea(msp, (ax + (bx - ax) * s / L, ay + (by - ay) * s / L),
                  (ax + (bx - ax) * e / L, ay + (by - ay) * e / L), capa, color, lw)
            s = e + g


def circ_disc(msp, c, r, capa="FINO", color=None, lw=None, d=1.6, g=1.0):
    n = max(24, int(2 * math.pi * r / 0.8))
    pts = [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    discontinua(msp, pts, capa, color, lw, d, g)


def PR(x0, y0, x1, y1):
    a, b = P(x0, y0), P(x1, y1)
    return a[0], a[1], b[0], b[1]


def tubo(msp, pts, color, lw=50, discont=False):
    if discont:
        discontinua(msp, [P(*p) for p in pts], "CONTORNO", color, lw, 2.0, 1.2)
    else:
        poli(msp, [P(*p) for p in pts], "CONTORNO", color=color, lw=lw)


def circ_lleno(msp, c, r, rgb, lw=None, color=None):
    relleno_circulo(msp, c, r, rgb)
    circulo(msp, c, r, "CONTORNO", color=color, lw=lw)


def detector(msp, x, y):
    """Detector de CH4/H2S con baliza (G)."""
    c = P(x, y)
    relleno_rect(msp, c[0] - 0.9, c[1] - 0.9, c[0] + 0.9, c[1] + 0.9, (240, 190, 40))
    rect(msp, c[0] - 0.9, c[1] - 0.9, c[0] + 0.9, c[1] + 0.9, "FINO")
    tn(msp, "G", c, 1.2, "MIDDLE_CENTER")


def matafuego(msp, x, y, n):
    c = P(x, y)
    pts = [(c[0] - 1.3, c[1] - 1.1), (c[0] + 1.3, c[1] - 1.1), (c[0], c[1] + 1.3)]
    relleno(msp, pts, ROJO_INC)
    tn(msp, str(n), (c[0] + 1.8, c[1] - 0.6), 1.8, "MIDDLE_LEFT", color=ROJO_INC)


def planta(msp):
    titulo_vista(msp, "A - PLANTA DE LA ZONA DE BIOGÁS (Sector Este) - ESC. 1:250", 26, 279.2, 3.3)
    # fondo del predio y zona clasificada cercada
    x0, y0, x1, y1 = PR(58.0, 13.15, 98.0, 40.1)
    relleno_rect(msp, x0, y0, x1, y1, (242, 245, 238))
    fx0, fy0, fx1, fy1 = PR(60, 16, 96, 38)
    relleno_rect(msp, fx0, fy0, fx1, fy1, (255, 248, 224))
    # portón R7 (acceso de servicio y bomberos)
    rx0, ry0, rx1, _ = PR(84, 13.15, 92, 16)
    relleno_rect(msp, rx0, ry0, rx1, fy0, (216, 216, 216))
    t(msp, "portón R7", (rx0 + 5, (ry0 + fy0) / 2), 1.8, "MIDDLE_LEFT")
    # cerco (con aberturas como en el modelo)
    for a, b in (((60, 16), (63.5, 16)), ((65, 16), (84, 16)), ((90, 16), (96, 16)),
                 ((60, 16), (60, 38)), ((60, 38), (96, 38)), ((96, 16), (96, 38))):
        discontinua(msp, [P(*a), P(*b)], "CONTORNO", lw=50, d=2.0, g=1.0)

    # zona clasificada ATEX: 3 m alrededor de los domos
    for xc in (68, 78.5):
        circ_disc(msp, P(xc, 31), (3.25 + 3.0) * KA, "FINO", color=GAS)

    # cañerías (debajo de los equipos)
    # agua caliente de la cogeneración a los serpentines
    for xc in (68, 78.5):
        tubo(msp, [(xc - 1.6, 31 - 3.25), (xc - 1.6, 24.4), (66.4, 24.4), (66.4, 20.44)], ROJO, 35)
    # alimentación (PVC) desde el tanque de mezcla
    tubo(msp, [(91.8, 23.6), (91.8, 21.3), (78.5, 21.3), (78.5, 27.75)], GRIS, 50)
    tubo(msp, [(78.5, 21.3), (68.0, 21.3), (68.0, 27.75)], GRIS, 50)
    tubo(msp, [(81.75, 31.3), (85.0, 31.3)], GRIS, 50)
    # biogás: domos -> colector -> trampa/desulfurador -> soplante -> antorcha
    tubo(msp, [(64.5, 31), (64.5, 26.5), (84.4, 26.5), (84.4, 32.0)], GAS, 70)
    tubo(msp, [(75.0, 31), (75.0, 26.5)], GAS, 70)
    tubo(msp, [(69.5, 26.5), (69.5, 19.6)], GAS, 70)
    tubo(msp, [(72.0, 18.6), (72.0, 21.75), (95.0, 21.75), (95.0, 18.2)], GAS, 70)
    # línea enterrada al quemador piloto del hogar (E8.6)
    tubo(msp, [(71.3, 18.3), (71.3, 17.4), (61.5, 17.4), (61.5, 16.5), (58.0, 16.5)], GAS, 70, True)

    # biodigestores BD-1 y BD-2 (Ø6,5 m, base Ø7,5 m)
    for xc, tag in ((68, "BD-1"), (78.5, "BD-2")):
        c = P(xc, 31)
        circ_lleno(msp, c, 3.75 * KA, (222, 222, 222), lw=25)
        circ_lleno(msp, c, 3.25 * KA, (208, 224, 220), lw=70)
        tn(msp, tag, c, 2.2, "MIDDLE_CENTER")
    # T3 tanque de digestato (Ø8,0 m)
    c = P(89, 33)
    circ_lleno(msp, c, 4.4 * KA, (222, 222, 222), lw=25)
    circ_lleno(msp, c, 4.0 * KA, (218, 230, 200), lw=70)
    tn(msp, "T3", (c[0], c[1] + 1.0), 2.2, "MIDDLE_CENTER")
    # tanque de mezcla
    c = P(92.5, 25.5)
    circ_lleno(msp, c, 1.75 * KA, (226, 226, 226), lw=50)
    tn(msp, "mezcla", c, 2.0, "MIDDLE_CENTER")
    # platea de sólidos y fosa del guano excedente
    x0, y0, x1, y1 = PR(82, 22, 86, 25)
    relleno_rect(msp, x0, y0, x1, y1, (236, 228, 214))
    rect(msp, x0, y0, x1, y1)
    tn(msp, "sólidos", ((x0 + x1) / 2, (y0 + y1) / 2), 2.0, "MIDDLE_CENTER")
    x0, y0, x1, y1 = PR(86, 17, 90, 20)
    relleno_rect(msp, x0, y0, x1, y1, (205, 184, 150))
    rect(msp, x0, y0, x1, y1)
    tn(msp, "fosa", ((x0 + x1) / 2, (y0 + y1) / 2), 2.0, "MIDDLE_CENTER")
    # separador M32 sobre plataforma
    x0, y0, x1, y1 = PR(83.2, 25.6, 86.0, 27.4)
    discontinua(msp, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], "CONTORNO", lw=35, d=1.2, g=0.8)
    cm = P(84.0, 29.0)
    t(msp, "separador M32", (cm[0], cm[1] - 1.7), 1.8, "TOP_CENTER")
    # sala de cogeneración (contenedor) y platea de tratamiento del gas
    x0, y0, x1, y1 = PR(68.1, 17.8, 71.7, 20.84)
    relleno_rect(msp, x0, y0, x1, y1, (236, 236, 236))
    rect(msp, x0, y0, x1, y1, "FINO")
    t(msp, "desulf.", (x1 - 0.6, y0 + 0.5), 1.8, "BOTTOM_RIGHT")
    x0, y0, x1, y1 = PR(69.2, 19.0, 69.8, 19.6)          # trampa de condensados
    relleno_rect(msp, x0, y0, x1, y1, (255, 255, 255))
    rect(msp, x0, y0, x1, y1, "FINO")
    circ_lleno(msp, P(70.6, 19.3), 0.5 * KA, (255, 255, 255), lw=25)   # desulfurador
    x0, y0, x1, y1 = PR(71.4, 18.3, 72.0, 18.9)          # soplante M33
    relleno_rect(msp, x0, y0, x1, y1, (200, 160, 20))
    rect(msp, x0, y0, x1, y1, "FINO")
    x0, y0, x1, y1 = PR(62, 18, 68.1, 20.44)
    relleno_rect(msp, x0, y0, x1, y1, (183, 212, 192))
    rect(msp, x0, y0, x1, y1)
    tn(msp, "CHP", ((x0 + x1) / 2, (y0 + y1) / 2), 2.0, "MIDDLE_CENTER")
    x0, y0, x1, y1 = PR(62.4, 21.2, 63.4, 21.6)          # tablero TS-BIO
    rect(msp, x0, y0, x1, y1, "FINO")
    t(msp, "TS-BIO", (x0, y1 + 2.5), 1.8, "BOTTOM_LEFT")
    # antorcha
    c = P(95, 18.2)
    circulo(msp, c, 0.6 * KA, "FINO")
    circ_lleno(msp, c, 0.38 * KA, (70, 70, 70))
    t(msp, "antorcha", (c[0] + 1.2, c[1] - 3.3), 1.8, "TOP_RIGHT")
    # detectores de gas, matafuegos (19 a 21) e hidrante HI-4
    for d in ((66, 20.5), (78, 26.5), (90, 28.5)):
        detector(msp, *d)
    matafuego(msp, 68.4, 20.6, 20)
    matafuego(msp, 83.0, 17.2, 19)
    matafuego(msp, 84.0, 29.0, 21)
    c = P(82, 14)
    circulo(msp, c, 1.4, "CONTORNO", color=ROJO_INC)
    relleno_circulo(msp, c, 0.55, ROJO_INC)
    linea(msp, (c[0] + 1.4, c[1]), (c[0] + 2.4, c[1]), "CONTORNO", color=ROJO_INC)
    tn(msp, "HI-4", (c[0], c[1] + 2.0), 1.8, "BOTTOM_CENTER", color=ROJO_INC)
    # cotas
    k = factor("1:250")
    ytop = P(0, 34.75)[1]
    cota(msp, P(64.75, 34.75), P(71.25, 34.75), distancia=261.3 - ytop, escala=k, valor="Ø6.500")
    cota(msp, P(71.75, 31), P(74.75, 31), distancia=0.0, escala=k, valor="3.000")
    y_t3 = P(0, 37.4)[1]
    cota(msp, P(85, 37.4), P(93, 37.4), distancia=267.6 - y_t3, escala=k, valor="Ø8.000")
    norte(msp, 180.0, 259.0, 5.0)
    escala_grafica(msp, 26.0, 156.7, "1:250", 20, 5)


# ---------------------------------------------------------------- B - corte 1:100
def elipse(cx, cy, a, b, n=60):
    return [(cx + a * math.cos(math.pi * i / n), cy + b * math.sin(math.pi * i / n)) for i in range(n + 1)]


def corte(msp):
    titulo_vista(msp, "B - CORTE DE UN BIODIGESTOR - ESC. 1:100", 195.9, 279.2, 3.3)
    k = factor("1:100")
    K = k * 1000.0
    cx, y0 = 240.2, 187.7                 # eje y cara superior de la platea
    ri = 3.25 * K                         # radio interior
    h_muro, h_liq, flecha_domo = 4.75 * K, 4.0 * K, 2.0 * K
    xi0, xi1 = cx - ri, cx + ri
    # platea
    pl = [(cx - 4.0 * K, y0 - 0.55 * K), (cx + 4.0 * K, y0 - 0.55 * K), (cx + 4.0 * K, y0), (cx - 4.0 * K, y0)]
    rayado(msp, pl, escala=0.5)
    poli(msp, pl, "CONTORNO", cerrada=True)
    # digestato
    relleno_rect(msp, xi0, y0, xi1, y0 + h_liq, (208, 224, 220))
    # muros: chapa (verde oscuro) + aislación (amarillo)
    for s in (-1, 1):
        xa = cx + s * ri
        relleno_rect(msp, min(xa, xa + s * 1.0), y0, max(xa, xa + s * 1.0), y0 + h_muro, (53, 95, 87))
        relleno_rect(msp, min(xa + s * 1.0, xa + s * 2.0), y0, max(xa + s * 1.0, xa + s * 2.0), y0 + h_muro,
                     (238, 228, 160))
        rect(msp, min(xa, xa + s * 2.0), y0, max(xa, xa + s * 2.0), y0 + h_muro, "FINO")
    # techo de doble membrana (casquete) y membrana interior
    poli(msp, elipse(cx, y0 + h_muro, ri + 0.5, flecha_domo), "CONTORNO", color=(90, 90, 90), lw=50)
    discontinua(msp, elipse(cx, y0 + h_muro, ri - 0.5, 1.3 * K), "FINO", (90, 90, 90), 35, 1.6, 1.0)
    # nivel del líquido
    discontinua(msp, [(xi0, y0 + h_liq), (xi1, y0 + h_liq)], "FINO", AZUL, 35, 1.6, 1.0)
    # serpentín de agua caliente
    for zz in (0.92, 0.63):
        discontinua(msp, [(xi0 + 2.0, y0 + zz * K), (xi1 - 2.0, y0 + zz * K)], "FINO", ROJO, 35, 1.6, 1.0)
    t(msp, "serpentín de agua caliente", (xi0 + 0.6, y0 + 1.6), 1.8, "BOTTOM_LEFT")
    # agitador M28/M29
    poli(msp, [(252.1, y0 + h_muro), (257.9, 221.0), (253.1, 209.0)], "CONTORNO", lw=50)
    relleno_rect(msp, 249.9, 204.9, 254.6, 209.0, (110, 125, 140))
    rect(msp, 249.9, 204.9, 254.6, 209.0, "FINO")
    t(msp, "agitador M28/M29", (248.8, 203.6), 1.8, "MIDDLE_RIGHT")
    circulo(msp, (cx, 221.0), 1.1, "FINO")
    t(msp, "digestato a 38 °C", (cx, 213.5), 1.8, "MIDDLE_CENTER")
    tn(msp, "biogás", (cx, y0 + h_muro + 3.4), 1.9, "MIDDLE_CENTER")
    t(msp, "techo de doble membrana (gasómetro 37 m³)", (cx, y0 + h_muro + 7.9), 1.8, "MIDDLE_CENTER")
    # salida de gas y válvula de sobrepresión/depresión
    xg = cx - 0.6 * K
    yg = y0 + h_muro + flecha_domo * math.sqrt(max(0.0, 1 - ((xg - cx) / (ri + 0.5)) ** 2))
    linea(msp, (xg, yg - 0.3), (xg, yg + 3.5), "CONTORNO", color=GAS, lw=70)
    t(msp, "salida de gas", (xg - 1.5, yg + 6.0), 1.8, "BOTTOM_RIGHT")
    xv = cx + 0.9 * K
    yv = y0 + h_muro + flecha_domo * math.sqrt(max(0.0, 1 - ((xv - cx) / (ri + 0.5)) ** 2))
    relleno_rect(msp, xv - 1.4, yv - 0.4, xv + 1.4, yv + 2.6, (200, 200, 200))
    rect(msp, xv - 1.4, yv - 0.4, xv + 1.4, yv + 2.6, "FINO")
    t(msp, "válvula P/V", (xv + 2.0, yv + 6.0), 1.8, "BOTTOM_LEFT")
    # entrada y rebalse a T3
    ye, yr = 200.0, 224.1
    linea(msp, (196.5, ye), (xi0 - 2.0, ye), "CONTORNO", color=GRIS, lw=70)
    t(msp, "entrada", (196.5, ye - 1.0), 1.8, "TOP_LEFT")
    linea(msp, (xi1 + 2.0, yr), (cx + 4.0 * K + 3.0, yr), "CONTORNO", color=GRIS, lw=70)
    t(msp, "rebalse\na T3",(xi1 + 2.4, yr + 1.0), 1.8, "BOTTOM_LEFT")
    # cotas
    cota(msp, (xi0, y0), (xi1, y0), distancia=-9.3, escala=k, valor="6.500")
    cota(msp, (xi0 - 2.0, y0), (xi0 - 2.0, y0 + h_liq), distancia=11.4, escala=k, valor="4.000 líquido")
    cota(msp, (xi1 + 2.0, y0), (xi1 + 2.0, y0 + h_muro), distancia=-12.0, escala=k, valor="4.750")


# ---------------------------------------------------------------- C - diagrama de proceso
def caja(msp, x, y, w, h, nombre, dato, rgb):
    relleno_rect(msp, x, y - h, x + w, y, rgb)
    rect(msp, x, y - h, x + w, y, "CONTORNO", lw=50)
    tn(msp, nombre, (x + w / 2, y - h * 0.36), 2.0, "MIDDLE_CENTER")
    t(msp, dato, (x + w / 2, y - h * 0.72), 1.8, "MIDDLE_CENTER")


def diagrama(msp):
    yt = 144.0
    titulo_vista(msp, "C - DIAGRAMA DE PROCESO DEL BIOGÁS - S/E", 26, yt, 3.3)
    W, H = 30.0, 10.0
    xs = [26.0, 60.1, 94.1, 128.1, 162.1, 196.1]
    r1, r2, r3 = 135.1, 118.1, 101.1
    verde, celeste, beige, amarillo = (236, 243, 232), (231, 239, 245), (240, 232, 218), (255, 243, 205)
    fila1 = [("Guano excedente", "2,52 t/día", verde), ("Tanque de mezcla", "8 % sólidos", verde),
             ("BD-1 + BD-2", "282 m³ · 38 °C", verde), ("Tanque T3", "201 m³", verde),
             ("Separador M32", "tornillo prensa", verde), ("Sólido", "1,8 t/día", beige)]
    for x, (n, d, c) in zip(xs, fila1):
        caja(msp, x, r1, W, H, n, d, c)
    for a, b in zip(xs[:-1], xs[1:]):
        flecha(msp, (a + W, r1 - H / 2), (b - 0.3, r1 - H / 2), "CONTORNO", color=(85, 85, 85), tam=1.8, lw=35)
    caja(msp, xs[0], r2, W, H, "Lixiviados y lavados", "2,3 m³/día", celeste)
    flecha(msp, (xs[0] + W / 2, r2), (xs[1] + 7.0, r1 - H - 0.2), "CONTORNO", color=AZUL, tam=1.8, lw=35)
    caja(msp, xs[4], r2, W, H, "Líquido", f"{BIO['liquido']:.2f}".replace(".", ",") + " m³/día a venta", celeste)
    flecha(msp, (xs[4] + W / 2, r1 - H), (xs[4] + W / 2, r2 + 0.2), "CONTORNO", color=(85, 85, 85), tam=1.8, lw=35)
    # recirculación de líquido al tanque de mezcla
    yrc = 121.5
    poli(msp, [(xs[4] + 3.8, r1 - H), (xs[4] + 3.8, yrc), (xs[1] + 20.0, yrc)], "CONTORNO", color=AZUL, lw=50)
    flecha(msp, (xs[1] + 20.0, yrc), (xs[1] + 20.0, r1 - H - 0.2), "CONTORNO", color=AZUL, tam=1.8, lw=50)
    t(msp, "recirculación 4,6 m³/día", (xs[3] + W / 2, yrc + 0.8), 1.8, "BOTTOM_CENTER", color=AZUL)
    # gas
    xg = xs[2] + W / 2
    flecha(msp, (xg, r1 - H), (xg, r3 + 0.2), "CONTORNO", color=GAS, tam=1.8, lw=50)
    fila3 = [("Domos (gas)", "184 m³/día"), ("Trampa + desulf.", "H2S → óxido de Fe"),
             ("Soplante M33", "medidor + CH4/H2S")]
    for x, (n, d) in zip(xs[2:5], fila3):
        caja(msp, x, r3, W, H, n, d, amarillo)
    for a, b in zip(xs[2:4], xs[3:5]):
        flecha(msp, (a + W, r3 - H / 2), (b - 0.3, r3 - H / 2), "CONTORNO", color=GAS, tam=1.8, lw=50)
    xd, wd = 206.0, 36.0
    destinos = [(112.8, "Cogeneración 25 kWe", "318 kWh/día"), (100.9, "Quemador piloto hogar", "12 m³/día"),
                (88.9, "Antorcha", "excedentes")]
    for y, n, d in destinos:
        caja(msp, xd, y, wd, H, n, d, amarillo)
        flecha(msp, (xs[4] + W, r3 - H / 2), (xd - 0.3, y - H / 2), "CONTORNO", color=GAS, tam=1.8, lw=50)
    t(msp, "calor (agua a 70 °C) → BD-1 y BD-2", (xd + wd / 2, 114.6), 1.8, "BOTTOM_CENTER", color=ROJO)


# ---------------------------------------------------------------- D - balance y seguridad
BALANCE = [
    ("Guano no procesado por la secadora", "920 t/año"),
    ("Alimentación (8 % ST)", "9,40 m³/día"),
    ("Sólidos volátiles", "526 kg SV/día"),
    ("Volumen útil / TRH", "282 m³ / 30 días"),
    ("Carga orgánica", "1,87 kg SV/m³·día"),
    ("Biogás (0,35 m³/kg SV)", "184 m³/día"),
    ("Metano / PCI", "58 % / 20,8 MJ/m³"),
    ("Energía del biogás", f"{BIO['E_MJ']:,} MJ/día".replace(",", ".")),
    ("Encendido + piloto del hogar", "12,1 m³/día"),
    ("Electricidad (CHP 25 kWe, η 32 %)", "318 kWh/día"),
    ("Horas de marcha del CHP", "12,7 h/día"),
    ("Calor útil (η 48 %)", f"{BIO['calor']} kWh/día"),
    ("Calor para digestores (media/invierno)", f"{BIO['calor_med'][-1]} / {BIO['calor_inv'][-1]} kWh/día"),
    ("Almacenamiento de gas", f"{BIO['almacen']} m³ = {BIO['h_almacen']:.1f} h".replace(".", ",")),
    ("Digestato líquido a T3", f"{BIO['liquido']:.2f}".replace(".", ",") + f" m³/día · {BIO['dias_T3']} días"),
]


def balance(msp):
    subtitulo(msp, "D - BALANCE DE MASA Y ENERGÍA", 291.9, 269.0, 2.6)
    filas = [["Balance diario (promedio anual)", "Valor"]] + [list(f) for f in BALANCE]
    y = tabla(msp, 291.9, 267.0, [76.4, 39.7], filas, h_fila=3.3, altura=1.9, alin=["L", "L"])
    subtitulo(msp, "SEGURIDAD DEL SISTEMA DE BIOGÁS", 291.9, y - 6.0, 2.6)
    t(msp, "\n".join([
        "• Zona clasificada ATEX: 3 m alrededor de domos y válvulas",
        "(círculo punteado); equipos eléctricos Ex en esa zona.",
        "• Válvulas de sobrepresión/depresión en cada domo,",
        "arrestallamas en la antorcha y en el quemador piloto.",
        "• Detectores de CH4/H2S (G) con baliza: cortan el soplante.",
        "• Cerco propio, portón con cartel, prohibido fumar y llamas.",
        "• Distancias: hogar ↔ BD-1 36 m; antorcha ↔ domos > 12 m.",
        "• Amoníaco: controlar NH4+ < 3 g/l (dilución y recirculación).",
        "• El agua del vado sanitario (desinfectante) no ingresa.",
    ]), (291.9, y - 8.5), 1.85, "TOP_LEFT")


def control_balance():
    """Compara el balance de la lámina con resultados.json -> biogas (solo informa)."""
    b = BIO
    esperado = {
        "Alimentación (8 % ST)": f"{b['Q_alim']:.2f}".replace(".", ","),
        "Sólidos volátiles": str(b["SV_kg"]),
        "Volumen útil / TRH": f"{b['V_util']} m³ / {b['TRH']}",
        "Carga orgánica": f"{b['carga']:.2f}".replace(".", ","),
        "Biogás (0,35 m³/kg SV)": str(b["biogas"]),
        "Metano / PCI": f"{round(b['CH4'] * 100)} % / {b['PCI']:.1f}".replace(".", ","),
        "Energía del biogás": f"{b['E_MJ']:,}".replace(",", "."),
        "Encendido + piloto del hogar": f"{b['piloto']:.1f}".replace(".", ","),
        "Electricidad (CHP 25 kWe, η 32 %)": str(b["E_el"]),
        "Horas de marcha del CHP": f"{b['horas']:.1f}".replace(".", ","),
        "Calor útil (η 48 %)": str(b["calor"]),
        "Calor para digestores (media/invierno)": f"{b['calor_med'][-1]} / {b['calor_inv'][-1]}",
        "Almacenamiento de gas": f"{b['almacen']} m³ = {b['h_almacen']:.1f}".replace(".", ","),
        "Digestato líquido a T3": f"{b['liquido']:.2f}".replace(".", ",") + f" m³/día · {b['dias_T3']}",
    }
    for nombre, valor in BALANCE:
        e = esperado.get(nombre)
        if e and e not in valor:
            print(f"  DIFERENCIA con resultados.json: {nombre}: lámina '{valor}' / JSON '{e}'")


def main():
    revs = [("D", "09/2026", "Emisión original: biodigestores BD-1 y BD-2, digestato, cogeneración, antorcha y "
                             "línea al quemador piloto"),
            ("E", FECHA, "Calor de digestores y digestato unificados con la memoria (U por capas, ISO 6946)")]
    doc, msp, z = lamina(20, "SISTEMA DE BIOGÁS: PLANTA,\nCORTE Y BALANCE", "1:250 / 1:100", revs)
    planta(msp)
    corte(msp)
    diagrama(msp)
    balance(msp)
    control_balance()
    exportar_lamina(doc, 20)


if __name__ == "__main__":
    main()
