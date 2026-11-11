"""P19 - Zaranda y envasado (zona 28): planta 1:50, corte A-A 1:100 y tablas.

Geometría (m) del modelo 3D: agregados E4 (zaranda y válvula desviadora), E5 (ensacadora 25 kg)
y E6 (bolsas chicas) del bloque Rev. D de visor.html, más layout_planta.json (G).
x al Este, y al Norte, origen en el vértice SO de la nave.
"""
import json
import math
import os

from lamina_secadora import (COL, exportar_lamina, factor, flecha, lamina, linea,
                             poli, rayado, rect, relleno, relleno_rect, subtitulo, suelo, t,
                             tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

# ---------------------------------------------------------------- vistas
K50 = factor("1:50") * 1000.0      # mm de papel por metro real (20)
K100 = factor("1:100") * 1000.0    # 10
PX0, PY0 = 26.0, 269.0             # papel de (x = 25,4; y = 18,0) en la planta
SX0, SZ0 = 130.6, 193.2            # corte: papel = SX0 + 10·y ; SZ0 + 10·z

GRIS_FONDO = (245, 246, 248)
DORADO = (190, 150, 30)
MARRON = (139, 90, 43)
GRIS_TRANSP = (188, 194, 198)
TROMMEL = (215, 220, 225)
CREMA = (255, 243, 214)


def P(x, y):
    """Planta 1:50: coordenadas del modelo (m) -> papel (mm)."""
    return (PX0 + (x - 25.4) * K50, PY0 + (y - 18.0) * K50)


def S(y, z):
    """Corte A-A 1:100 (x = 28,0 mirando al Oeste: el Norte queda a la derecha)."""
    return (SX0 + y * K100, SZ0 + z * K100)


def caja(f, x0, y0, x1, y1, fondo=None, capa="CONTORNO", tipo=None, color=None, lw=None):
    a, b = f(x0, y0), f(x1, y1)
    if fondo:
        relleno_rect(msp_, a[0], a[1], b[0], b[1], fondo)
    return rect(msp_, a[0], a[1], b[0], b[1], capa, color=color, lw=lw, tipo=tipo)


def barra(f, p0, p1, ancho, color, borde=None):
    """Conducto visto (franja de ancho real 'ancho' m) entre dos puntos del modelo."""
    a, b = f(*p0), f(*p1)
    k = K50 if f is P else K100
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    nx, ny = -dy / d * ancho * k / 2, dx / d * ancho * k / 2
    pts = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
    relleno(msp_, pts, color)
    if borde:
        poli(msp_, pts, "FINO", cerrada=True, color=borde)


def matafuego_existente(c, etiqueta):
    """Triángulo rojo con 'E' (matafuego existente Rev. C), como en el plano 15."""
    x, y = c
    s = 2.2
    pts = [(x - s / 2, y - s * 0.42), (x + s / 2, y - s * 0.42), (x, y + s * 0.5)]
    poli(msp_, pts, "CONTORNO", cerrada=True, color=COL["incendio"], lw=25)
    tn(msp_, "E", (x, y - 0.25), 1.1, "MIDDLE_CENTER", color=COL["incendio"])
    tn(msp_, etiqueta, (x + 1.8, y), 1.8, "MIDDLE_LEFT", color=COL["incendio"])


def parada(c, etiqueta):
    x, y = c
    relleno_rect(msp_, x - 1.0, y - 1.0, x + 1.0, y + 1.0, COL["amarillo_seg"])
    rect(msp_, x - 1.0, y - 1.0, x + 1.0, y + 1.0, "FINO")
    from lamina_secadora import relleno_circulo, circulo
    relleno_circulo(msp_, (x, y), 0.65, COL["rojo"])
    circulo(msp_, (x, y), 0.65, "FINO")
    tn(msp_, etiqueta, (x + 1.6, y), 1.8, "MIDDLE_LEFT")


def g(etq, cen, apunta, crema=False):
    """Globo de referencia en la planta (centro y punta en coordenadas del modelo)."""
    from lamina_secadora import circulo, relleno_circulo
    c, q, r = P(*cen), P(*apunta), 2.6
    relleno_circulo(msp_, c, r, CREMA if crema else (255, 255, 255))
    circulo(msp_, c, r, "COTAS")
    tn(msp_, etq, c, 1.8 if len(etq) <= 2 else 1.5, "MIDDLE_CENTER", capa="COTAS")
    dx, dy = q[0] - c[0], q[1] - c[1]
    d = math.hypot(dx, dy)
    linea(msp_, (c[0] + dx / d * r, c[1] + dy / d * r), q, "COTAS")
    h = msp_.add_hatch(dxfattribs={"layer": "COTAS"})
    h.paths.add_edge_path().add_arc(q, 0.5, 0, 360)


def cota_(p1, p2, distancia, valor):
    """Cota alineada con texto de 2,0 mm (valor real fijo, en mm)."""
    dim = msp_.add_aligned_dim(p1=p1, p2=p2, distance=distancia, dimstyle="IRAM", text=valor,
                               override={"dimtxt": 2.0, "dimasz": 2.0}, dxfattribs={"layer": "COTAS"})
    dim.render()


msp_ = None


# ---------------------------------------------------------------- planta 1:50
def planta(msp):
    titulo_vista(msp, "A - PLANTA DE LA ZONA 28 (ZARANDA Y ENVASADO) - ESC. 1:50", 26, 279, 3.3)
    # fondo de la zona
    caja(P, 25.4, 8.9, 33.29, 18.3, GRIS_FONDO, capa="AUXILIAR")
    # muro de acopio (y = 9,0, h 2,0 m) con rayado
    a, b = P(26.0, 8.9), P(33.0, 9.1)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.12, angulo=45)
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO")
    c = P(29.5, 9.0)
    relleno_rect(msp, c[0] - 13.5, c[1] - 1.5, c[0] + 13.5, c[1] + 1.5, GRIS_FONDO)
    t(msp, "muro de acopio h 2,0 m", c, 1.9, "MIDDLE_CENTER")
    # muro Norte con la puerta cortafuego PC1 (26,2 a 27,2) y columnas de los pórticos
    caja(P, 25.4, 17.94, 26.2, 18.06, (20, 20, 20))
    caja(P, 27.2, 17.94, 33.0, 18.06, (20, 20, 20))
    for xc in (27.5, 33.0):
        caja(P, xc - 0.15, 17.85, xc + 0.15, 18.15, (20, 20, 20))
    t(msp, "PC1 RF-60 (al anexo)", (P(26.7, 18.0)[0], P(26.7, 18.0)[1] + 1.6), 1.8, "BOTTOM_CENTER")
    # muro Este: SE1 (15,0 a 16,2) y portón P3 nuevo (12,4 a 14,9)
    caja(P, 32.94, 9.1, 33.06, 12.4, (20, 20, 20))
    caja(P, 32.94, 14.9, 33.06, 15.0, (20, 20, 20))
    caja(P, 32.94, 16.2, 33.06, 17.85, (20, 20, 20))
    tn(msp, "SE1", (P(33.0, 15.6)[0] + 2.2, P(33.0, 15.6)[1]), 2.0, "MIDDLE_CENTER", rotacion=90)
    # zona libre frente a SE1
    a, b = P(31.8, 14.9), P(33.0, 16.4)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.18, angulo=45, color=COL["salida"])
    rect(msp, a[0], a[1], b[0], b[1], "FINO", tipo="DASHED")
    t(msp, "zona libre", (P(32.4, 16.85)), 1.8, "MIDDLE_CENTER", color=COL["salida"])
    cota_(P(33.0, 12.4), P(33.0, 14.9), 8.0, "2.500")
    # recorrido de los pallets: fin de la cinta -> portón P3
    poli(msp, [P(31.8, 11.75), P(31.8, 13.65), P(33.0, 13.65)], "FINO", color=MARRON, lw=35, tipo="DASHED")
    flecha(msp, P(33.0, 13.65), P(33.45, 13.65), "FINO", MARRON, tam=2.2, lw=35)
    tn(msp, "P3 2.500", (P(33.0, 13.65)[0] + 3.9, P(33.0, 13.65)[1]), 2.0, "MIDDLE_CENTER", rotacion=90)

    # plataforma a +3,00 (E4) con escalera al Este
    a, b = P(26.6, 10.2), P(29.4, 14.2)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.3, angulo=135, color=DORADO)
    rect(msp, a[0], a[1], b[0], b[1], "FINO", color=DORADO, lw=35)
    caja(P, 29.4, 13.35, 30.9, 14.15, color=DORADO, capa="FINO")
    for i in range(1, 6):
        xx = 29.4 + 0.25 * i
        linea(msp, P(xx, 13.35), P(xx, 14.15), "FINO", DORADO)
    flecha(msp, P(30.8, 13.75), P(29.65, 13.75), "FINO", MARRON, tam=1.8)
    cota_(P(26.6, 10.2), P(26.6, 14.2), 6.0, "4.000")
    cota_(P(26.6, 10.2), P(29.4, 10.2), -6.0, "2.800")

    # big bag de rechazo
    caja(P, 27.5, 14.1, 28.5, 15.1, (237, 228, 210))
    t(msp, "big bag", P(28.0, 14.6), 1.8, "MIDDLE_CENTER")
    # trommel Ø0,9 × 3,0 (eje x = 28,0)
    caja(P, 27.55, 10.6, 28.45, 13.6, TROMMEL)
    for yy in (11.1, 12.6, 13.1):
        linea(msp, P(27.55, yy), P(28.45, yy), "AUXILIAR", (120, 120, 120))
    linea(msp, P(28.0, 10.3), P(28.0, 13.9), "EJES")
    # motorreductor M18
    caja(P, 28.35, 10.1, 28.95, 10.35, (110, 125, 140))
    # tolva pulmón (por encima, en trazos) y ensacadora
    caja(P, 27.62, 11.25, 28.38, 12.25, (255, 255, 255))
    caja(P, 27.35, 11.0, 28.65, 12.5, tipo="DASHED", capa="CONTORNO")
    # cinta de salida M21, cosedora M20 y bolsas
    caja(P, 27.7, 11.4, 31.0, 12.1, (232, 232, 232))
    caja(P, 29.2, 11.9, 29.7, 12.3, (222, 232, 245))
    caja(P, 29.3, 11.62, 29.72, 11.88, (220, 205, 170), capa="FINO")
    caja(P, 30.35, 11.6, 30.77, 11.9, (220, 205, 170), capa="FINO")
    flecha(msp, P(30.1, 11.75), P(30.95, 11.75), "FINO", MARRON, tam=1.8, lw=35)
    cota_(P(27.7, 12.1), P(31.0, 12.1), 3.6, "3.300")
    # pallets de producto embolsado
    for y0 in (9.4, 10.65):
        a, b = P(31.2, y0), P(32.4, y0 + 1.0)
        relleno_rect(msp, a[0], a[1], b[0], b[1], (232, 220, 190))
        rect(msp, a[0], a[1], b[0], b[1])
        linea(msp, a, b, "FINO")
        linea(msp, (a[0], b[1]), (b[0], a[1]), "FINO")
    # envasadora de bolsas chicas (E6), mesa y transportador flexible M24
    caja(P, 29.0, 16.0, 30.2, 17.2, (228, 231, 238))
    caja(P, 30.4, 16.6, 31.9, 17.4, (255, 255, 255))
    barra(P, (28.2, 12.3), (28.9, 15.2), 0.2, GRIS_TRANSP)
    barra(P, (28.9, 15.2), (29.6, 16.4), 0.2, GRIS_TRANSP)
    caja(P, 28.7, 15.0, 29.1, 15.4, (115, 130, 145))
    # elevador 7, válvula desviadora M35, bajada a la zaranda y pico al acopio
    barra(P, (26.2, 8.97), (26.55, 8.9), 0.3, GRIS_TRANSP)
    caja(P, 25.45, 8.8, 26.25, 9.8, (200, 200, 200))
    caja(P, 26.05, 9.03, 26.4, 9.53, (225, 230, 235))
    barra(P, (26.3, 9.58), (27.99, 10.45), 0.3, GRIS_TRANSP)
    tn(msp, "7", P(25.85, 10.15), 2.0, "MIDDLE_CENTER")
    tn(msp, "M35", P(26.1, 9.66), 1.8, "MIDDLE_CENTER")
    t(msp, "pico al acopio", P(27.25, 9.32), 1.8, "MIDDLE_CENTER")
    # seguridad
    matafuego_existente(P(27.5, 17.55), "07")
    matafuego_existente(P(32.6, 11.0), "08")
    parada(P(30.7, 10.25), "PE-07")
    # globos
    g("E6", (28.45, 17.2), (29.3, 16.6), crema=True)
    g("M22", (30.95, 15.2), (29.9, 16.2))
    g("M24", (27.5, 15.75), (28.9, 15.2))
    g("E4", (26.2, 13.0), (27.8, 12.85), crema=True)
    g("E5", (26.2, 11.6), (27.8, 11.8), crema=True)
    g("M19", (29.0, 13.0), (28.2, 11.6))
    g("M20", (29.65, 12.85), (29.45, 12.1))
    g("M21", (30.6, 12.7), (30.0, 11.8))
    g("M18", (29.55, 9.75), (28.7, 10.22))


# ---------------------------------------------------------------- corte A-A 1:100
def corte(msp):
    titulo_vista(msp, "B - CORTE A-A (x = 28,0; mirando al Oeste) - ESC. 1:100", 211.8, 279, 3.3)
    suelo(msp, S(8.6, 0)[0], S(18.4, 0)[0], SZ0)
    # muro Norte (y = 18), h alero 7,0
    a, b = S(17.95, 0), S(18.05, 7.0)
    relleno_rect(msp, a[0], a[1], b[0], b[1], (20, 20, 20))
    # elevador 7 con la válvula desviadora M35
    a, b = S(8.95, 0), S(9.15, 0.68)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.1, angulo=45)
    rect(msp, a[0], a[1], b[0], b[1], "FINO")
    caja(S, 8.85, 0.68, 9.75, 6.29, (222, 223, 225))
    caja(S, 8.85, 6.29, 9.75, 6.78, (200, 200, 200))
    caja(S, 9.05, 5.8, 9.55, 6.25, (225, 230, 235))
    tn(msp, "elevador 7", (S(8.85, 7.3)[0] + 0.5, S(0, 7.3)[1]), 1.8, "BOTTOM_LEFT")
    cota_(S(9.2, 0), S(9.2, 5.85), -1.5, "5.850")
    # bajada a la zaranda
    barra(S, (9.55, 5.82), (10.47, 4.45), 0.2, GRIS_TRANSP)
    flecha(msp, S(9.65, 5.27), S(10.2, 4.59), "FINO", MARRON, tam=1.8, lw=35)
    # plataforma +3,00, baranda 1,0 m y columnas
    for yy in (10.2, 14.2):
        linea(msp, S(yy, 0), S(yy, 3.0), "CONTORNO", (90, 90, 90))
    linea(msp, S(10.2, 3.0), S(14.2, 3.0), "CONTORNO", (40, 40, 40), lw=70)
    linea(msp, S(10.2, 3.05), S(14.2, 3.05), "FINO", DORADO, lw=35)
    poli(msp, [S(10.2, 3.05), S(10.2, 4.0), S(14.2, 4.0), S(14.2, 3.05)], "FINO", color=DORADO, lw=35)
    # trommel inclinado 5°
    pts = [S(10.6, 4.43), S(13.6, 4.17), S(13.6, 3.27), S(10.6, 3.53)]
    relleno(msp, pts, TROMMEL)
    poli(msp, pts, "CONTORNO", cerrada=True)
    linea(msp, S(10.4, 3.99), S(13.85, 3.70), "EJES")
    tn(msp, "zaranda Ø0,9 × 3,0 m (5°)", S(11.0, 4.9), 1.8, "BOTTOM_LEFT")
    # tolva pulmón 1,5 m³ y ensacadora
    pts = [S(11.0, 2.95), S(12.5, 2.95), S(12.05, 2.05), S(11.45, 2.05)]
    relleno(msp, pts, (238, 238, 238))
    poli(msp, pts, "CONTORNO", cerrada=True)
    flecha(msp, S(11.75, 2.85), S(11.75, 2.15), "FINO", MARRON, tam=1.6, lw=35)
    caja(S, 11.25, 1.52, 12.25, 2.03, (255, 255, 255))
    caja(S, 11.52, 0.53, 12.0, 1.1, (220, 205, 170))
    caja(S, 11.4, 0.45, 12.1, 0.53, (130, 130, 130), capa="FINO")
    tn(msp, "ensacadora", S(12.3, 0.95), 1.8, "MIDDLE_LEFT")
    # rechazo al big bag
    barra(S, (13.75, 3.33), (14.6, 1.23), 0.2, GRIS_TRANSP)
    caja(S, 14.1, 0.0, 15.1, 1.13, (237, 228, 210))
    tn(msp, "rechazo", (S(14.1, 1.75)[0] - 0.5, S(0, 1.75)[1]), 1.8, "MIDDLE_RIGHT")
    cota_(S(15.4, 0), S(15.4, 3.0), -2.0, "3.000")
    # envasadora de bolsas chicas
    caja(S, 16.0, 0.0, 17.2, 2.19, (228, 231, 238))
    pts = [S(16.3, 2.9), S(16.9, 2.9), S(16.7, 2.2), S(16.5, 2.2)]
    relleno(msp, pts, (255, 255, 255))
    poli(msp, pts, "CONTORNO", cerrada=True)
    tn(msp, "envasadora", S(16.6, 3.3), 1.8, "BOTTOM_CENTER")


# ---------------------------------------------------------------- tablas
def tablas(msp):
    x = 211.8
    subtitulo(msp, "CAPACIDADES", x, 180.4, 2.6)
    filas = [["Concepto", "Valor"],
             ["Producto seco por turno", "2.635 kg"],
             ["Rechazo de zaranda (≈ 2,5 %)", "66 kg/día → big bag"],
             ["Bolsas de 25 kg (60 %)", "62 bolsas/día · 21 min"],
             ["Bolsas chicas 1-2-5 kg (15 %)", "204 bolsas/día · 14 min"],
             ["A granel (25 %)", "acopio 8 → camión (circuito B)"],
             ["Tolva pulmón", "1,5 m³ = 2,3 h de producción"],
             ["Zaranda (trommel)", "Ø0,9 × 3,0 m · malla 6 mm · 18 rpm · 1,5 t/h"]]
    tabla(msp, x, 179.2, [66, 81.6], filas, h_fila=3.36, altura=1.8)

    subtitulo(msp, "EQUIPOS Y MOTORES (tablero TS-ENS)", x, 146.6, 2.6)
    filas = [["Tag", "Equipo", "kW", "Arranque"],
             ["M18", "Zaranda rotativa (trommel)", "1,10", "VFD"],
             ["M19", "Alimentador de la ensacadora 25 kg", "0,75", "VFD"],
             ["M20", "Cosedora de bolsas", "0,37", "directo"],
             ["M21", "Cinta de salida de bolsas", "0,55", "directo"],
             ["M22", "Envasadora vertical de bolsas chicas", "2,20", "propio"],
             ["M24", "Transportador flexible a la envasadora", "0,55", "directo"],
             ["M35", "Actuador de la válvula desviadora del elevador", "0,12", "directo"]]
    tabla(msp, x, 145.4, [11.7, 107.9, 12, 16], filas, h_fila=3.36, altura=1.8, alin=["L", "L", "R", "C"])

    subtitulo(msp, "BOLSAS PARA VENTA (viveros y locales de plantas)", x, 113.2, 2.6)
    filas = [["Formato", "Bolsa", "Rótulo (SENASA)"],
             ["25 kg", "rafia laminada 50 × 80 cm, cosida", "nombre, N-P-K y MO, humedad ≤ 15 %"],
             ["5 kg", "PE impreso con fuelle y asa", "peso neto, lote, fecha, N° de registro"],
             ["1 y 2 kg", "PE impreso, cierre zip", "modo de uso para viveros y macetas"]]
    tabla(msp, x, 112.0, [17.8, 59.8, 70], filas, h_fila=3.36, altura=1.8)


def main():
    global msp_
    revs = [("D", "09/2026", "Emisión original: separador de cáscara y plumas, ensacadora 25 kg y bolsitas")]
    doc, msp, z = lamina(19, "ZARANDA Y ENVASADO\n(25 kg Y BOLSAS CHICAS)", "1:50 / 1:100", revs)
    msp_ = msp
    planta(msp)
    corte(msp)
    tablas(msp)
    exportar_lamina(doc, 19)


if __name__ == "__main__":
    main()
