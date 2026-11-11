"""P04 - Generador de aire caliente a cáscara de arroz: cortes D-D y E-E (1:50), planta del anexo (1:100).

Geometría: fuente/datos/layout_planta.json -> G.anexo (hogar, intercambiador, ventiladores, ciclón de humos,
chimenea, cenizas), G.silo, G.ducto_caliente. Coordenadas del proyecto: x al Este, y al Norte (m).
"""
import json
import math
import os


from lamina_secadora import (fuente_pil, COL, FECHA, arco, circulo, exportar_lamina, factor, flecha, lamina, linea,
                             poli, rayado, rect, relleno, relleno_circulo, relleno_rect, subtitulo, suelo, t,
                             tabla, tn)
from lamina_a3 import cota

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
AN = G["anexo"]

K50, K100 = factor("1:50"), factor("1:100")
M50, M100 = K50 * 1000, K100 * 1000          # mm de papel por metro

ROJO, AZUL, GRIS = COL["aire_caliente"], COL["aire_frio"], COL["humos"]
LADRILLO = COL["ladrillo"]
MURO = (205, 195, 175)
E_MURO = 0.2                                  # espesor de muros del anexo (m)

# ---------------------------------------------------------------- helpers propios de la lámina
def ancho_texto(texto, h, negrita=True):
    return fuente_pil(negrita).getlength(texto) / 1000.0 * h / 0.716


def titulo(msp, texto, x, y, h=3.5):
    tn(msp, texto, (x, y), h, "BOTTOM_LEFT")
    largo = ancho_texto(texto, h)
    linea(msp, (x, y - 1.0), (x + largo, y - 1.0), "CONTORNO")
    linea(msp, (x, y - 1.8), (x + largo, y - 1.8), "FINO")


def globo2(msp, etiqueta, centro, apunta_a=None, radio=3.2, relleno_rgb=(255, 255, 255)):
    h = min(radio * 0.95, 1.55 * radio / max(ancho_texto(etiqueta, 1.0), 0.1))
    if relleno_rgb:
        relleno_circulo(msp, centro, radio, relleno_rgb)
    circulo(msp, centro, radio, "COTAS", lw=50)
    tn(msp, etiqueta, centro, h, "MIDDLE_CENTER", capa="COTAS")
    if apunta_a:
        dx, dy = apunta_a[0] - centro[0], apunta_a[1] - centro[1]
        d = math.hypot(dx, dy)
        if d > radio:
            linea(msp, (centro[0] + dx / d * radio, centro[1] + dy / d * radio), apunta_a, "COTAS", lw=35)
            p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
            p.paths.add_edge_path().add_arc(apunta_a, 0.6, 0, 360)


def caja(msp, x0, y0, x1, y1, capa="CONTORNO", fill=None, color=None, lw=None):
    if fill:
        relleno_rect(msp, x0, y0, x1, y1, fill)
    return rect(msp, x0, y0, x1, y1, capa, color, lw)


def muro_rayado(msp, x0, y0, x1, y1, fill=MURO, escala=0.25):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    relleno(msp, pts, fill)
    rayado(msp, pts, escala=escala)
    rect(msp, x0, y0, x1, y1, "CONTORNO")


def corte_break(msp, x0, x1, y):
    """Línea de corte (rotura) con zigzag en el medio, para cortar la chimenea."""
    xm = (x0 + x1) / 2
    poli(msp, [(x0 - 0.8, y), (xm - 1.2, y), (xm - 0.4, y + 1.3), (xm + 0.4, y - 1.3), (xm + 1.2, y), (x1 + 0.8, y)],
         "FINO")


# ---------------------------------------------------------------- A - corte D-D (mirando al Norte), 1:50
X0D, Z0 = 35.1, 164.1


def D(x, z):
    return (X0D + (x - AN["x0"]) * M50, Z0 + z * M50)


def corte_dd(msp):
    h = AN["h"]
    ho, ic, ch = AN["hogar"], AN["intercambiador"], AN["chimenea"]
    suelo(msp, 24.8, 225.0, Z0)
    # muros O y E cortados, losa de techo
    muro_rayado(msp, *D(AN["x0"] - E_MURO, 0), *D(AN["x0"], h))
    muro_rayado(msp, *D(AN["x1"], 0), *D(AN["x1"] + E_MURO, h))
    caja(msp, *D(AN["x0"] - E_MURO, h), *D(AN["x1"] + E_MURO, h + 0.18), "CONTORNO", fill=(125, 125, 125))

    # chimenea (atraviesa la losa) con línea de rotura
    cx0, cx1 = ch["x"] - ch["D"] / 2, ch["x"] + ch["D"] / 2
    rect(msp, *D(cx0, 0.3), *D(cx1, h), "CONTORNO")
    rect(msp, *D(cx0, h + 0.18), *D(cx1, 5.55), "CONTORNO")
    corte_break(msp, D(cx0, 0)[0], D(cx1, 0)[0], D(0, 5.55)[1])
    flecha(msp, D(ch["x"], 4.95), D(ch["x"], 5.5), color=GRIS, tam=1.5, lw=35)
    t(msp, "15 chimenea Ø500 (h = 12,0 m)", (64.1, 273.8), 2.0)

    # ciclón de humos (detrás), caja O y carcasa del intercambiador
    caja(msp, 38.9, 199.9, 55.2, 220.2, "CONTORNO", lw=50)
    poli(msp, [(38.9, 199.9), (44.9, 183.9), (49.2, 183.9), (55.2, 199.9)], "CONTORNO", lw=50)
    caja(msp, 40.0, 189.7, 44.9, 196.6, "CONTORNO")
    flecha(msp, (48.3, 193.2), (40.9, 193.2), color=GRIS, tam=1.4, lw=35)
    caja(msp, *D(21.0, ic["z0"]), *D(ic["xts"][0], ic["z1"]), "CONTORNO", lw=50)
    caja(msp, *D(ic["xts"][0], 0.7), *D(ic["xts"][1], 3.1), "CONTORNO", lw=50)
    # tubos (6 filas, dibujados como líneas) y pasos de humos
    for zc in (2.50, 2.30, 2.05, 1.85, 1.60, 1.40):
        for s in (-1, 1):
            linea(msp, D(ic["xts"][0], zc + s * ic["D"] / 2), D(ic["xts"][1], zc + s * ic["D"] / 2), "CONTORNO", lw=50)
    for zb in (ic["z0"], ic["z1"]):
        linea(msp, D(ic["xts"][0], zb), D(ic["xts"][1], zb), "CONTORNO", lw=50)
    for txt, x, z in (("PASO 1", 61.2, 2.40), ("PASO 2", 113.1, 1.95), ("PASO 3", 61.2, 1.50)):
        tn(msp, txt, (x, D(0, z)[1]), 1.9, "MIDDLE_LEFT", fondo=True)
    for x_a, x_b, z in ((100.1, 81.7, 2.40), (81.7, 100.1, 1.95), (100.1, 81.7, 1.50)):
        flecha(msp, (x_a, D(0, z)[1]), (x_b, D(0, z)[1]), color=GRIS, tam=1.6, lw=50)
    # caja E (sup. e inf.) entre el haz y el hogar
    caja(msp, *D(ic["xts"][1] + 0.03, ic["z0"]), *D(ho["x0"], ic["z1"]), "CONTORNO", lw=50)
    linea(msp, D(ic["xts"][1] + 0.03, 2.18), D(ho["x0"], 2.18), "CONTORNO", lw=50)
    # aire de proceso: entra frío abajo (azul) y sale caliente arriba (rojo)
    for x in (61.0, 77.0, 93.1, 109.0, 125.0):
        flecha(msp, (x, 179.4), (x, 185.4), color=AZUL, tam=1.4, lw=50)
        flecha(msp, (x, 188.6), (x, 191.1), color=AZUL, tam=1.2, lw=50)
        flecha(msp, (x, 198.4), (x, 200.5), color=AZUL, tam=1.2, lw=50)
        flecha(msp, (x, 207.2), (x, 209.9), color=ROJO, tam=1.2, lw=50)
        flecha(msp, (x, 216.4), (x, 223.3), color=ROJO, tam=1.4, lw=50)
    t(msp, "aire 18 °C desde ventiladores (11)", (91.0, 175.0), 2.0, "MIDDLE_CENTER")
    t(msp, "plenum 135 °C", (100.0, 227.6), 1.9, "BOTTOM_LEFT")
    # ducto caliente 12 (sección, sale hacia el Sur)
    dc = G["ducto_caliente"]
    a, b = D(dc["x0"], 3.1), D(dc["x1"], 3.8)
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", color=ROJO, lw=50)
    linea(msp, a, b, "CONTORNO", color=ROJO, lw=50)
    linea(msp, (a[0], b[1]), (b[0], a[1]), "CONTORNO", color=ROJO, lw=50)
    t(msp, "12 al secador (hacia el Sur)", (89.1, 243.8), 2.0)
    globo2(msp, "10", (83.0, 224.0), apunta_a=(91.1, 209.9))

    # hogar: ladrillo refractario 230 + aislante 70
    o = [D(ho["x0"], 0), D(ho["x1"], ho["z1"])]
    i = [D(ho["ix0"], ho["iz0"]), D(ho["ix1"], ho["iz1"])]
    anillo = [(o[0][0], o[0][1]), (o[1][0], o[0][1]), (o[1][0], o[1][1]), (o[0][0], o[1][1])]
    relleno(msp, anillo, LADRILLO)
    rayado(msp, anillo, escala=0.5)
    caja(msp, i[0][0], i[0][1], i[1][0], i[1][1], "CONTORNO", fill=(255, 255, 255), lw=50)
    rect(msp, o[0][0], o[0][1], o[1][0], o[1][1], "CONTORNO", lw=70)
    rect(msp, *D(ho["x0"] + 0.23, 0.23), *D(ho["x1"] - 0.23, ho["z1"] - 0.23), "CONTORNO", lw=50)
    # boca hacia la caja E sup.
    caja(msp, 137.0, 208.1, 143.2, 216.3, "CONTORNO", fill=(255, 255, 255))
    flecha(msp, (145.3, 212.4), (133.1, 212.4), color=GRIS, tam=1.4, lw=50)
    # parrilla escalonada, cenicero y M13
    xs = [146.6, 152.0, 157.4, 162.8, 168.2, 173.6, 178.9]
    ys = [182.1, 184.6, 187.2, 189.7, 192.2, 194.7]
    pts = [(xs[0], 179.6), (xs[0], ys[0])]
    for k in range(6):
        pts += [(xs[k + 1], ys[k])] + ([(xs[k + 1], ys[k + 1])] if k < 5 else [])
    poli(msp, pts, "CONTORNO", color=(70, 70, 70), lw=70)
    linea(msp, (i[0][0], 176.5), (i[1][0], 176.5), "CONTORNO", lw=50)
    circulo(msp, (151.0, 173.0), 1.6, "CONTORNO", lw=50)
    t(msp, "M13", (156.0, 173.0), 1.8)
    for x in (161.1, 171.0):
        flecha(msp, (x, 170.7), (x, 178.1), color=AZUL, tam=1.4, lw=50)
    t(msp, "parrilla 0,6 m²", (152.4, 182.3), 1.9, "BOTTOM_LEFT", fondo=True)
    tn(msp, "900-1000 °C", (161.0, 204.0), 2.2, "MIDDLE_CENTER")
    t(msp, "aire secundario", (176.9, 211.7), 1.9, "MIDDLE_RIGHT")
    for y in (207.0, 203.0):
        flecha(msp, (184.3, y), (177.8, y), color=AZUL, tam=1.4, lw=50)
    globo2(msp, "9", (151.0, 227.0), apunta_a=(144.6, 220.0))
    # sinfín de cáscara 14 desde el silo (con rotura) y conducto de aire secundario
    caja(msp, 185.0, 192.9, 189.4, 199.8, "CONTORNO", fill=(255, 255, 255), lw=50)
    circulo(msp, (187.2, 196.6), 2.0, "CONTORNO", lw=50)
    linea(msp, (187.2, 197.3), (226.2, 187.9), "CONTORNO", lw=50)
    linea(msp, (187.2, 193.7), (222.6, 185.0), "CONTORNO", lw=50)
    poli(msp, [(225.0, 190.0), (225.8, 188.4), (229.0, 187.6), (223.0, 186.3), (222.6, 183.8)], "FINO")
    t(msp, "desde silo (13)", (219.8, 182.3), 1.9, "MIDDLE_CENTER")
    poli(msp, [(185.0, 206.1), (193.0, 206.1), (193.0, Z0)], "CONTORNO")
    poli(msp, [(185.0, 205.4), (192.3, 205.4), (192.3, Z0)], "CONTORNO")
    globo2(msp, "14", (192.6, 216.7), apunta_a=(187.4, 199.6))

    # cotas
    cota(msp, (27.5, Z0), (27.5, D(0, h)[1]), distancia=0, escala=K50)
    linea(msp, (26.0, D(0, h)[1]), D(AN["x0"] - E_MURO, h), "FINO")
    cota(msp, D(21.0, 0), D(ho["x0"], 0), distancia=-6.1, escala=K50)
    cota(msp, D(ho["x0"], 0), D(ho["x1"], 0), distancia=-6.1, escala=K50)
    dim = msp.add_aligned_dim(p1=(206.0, Z0), p2=(206.0, D(0, ho["z1"])[1]), distance=0, dimstyle="IRAM",
                              override={"dimlfac": 1.0 / K50, "dimtmove": 2}, dxfattribs={"layer": "COTAS"})
    dim.set_location((204.6, 207.5), leader=False)
    dim.render()
    linea(msp, (190.1, D(0, ho["z1"])[1]), (207.5, D(0, ho["z1"])[1]), "FINO")


# ---------------------------------------------------------------- B - corte E-E (mirando al Oeste), 1:50
X0E = 243.0


def E(y, z):
    """El Sur (nave) queda a la izquierda."""
    return (X0E + (y - AN["y0"]) * M50, Z0 + z * M50)


def corte_ee(msp):
    h = AN["h"]
    ic = AN["intercambiador"]
    suelo(msp, 234.8, 381.4, Z0)
    muro_rayado(msp, *E(AN["y0"] - E_MURO, 0), *E(AN["y0"], h))
    muro_rayado(msp, *E(AN["y1"], 0), *E(AN["y1"] + E_MURO, h))
    caja(msp, *E(AN["y0"] - E_MURO, h), *E(AN["y1"] + E_MURO, h + 0.18), "CONTORNO", fill=(125, 125, 125))
    t(msp, "muro cortafuego RF-120", (239.0, 268.2), 2.0)
    # intercambiador: plenum superior 400, haz 1600 en 3 pasos, plenum inferior
    y0, y1 = ic["y0"], ic["y1"]
    caja(msp, *E(y0, 0.7), *E(y1, 3.1), "CONTORNO", lw=50)
    for z in (ic["z1"], ic["z0"]):
        linea(msp, E(y0, z), E(y1, z), "CONTORNO", lw=50)
    for z in (2.18, 1.74):
        linea(msp, E(y0, z), E(y1, z), "CONTORNO", lw=50)
    paso = 0.1153
    for zc in (2.50, 2.30, 2.05, 1.85, 1.60, 1.40):
        for n in range(ic["por_fila"]):
            circulo(msp, E(y0 + 0.07 + n * paso, zc), ic["D"] / 2 * M50, "CONTORNO", lw=50)
    for txt, z in (("P1", 2.40), ("P2", 1.96), ("P3", 1.51)):
        tn(msp, txt, (334.8, E(0, z)[1]), 1.9, "MIDDLE_LEFT")
    for x in (295.0, 309.0, 323.0):
        flecha(msp, (x, 216.4), (x, 223.2), color=ROJO, tam=1.4, lw=50)
        flecha(msp, (x, 187.8), (x, 190.8), color=AZUL, tam=1.2, lw=50)
    cota(msp, (344.5, E(0, ic["z1"])[1]), (344.5, E(0, 3.1)[1]), distancia=0, escala=K50)
    cota(msp, (344.5, E(0, ic["z0"])[1]), (344.5, E(0, ic["z1"])[1]), distancia=0, escala=K50)
    for z in (3.1, ic["z1"], ic["z0"]):
        linea(msp, (340.0, E(0, z)[1]), (346.0, E(0, z)[1]), "FINO")
    cota(msp, E(y0, 0.7), E(y1, 0.7), distancia=-5.0, escala=K50)
    t(msp, "114 tubos Ø63,5 x 3 - 6 filas x 19", (300.1, 159.4), 2.0)
    t(msp, "paso 116 mm (1,83 D) - 3 pasos de 38 tubos", (300.1, 156.4), 2.0)
    # ventilador 11 de aire de proceso
    v = AN["ventiladores"][0]
    c = E(v["y"], 0.755)
    relleno_circulo(msp, c, 12.4, (255, 255, 255))
    circulo(msp, c, 12.4, "CONTORNO", lw=50)
    circulo(msp, c, 5.1, "CONTORNO", lw=50)
    tn(msp, "11", c, 2.2, "MIDDLE_CENTER")
    rect(msp, 255.0, Z0, 277.1, 166.6, "CONTORNO", lw=50)
    linea(msp, (273.0, 183.2), (287.0, 183.2), "CONTORNO", lw=50)
    linea(msp, (277.1, 178.6), (287.0, 178.6), "CONTORNO", lw=50)
    flecha(msp, (279.8, 181.0), (294.3, 181.0), color=AZUL, tam=1.4, lw=50)
    # ducto caliente: subida y tramo horizontal a la nave con compuerta cortafuego
    rect(msp, 243.0, 228.1, 301.0, 240.1, "CONTORNO", color=ROJO, lw=50)
    rect(msp, 301.0, 226.2, 313.0, 240.1, "CONTORNO", color=ROJO, lw=50)
    flecha(msp, (307.0, 228.1), (307.0, 236.6), color=ROJO, tam=1.4, lw=50)
    flecha(msp, (297.3, 234.2), (250.8, 234.2), color=ROJO, tam=1.4, lw=50)
    caja(msp, 238.1, 227.0, 244.1, 241.2, "CONTORNO", fill=(255, 255, 255), lw=50)
    linea(msp, (243.6, 240.4), (238.6, 227.6), "CONTORNO")
    t(msp, "compuerta cortafuego", (245.1, 246.2), 2.0)
    t(msp, "a la nave", (233.5, 234.2), 2.0, "MIDDLE_RIGHT")


# ---------------------------------------------------------------- C - planta del anexo, 1:100
X0P, Y0P = 37.1, 80.0


def PL(x, y):
    return (X0P + (x - AN["x0"]) * M100, Y0P + (y - AN["y0"]) * M100)


def muro_planta(msp, a, b):
    pts = [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])]
    relleno(msp, pts, (255, 255, 255))
    rayado(msp, pts, escala=0.12)
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=50)


def planta(msp):
    ho, ic, cz = AN["hogar"], AN["intercambiador"], AN["ciclon_humos"]
    x0, x1, y0, y1 = AN["x0"], AN["x1"], AN["y0"], AN["y1"]
    e = E_MURO
    # muros: N con acceso de 2 hojas (24,0-25,2); S = muro RF-120 de la nave con puerta RF-60 (26,2-27,2)
    muro_planta(msp, PL(x0 - e, y1), PL(24.0, y1 + e))
    muro_planta(msp, PL(25.2, y1), PL(x1 + e, y1 + e))
    muro_planta(msp, PL(x0 - e, y0), PL(x0, y1))
    muro_planta(msp, PL(x1, y0), PL(x1 + e, y1))
    muro_planta(msp, PL(19.77, y0 - e), PL(26.2, y0))
    muro_planta(msp, PL(27.2, y0 - e), PL(29.0, y0))
    # puertas
    for xh, a0, a1 in ((24.0, 0, 90), (25.2, 90, 180)):
        c = PL(xh, y1 + e)
        linea(msp, c, (c[0], c[1] + 6.0), "CONTORNO")
        arco(msp, c, 6.0, a0, a1, "FINO")
    t(msp, "acceso 2 hojas 1,2 m", (PL(24.6, 0)[0], 141.6), 1.8, "MIDDLE_CENTER")
    c = PL(26.2, y0 - e)
    linea(msp, c, (c[0], c[1] - 10.0), "CONTORNO")
    arco(msp, c, 10.0, 270, 360, "FINO")
    t(msp, "RF-60", (108.3, 72.5), 1.8, "MIDDLE_LEFT")
    t(msp, "muro cortafuego RF-120", (66.3, 72.3), 1.8, "MIDDLE_LEFT")
    # toma de aire (cámara de mezcla) en el muro O
    rect(msp, 33.9, 87.9, 37.7, 104.2, "CONTORNO", lw=50)
    t(msp, "toma de\naire", (39.1, 96.0), 1.8, "MIDDLE_LEFT")
    # equipos
    circulo(msp, PL(cz["x"], cz["y"]), cz["D"] / 2 * M100, "CONTORNO", lw=50)
    a, b = PL(ic["x0"], ic["y0"]), PL(ic["x1"], ic["y1"])
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=50)
    tn(msp, "10", (PL(23.3, 0)[0], PL(0, 21.3)[1]), 2.2, "MIDDLE_CENTER")
    a, b = PL(ho["x0"], ho["y0"]), PL(ho["x1"], ho["y1"])
    ai, bi = PL(ho["ix0"], ho["iy0"]), PL(ho["ix1"], ho["iy1"])
    h = msp.add_hatch(dxfattribs={"layer": "RAYADO"})
    h.set_pattern_fill("ANSI31", scale=0.25)
    h.paths.add_polyline_path([a, (b[0], a[1]), b, (a[0], b[1])], is_closed=True, flags=1)
    h.paths.add_polyline_path([ai, (bi[0], ai[1]), bi, (ai[0], bi[1])], is_closed=True, flags=16)
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=70)
    rect(msp, ai[0], ai[1], bi[0], bi[1], "FINO")
    tn(msp, "9", (PL(26.8, 0)[0], PL(0, 21.3)[1]), 2.2, "MIDDLE_CENTER")
    for v in AN["ventiladores"]:
        c = PL(v["x"], v["y"])
        rect(msp, c[0] - 3.0, c[1] + 5.2, c[0] + 3.0, PL(0, ic["y0"])[1], "CONTORNO", lw=50)
        relleno_circulo(msp, c, 6.25, (255, 255, 255))
        circulo(msp, c, 6.25, "CONTORNO", lw=50)
    tn(msp, "11", (67.9, 91.5), 2.0, "MIDDLE_CENTER")
    # ducto caliente (en altura) y pase por el muro RF-120
    dc = G["ducto_caliente"]
    rect(msp, *PL(dc["x0"], 18.2), *PL(dc["x1"], 21.0), "CONTORNO")
    caja(msp, 50.0, 80.0, 64.2, 81.7, "CONTORNO", lw=70)
    # ventilador de combustión y cenizas (16)
    vc, cn = AN["vent_comb"], AN["cenizas"]
    a, b = PL(cn["x"] - 0.5, cn["y"] - 0.5), PL(cn["x"] + 0.5, cn["y"] + 0.5)
    rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=50)
    circulo(msp, PL(vc["x"], vc["y"]), 3.6, "CONTORNO", lw=50)
    tn(msp, "16", PL(cn["x"], cn["y"]), 2.0, "MIDDLE_CENTER")
    t(msp, "vent. 4 kW", (93.5, 134.0), 1.8, "MIDDLE_RIGHT")
    # chimenea
    circulo(msp, PL(AN["chimenea"]["x"], AN["chimenea"]["y"]), 2.5, "CONTORNO", lw=50)
    # silo 13 y sinfín 14
    si = G["silo"]
    c = PL(si["x"], si["y"])
    circulo(msp, c, si["D"] / 2 * M100, "CONTORNO", lw=50)
    tn(msp, "13", c, 2.2, "MIDDLE_CENTER")
    for yy in (112.25, 113.9):
        linea(msp, (PL(ho["x1"], 0)[0], yy), (c[0] - si["D"] / 2 * M100, yy), "CONTORNO")
    tn(msp, "14", (122.1, 117.5), 1.9, "MIDDLE_CENTER")
    # líneas de corte D-D (y = 21,3) y E-E (x = 23,3)
    yd = PL(0, 21.3)[1]
    for xa, xb, xf in ((27.75, 34.3, 31.0), (160.4, 166.3, 163.1)):
        linea(msp, (xa, yd), (xb, yd), "CONTORNO", lw=70)
        flecha(msp, (xf, yd), (xf, yd + 5.5), "CONTORNO", tam=1.8, lw=50)
        tn(msp, "D", (xf, yd + 7.0), 3.6, "BOTTOM_CENTER")
    xe = PL(23.3, 0)[0]
    for ya, yb, yt in ((145.0, 151.3, 147.9), (73.0, 80.0, 75.4)):
        linea(msp, (xe, ya), (xe, yb), "CONTORNO", lw=70)
        flecha(msp, (xe, yt), (xe - 6.0, yt), "CONTORNO", tam=1.8, lw=50)
        tn(msp, "E", (xe - 7.0, yt), 3.6, "MIDDLE_RIGHT")
    # cotas
    cota(msp, (25.8, PL(0, y0)[1]), (25.8, PL(0, y1 + e)[1]), distancia=0, escala=K100)
    linea(msp, (24.5, PL(0, y1 + e)[1]), (34.0, PL(0, y1 + e)[1]), "FINO")
    linea(msp, (24.5, PL(0, y0)[1]), (29.5, PL(0, y0)[1]), "FINO")
    cota(msp, PL(x0 - e, y0), PL(x1 + e, y0), distancia=-13.75, escala=K100)


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Anexo cortafuego; tubos como líneas; humos 3 pasos (salida O); contracorriente"),
            ("C", "09/2026", "Planta C: puerta RF-60 a la nave en muro RF-120 (x 26,2-27,2, como el plano 01)"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    for r in revs:
        assert len(r[2]) <= 80, (len(r[2]), r[2])
    doc, msp, z = lamina(4, "GENERADOR DE AIRE CALIENTE\nA CÁSCARA DE ARROZ", "1:50 / 1:100", revs)
    titulo(msp, "A - CORTE D-D (mirando al Norte)  -  ESC. 1:50", 25, 279.5, 3.6)
    corte_dd(msp)
    titulo(msp, "B - CORTE E-E (mirando al Oeste)  -  ESC. 1:50", 230.2, 279.5, 3.6)
    corte_ee(msp)
    titulo(msp, "C - PLANTA DEL ANEXO  -  ESC. 1:100", 100.2, 152.0, 3.6)
    planta(msp)
    # datos del generador
    subtitulo(msp, "DATOS DEL GENERADOR", 232, 148.0, 2.8)
    tabla(msp, 232, 146.0, [72, 101], [
        ["Magnitud", "Valor"],
        ["Potencia útil al aire", "882 kW"],
        ["Combustible", "cáscara de arroz, PCI 13,5 MJ/kg"],
        ["Consumo / cenizas (18 %)", "314 kg/h / 56 kg/h"],
        ["Rendimiento hogar + intercambiador", "75 %"],
        ["Aire de combustión (exceso 40 %)", "2.020 kg/h - ventilador 4 kW"],
        ["Humos", "2.280 kg/h; 850 °C -> 200 °C"],
        ["Aire de proceso", "26.600 kg/h a.s.; 18 -> 135 °C"],
        ["Intercambiador", "114 tubos Ø63,5 x 4 m; 91 m²"],
        ["LMTD / U", "390 K / 25 W/m²K (contracorriente)"],
        ["Tubos paso 1 / pasos 2-3", "AISI 310 / ASTM A106"],
        ["Refractario", "ladrillo aluminoso 230 + aislante 70"],
        ["Seguridades", "TT-06 (950 °C), BE-01, by-pass, RF-120"],
    ], h_fila=4.75, altura=2.1, sombras={i: (246, 247, 248) for i in range(2, 13, 2)})
    # notas
    subtitulo(msp, "NOTAS", 25, 55.0, 2.8)
    for k, r in enumerate([
        "1. Humos por dentro de los tubos: hogar -> caja E (sup.) -> paso 1 -> caja O -> paso 2 -> caja E (inf.) -> "
        "paso 3 -> caja O (inf.) -> ciclón -> chimenea.",
        "2. Aire por la carcasa de abajo hacia arriba: entra frío por el paso 3 y sale caliente por el paso 1 "
        "(contracorriente, como supone el cálculo).",
        "3. El producto nunca toca los humos (intercambio indirecto).",
        "4. Tapas de las cajas abulonadas para deshollinar los tubos (semanal).",
    ]):
        t(msp, r, (25, 52.4 - k * 3.6), 2.0, "MIDDLE_LEFT")
    exportar_lamina(doc, 4)


if __name__ == "__main__":
    main()
