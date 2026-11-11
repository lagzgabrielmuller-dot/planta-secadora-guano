"""P13 - Implantación general ampliada (predio Rev. C + Sector Este Rev. D), esc. 1:500.

Geometría en metros de fuente/datos/layout_planta.json (clave G) y de las piezas Rev. D de
visor.html (__revDBuild: E1-E9, D7, hidrantes). Origen en el vértice SO de la nave.
"""
import json
import os


from lamina_secadora import (COL, escala_grafica, exportar_lamina, factor, globo,
                             lamina, linea, norte, notas, poli, relleno, relleno_circulo,
                             relleno_rect, circulo, subtitulo, t, tabla, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

ESC = "1:500"
k = factor(ESC)            # mm reales -> mm de papel
KM = k * 1000.0            # m reales -> mm de papel (2 mm/m)
OX, OY = 71.9, 183.2       # posición en el papel del origen (vértice SO de la nave)

# colores (RGB) tomados del original
VERDE = (232, 241, 224)
PAV_C = (217, 217, 217)    # pavimento Rev. C
PLAYON = (206, 206, 206)
PAV_D = (208, 216, 228)    # pavimento nuevo Rev. D
VEREDA = (230, 226, 220)
CALLE = (190, 191, 193)
ARBOL = (208, 228, 196)
ARBOL_L = (70, 120, 60)
BEIGE = (240, 230, 214)
ROSADO = (240, 222, 214)
CELESTE = (226, 232, 240)
TOSTADO = (214, 186, 150)
CREMA = (255, 243, 214)
ORO = (212, 167, 0)
ORO_TXT = (150, 115, 0)
ROJO = COL["incendio"]
NARANJA = COL["recirc"]
BIOGAS_Z = (255, 248, 222)


def P(x, y):
    return (OX + x * KM, OY + y * KM)


def R(x0, y0, x1, y1):
    return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]


def caja(msp, x0, y0, x1, y1, fill=None, capa="CONTORNO", color=None, lw=None, tipo=None):
    if fill:
        relleno(msp, R(x0, y0, x1, y1), fill)
    return poli(msp, R(x0, y0, x1, y1), capa, True, color, lw, tipo)


def disco(msp, x, y, r, fill=None, capa="CONTORNO", color=None, lw=None):
    if fill:
        relleno_circulo(msp, P(x, y), r * KM, fill)
    return circulo(msp, P(x, y), r * KM, capa, color, lw)


def trazo(msp, pts, color=None, lw=None, tipo=None, capa="CONTORNO", ltscale=None):
    e = poli(msp, [P(*p) for p in pts], capa, False, color, lw, tipo)
    if ltscale:
        e.dxf.ltscale = ltscale
    return e


def relleno_con_hueco(msp, ext, huecos, color):
    h = msp.add_hatch(dxfattribs={"layer": "RELLENO"})
    h.rgb = color
    h.paths.add_polyline_path([P(*p) for p in ext], is_closed=True, flags=1)
    for hu in huecos:
        h.paths.add_polyline_path([P(*p) for p in hu], is_closed=True, flags=16)
    return h


def arbol(msp, x, y, r=1.5):
    disco(msp, x, y, r, ARBOL, "FINO", ARBOL_L)
    relleno_circulo(msp, P(x, y), 0.18, ARBOL_L)


def hidrante(msp, x, y, tag, lado=1, etiqueta="arriba"):
    c = P(x, y)
    relleno_circulo(msp, c, 2.1, (255, 255, 255))
    circulo(msp, c, 2.1, "CONTORNO", ROJO, lw=50)
    relleno_circulo(msp, c, 1.0, ROJO)
    linea(msp, (c[0] + 2.1 * lado, c[1]), (c[0] + 3.4 * lado, c[1]), "CONTORNO", ROJO)
    if etiqueta == "izq":
        tn(msp, tag, (c[0] - 2.6, c[1] + 2.0), 1.6, "BOTTOM_RIGHT", color=ROJO)
    else:
        tn(msp, tag, (c[0], c[1] + 2.8), 1.6, "BOTTOM_CENTER", color=ROJO)


def cota_p(msp, p1, p2, distancia, valor=None, h=1.9):
    """Cota con la medida real (dimlfac = 1/k) y texto de 1,9 mm."""
    dim = msp.add_aligned_dim(p1=p1, p2=p2, distance=distancia, dimstyle="IRAM", text=valor or "<>",
                              override={"dimlfac": 1.0 / k, "dimtxt": h, "dimasz": 2.0},
                              dxfattribs={"layer": "COTAS"})
    dim.render()
    return dim


def ajustar_titulo_rotulo(msp, titulo, ancho=124.0):
    """El rótulo estima el ancho de la letra en 0,68 h; Arial negrita mayúscula ocupa ~0,83 h."""
    for e in msp.query('TEXT[layer=="ROTULO"]'):
        if e.dxf.text == titulo:
            e.dxf.height = min(e.dxf.height, ancho / (0.83 * len(titulo)))


def gl(msp, txt, xy, a=None, r=2.6, revd=False):
    """Globo en coordenadas reales (m)."""
    globo(msp, txt, P(*xy), P(*a) if a else None, radio=r,
          relleno_rgb=CREMA if revd else (255, 255, 255))


def muro_con_vanos(msp, a, b, vanos, eje):
    """Muro recto de a a b (m) con vanos [(s0, s1)] medidos sobre el eje 'x' o 'y'."""
    i = 0 if eje == "x" else 1
    s, fin = a[i], b[i]
    for v0, v1 in sorted(vanos) + [(fin, fin)]:
        p0, p1 = list(a), list(a)
        p0[i], p1[i] = s, v0
        if v0 > s:
            linea(msp, P(*p0), P(*p1), "CONTORNO", lw=100)
        s = v1


def main():
    revs = [("D", "09/2026", "Emisión original: predio 120 × 76 m, Sector Este (expedición y biogás), "
                             "limpieza de vehículos, accesos")]
    doc, msp, z = lamina(13, "IMPLANTACIÓN GENERAL AMPLIADA - REV. D", ESC, revs)
    ajustar_titulo_rotulo(msp, "IMPLANTACIÓN GENERAL AMPLIADA - REV. D")
    tit = "IMPLANTACIÓN GENERAL AMPLIADA (PREDIO + SECTOR ESTE) - ESC. 1:500"
    tn(msp, tit, (26, 278), 3.2, "BOTTOM_LEFT")
    largo = 0.79 * 3.2 * len(tit)
    linea(msp, (26, 277.0), (26 + largo, 277.0), "CONTORNO")
    linea(msp, (26, 276.2), (26 + largo, 276.2), "FINO")

    pr = dict(G["predio"])
    pr["x1"] = 98.0                       # Rev. D: el predio pasa a 120 × 76 m (__revDSetup)
    cx0, cx1 = -23.0, 99.5                # calle pública recortada al dibujo
    calle = G["calle"]

    # ---------------- fondo: calle pública, vereda, predio
    relleno_rect(msp, *P(cx0, calle["y0"]), *P(cx1, calle["y1"]), CALLE)
    relleno_rect(msp, *P(cx0, calle["y1"]), *P(cx1, pr["y0"]), VEREDA)
    yc = (calle["y0"] + calle["y1"]) / 2
    e = linea(msp, P(cx0 + 1, yc), P(cx1 - 0.5, yc), "FINO", (255, 255, 255), lw=35)
    e.dxf.linetype = "DASHED"
    e.dxf.ltscale = 8
    linea(msp, P(cx0, calle["y0"]), P(cx1, calle["y0"]), "FINO", (150, 150, 150))
    tn(msp, "CALLE PÚBLICA DE ACCESO (lote propuesto junto al Parque Industrial - ver plano 14)",
       (P(0, 0)[0] - 40, P(0, -44.2)[1]), 2.0, "MIDDLE_LEFT")
    relleno_rect(msp, *P(pr["x0"], pr["y0"]), *P(pr["x1"], pr["y1"]), VERDE)

    # ---------------- pavimentos Rev. C (calles R1-R5, sobreanchos) y playones
    for pv in G["pavimento"]:
        relleno_con_hueco(msp, pv["ext"], pv.get("holes", []), PAV_C)
    relleno(msp, [P(*p) for p in G["entrada_vehicular"]], PAV_C)
    for pl in G["playones"]:
        relleno_rect(msp, *P(pl["x0"], pl["y0"]), *P(pl["x1"], pl["y1"]), PLAYON)
    es = G["estacionamiento"]
    caja(msp, es["x0"], es["y0"], es["x1"], es["y1"], (210, 210, 210), "FINO")

    # ---------------- pavimentos nuevos Rev. D (E9: R6, R7, playón biogás, R8)
    for x0, y0, x1, y1 in ((44, -9, 96, -2), (84, -2, 92, 22), (84, 16, 96, 22), (86, -36, 92, -9),
                           (86, -39, 92, -36)):
        relleno_rect(msp, *P(x0, y0), *P(x1, y1), PAV_D)

    # ---------------- cortina forestal (Rev. C + Sector Este)
    arboles = [(a[0], a[1]) for a in G["arboles"]]
    y = -31.0
    while y <= 36.0:
        if not (10 < y < 26):
            arboles.append((97.0, y))
        y += 5.5
    x = 52.0
    while x <= 92.0:
        arboles.append((x, 39.0))
        x += 5.5
    for a in arboles:
        arbol(msp, *a)

    # ---------------- zona de biogás (ATEX) E8
    caja(msp, 60, 16, 96, 38, BIOGAS_Z, "FINO", ORO, lw=50, tipo="DASHED").dxf.ltscale = 6
    t(msp, "ZONA DE BIOGÁS (ATEX)", P(77.0, 35.6), 1.6, "MIDDLE_CENTER", estilo="NEGRITA", fondo=True)
    for xb in (68.0, 78.5):                                    # BD-1 y BD-2 Ø6,5 m
        e = circulo(msp, P(xb, 31), 6.25 * KM, "FINO", ORO)
        e.dxf.linetype = "DOT"
        e.dxf.ltscale = 3
        disco(msp, xb, 31, 3.25, (204, 222, 216), lw=70)
    disco(msp, 89, 33, 4.0, (214, 232, 200), lw=70)           # E8.3 tanque de digestato Ø8 m
    caja(msp, 83.2, 25.6, 86.0, 27.4, None, "FINO", tipo="DASHED")  # separador sobre plataforma
    caja(msp, 82, 22, 86, 25, (232, 226, 212), "CONTORNO")     # platea de sólidos
    disco(msp, 92.5, 25.5, 1.75, (225, 225, 225))             # tanque de mezcla
    caja(msp, 86, 17, 90, 20, (196, 176, 150))                 # fosa de guano excedente
    caja(msp, 62, 18, 68.1, 20.44, (200, 220, 205))            # cogeneración
    disco(msp, 70.6, 19.3, 0.5, (255, 255, 255), "FINO")       # desulfurador
    relleno_circulo(msp, P(95, 18.2), 0.9, (30, 30, 30))       # antorcha
    circulo(msp, P(95, 18.2), 0.9, "FINO")

    # línea de biogás enterrada E8.6 (cogeneración -> quemador piloto del hogar)
    ruta = [(71.3, 18.6), (71.3, 17.4), (61.5, 17.4), (61.5, 16.5), (35.5, 16.5), (35.5, 19.2), (29.1, 19.2)]
    trazo(msp, ruta, ORO, lw=70, tipo="DASHED", ltscale=6)
    t(msp, "línea de biogás PEAD Ø63 enterrada (mojones c/ 6 m)", P(36.3, 16.15), 1.5, "TOP_LEFT",
      color=ORO_TXT)

    # ---------------- E7 depósito de expedición 20 × 12 m
    caja(msp, 60, 0, 80, 12, (240, 222, 214), lw=100)
    relleno_rect(msp, *P(68, -1.2), *P(72, 0), COL["amarillo_seg"])
    t(msp, "DEPÓSITO DE EXPEDICIÓN\n20 × 12 m", P(70, 4.6), 1.9, "MIDDLE_CENTER", estilo="NEGRITA")

    # ---------------- Rev. C: anexo, equipos exteriores, E3, E2
    an = G["anexo"]
    caja(msp, an["x0"], an["y0"], an["x1"], an["y1"], ROSADO, lw=70)
    ic = an["intercambiador"]
    caja(msp, ic["x0"], ic["y0"], ic["x1"], ic["y1"], (225, 225, 225), "FINO")
    ho = an["hogar"]
    caja(msp, ho["x0"], ho["y0"], ho["x1"], ho["y1"], TOSTADO, "CONTORNO", (139, 90, 43))
    for v in an["ventiladores"]:
        disco(msp, v["x"], v["y"], 0.5, (255, 255, 255), "FINO")
    disco(msp, an["ciclon_humos"]["x"], an["ciclon_humos"]["y"], 0.4, (255, 255, 255), "FINO")
    caja(msp, an["cenizas"]["x"] - 0.5, an["cenizas"]["y"] - 0.5, an["cenizas"]["x"] + 0.5,
         an["cenizas"]["y"] + 0.5, (255, 255, 255), "FINO")
    ch = an["chimenea"]
    relleno_circulo(msp, P(ch["x"], ch["y"]), ch["D"] / 2 * KM, (40, 40, 40))
    si = G["silo"]
    disco(msp, si["x"], si["y"], si["D"] / 2, (255, 255, 255), lw=70)
    disco(msp, G["ciclon"]["x"], G["ciclon"]["y"], G["ciclon"]["D"] / 2, (255, 255, 255))
    disco(msp, G["scrubber"]["x"], G["scrubber"]["y"], G["scrubber"]["D"] / 2, (255, 255, 255))
    ts = G["tanque_sol"]
    disco(msp, ts["x"], ts["y"], ts["D"] / 2, (205, 222, 240), "FINO")
    ex = G["extractor"]
    disco(msp, ex["x"], ex["y"], 0.5, (255, 255, 255), "FINO")
    disco(msp, ex["chim_x"], ex["chim_y"], ex["chim_D"] / 2, (150, 150, 150), "FINO")
    # D7 recirculación de aire (ciclón -> cámara de mezcla del anexo)
    caja(msp, 19.55, 18.65, 20.25, 20.55, TOSTADO, "FINO")
    trazo(msp, [(15.2, 22.1), (19.9, 22.1), (19.9, 20.55)], NARANJA, lw=100)
    # E3 biofiltro y E2 lavadero
    caja(msp, 0.5, 20.2, 9.0, 24.7, (196, 160, 120))
    caja(msp, -0.85, 19.3, -0.35, 20.7, COL["azul"], "FINO")
    # tanque de incendio 27 y casilla de bomba
    caja(msp, G["casilla_bomba"]["x"] - 0.8, G["casilla_bomba"]["y"] - 0.6,
         G["casilla_bomba"]["x"] + 0.8, G["casilla_bomba"]["y"] + 0.6, None, "FINO", ROJO)

    # ---------------- nave de proceso 33 × 18 m
    nv = G["nave"]
    for zo in G["zonas"]:
        col = {1: BEIGE, 8: BEIGE, 28: CELESTE}[zo["n"]]
        relleno_rect(msp, *P(zo["x0"], zo["y0"]), *P(zo["x1"], zo["y1"]), col)
    for lo in G["locales"]:
        caja(msp, lo["x0"], lo["y0"], lo["x1"], lo["y1"], (255, 255, 255), "CONTORNO")
    mc = G["muro_contencion"]
    linea(msp, P(mc["x"], mc["y0"]), P(mc["x"], mc["y1"]), "CONTORNO", lw=70)
    for m in G["muros_acopio"]:
        linea(msp, P(m["x0"], m["y0"]), P(m["x1"], m["y1"]), "CONTORNO", lw=70)
    pg = G["pila_guano"]
    disco(msp, pg["x"], pg["y"], pg["r"], TOSTADO, "FINO")
    caja(msp, 4.4, 12.6, 9.2, 16.9, None, "FINO", tipo="DASHED")      # E3 campana
    tv = G["tolva"]
    caja(msp, tv["x0"], tv["y0"], tv["x1"], tv["y1"], TOSTADO, "FINO")
    ci = G["cinta"]
    caja(msp, tv["x1"], ci["y"] - ci["B"] / 2, ci["x_cabeza"], ci["y"] + ci["B"] / 2, (238, 232, 220), "FINO")
    se = G["secador"]
    caja(msp, se["x0"], se["y0"], se["x0"] + se["L"], se["y0"] + se["A"], (242, 242, 242), lw=70)
    caja(msp, se["x0"] + 0.3, se["y0"] + 0.3, se["x0"] + se["L"] - 0.3, se["y0"] + se["A"] - 0.3, None,
         "FINO", tipo="DASHED")
    sd = G["sinfin_desc"]
    linea(msp, P(sd["x0"], sd["y"]), P(sd["x1"], sd["y"]), "FINO")
    el = G["elevador"]
    caja(msp, el["x"] - el["ax"] / 2, el["y"] - el["ay"] / 2, el["x"] + el["ax"] / 2, el["y"] + el["ay"] / 2,
         (190, 190, 190), "FINO")
    ps = G["pila_seca"]
    disco(msp, ps["x"], ps["y"], ps["r"], TOSTADO, "FINO")
    # E4-E6 (zona 28): plataforma, trommel, cinta de bolsas y envasadora
    caja(msp, 26.6, 10.2, 29.4, 14.2, None, "FINO", tipo="DASHED")
    caja(msp, 27.6, 10.6, 28.4, 13.6, (235, 235, 235), "FINO")
    caja(msp, 28.4, 11.4, 31.0, 12.1, (250, 250, 250), "FINO")
    caja(msp, 29.0, 16.0, 30.2, 17.2, (215, 220, 225), "FINO")
    # ductos de aire agotado (17) y caliente (12)
    dg = G["ducto_agotado"]
    r2 = dg["D"] / 2
    caja(msp, 14.5 - r2, 9.3, 14.5 + r2, 20.2, (200, 230, 210), "FINO", COL["aire_agotado"])
    dc = G["ducto_caliente"]
    caja(msp, dc["x0"], 11.2, dc["x1"], nv["A"], (248, 205, 205), "FINO", COL["aire_caliente"])
    # muros con vanos (portones P1, P2, P3; puertas PP1, SE1, SE2)
    L, A = nv["L"], nv["A"]
    muro_con_vanos(msp, (0, 0), (L, 0), [(19, 20), (28, 32)], "x")
    muro_con_vanos(msp, (0, A), (L, A), [], "x")
    muro_con_vanos(msp, (0, 0), (0, A), [(2, 3.2), (12.6, 16.6)], "y")
    muro_con_vanos(msp, (L, 0), (L, A), [(12.4, 14.9), (15, 16.2)], "y")
    t(msp, "NAVE DE PROCESO 33 × 18 m", P(10.0, 13.7), 1.6, "MIDDLE_LEFT", estilo="NEGRITA", fondo=True)

    # ---------------- E1 vado + arco sobre la báscula, báscula 30, garita 31, pilar
    ba = G["bascula"]
    caja(msp, ba["x0"], ba["y0"], ba["x1"], ba["y1"], (150, 166, 166))
    caja(msp, 4.1, -16.9, 7.5, -12.2, (166, 212, 196))
    linea(msp, P(3.75, -14.6), P(7.85, -14.6), "CONTORNO", COL["salida"], lw=100)
    caja(msp, -2.6, -17.3, -0.6, -15.3, (255, 255, 255), "FINO")     # tanque desinfectante + M17
    ga = G["garita"]
    caja(msp, ga["x0"], ga["y0"], ga["x1"], ga["y1"], (255, 255, 255))
    pa = G["pilar_acometida"]
    caja(msp, pa["x"] - 0.6, pa["y"] - 0.6, pa["x"] + 0.6, pa["y"] + 0.6, (80, 80, 80), "FINO")

    # ---------------- cerco perimetral h 2,0 m (portón de 10 m y portón R8 de emergencia)
    pc = G["porton_predio"]
    cerco = [[(pc["x0"], pr["y0"]), (pr["x0"], pr["y0"]), (pr["x0"], pr["y1"]), (pr["x1"], pr["y1"]),
              (pr["x1"], pr["y0"]), (92, pr["y0"])], [(86, pr["y0"]), (pc["x1"], pr["y0"])]]
    for c in cerco:
        trazo(msp, c, None, lw=50, tipo="DASHED", ltscale=8)

    # ---------------- textos de calles e hidrantes
    tn(msp, "R6 - calle de vinculación y playón de expedición", P(73.3, -5.5), 1.8, "MIDDLE_CENTER")
    tn(msp, "R7", P(88, 7.5), 1.8, "MIDDLE_CENTER", rotacion=90)
    tn(msp, "R8", P(88.8, -21.0), 1.8, "MIDDLE_CENTER", rotacion=90)
    t(msp, "separación entre sectores S1-S4", P(46.7, 6.5), 1.6, "MIDDLE_CENTER")
    for (x, y), tag in zip(((-1.3, 4.6), (12.0, 19.2), (35.6, 9.5), (82.0, 14.0)), ("HI-1", "HI-2", "HI-3", "HI-4")):
        hidrante(msp, x, y, tag, etiqueta="izq" if tag == "HI-2" else "arriba")

    # ---------------- referencias (globos)
    gl(msp, "1", (4.6, 15.4))
    gl(msp, "4", (18.0, 9.3))
    gl(msp, "8", (30.5, 3.4))
    gl(msp, "9", (26.8, 21.3))
    gl(msp, "13", (si["x"], si["y"]))
    gl(msp, "18", (G["ciclon"]["x"], G["ciclon"]["y"]))
    gl(msp, "19", (G["scrubber"]["x"], G["scrubber"]["y"]))
    gl(msp, "22", (24.2, 2.5))
    tq = G["tanque_incendio"]
    disco(msp, tq["x"], tq["y"], tq["D"] / 2, (255, 255, 255), "CONTORNO", ROJO, lw=50)
    tn(msp, "27", P(tq["x"], tq["y"]), 2.3, "MIDDLE_CENTER")
    gl(msp, "30", (5.75, -24.0))
    gl(msp, "31", ((ga["x0"] + ga["x1"]) / 2, (ga["y0"] + ga["y1"]) / 2))
    gl(msp, "E1", (10.6, -18.6), (7.85, -14.6), revd=True)
    gl(msp, "E2", (-5.0, 22.0), (-0.6, 20.0), revd=True)
    gl(msp, "E3", (5.0, 27.3), (4.75, 22.45), revd=True)
    gl(msp, "E4", (30.4, 12.9), (28.0, 11.0), revd=True)
    gl(msp, "D19", (12.0, 27.2), r=2.8, revd=True)
    gl(msp, "D7", (19.6, 27.3), (19.9, 22.1), revd=True)
    gl(msp, "E7", (70.0, 9.0), r=2.8, revd=True)
    gl(msp, "E8.1", (91.4, 12.8), (88.0, 18.5), r=3.0, revd=True)
    gl(msp, "E8.2", (73.25, 25.9), (73.25, 31.0), r=3.0, revd=True)
    gl(msp, "E8.3", (89.0, 33.0), r=3.0, revd=True)
    gl(msp, "E8.4", (64.6, 23.3), (65.05, 19.2), r=3.0, revd=True)
    gl(msp, "E8.5", (95.6, 12.0), (95.0, 17.3), r=3.0, revd=True)
    gl(msp, "E8.6", (40.0, 20.6), (35.5, 18.0), r=3.0, revd=True)
    gl(msp, "E9", (89.0, -26.0), r=2.8, revd=True)

    # ---------------- cotas (mm reales)
    cota_p(msp, P(pr["x0"], pr["y1"]), P(pr["x1"], pr["y1"]), 7.8)
    cota_p(msp, P(pr["x0"], pr["y1"]), P(50, pr["y1"]), 3.4, "<> (predio Rev. C)")
    cota_p(msp, P(50, pr["y1"]), P(pr["x1"], pr["y1"]), 3.4, "<> (ampliación Rev. D)")
    cota_p(msp, P(pr["x1"], pr["y0"]), P(pr["x1"], pr["y1"]), -4.5)
    # anexo: cara exterior del muro Este (x = 28,5 + 0,2) a la envolvente de BD-1 (68 - 3,25)
    cota_p(msp, P(28.7, 26.3), P(64.75, 26.3), 0.0, "<> hogar → BD-1")
    cota_p(msp, P(nv["L"], 1.8), P(60, 1.8), 0.0)

    # ---------------- escala gráfica, norte, leyenda
    escala_grafica(msp, 27.9, 81.6, ESC, 50, 10)
    norte(msp, 128.0, 69.0, 6.0)
    subtitulo(msp, "LEYENDA", 140.0, 86.6, 2.5)
    ley = [("línea de biogás enterrada", ORO, "DASHED", 70),
           ("recirculación de aire (D7)", NARANJA, None, 70),
           ("cerco perimetral h 2,0 m", (0, 0, 0), "DASHED", 50),
           ("zona clasificada (ATEX) r = 3 m", ORO, "DOT", 50),
           ("pavimento nuevo Rev. D", None, None, None)]
    yy = 83.8
    for txt, col, tipo, lw in ley:
        if col is None:
            relleno_rect(msp, 140, yy - 1.2, 148, yy + 1.2, PAV_D)
        else:
            e = linea(msp, (140, yy), (148, yy), "CONTORNO", col, lw=lw)
            if tipo:
                e.dxf.linetype = tipo
                e.dxf.ltscale = 4 if tipo == "DASHED" else 3
        t(msp, txt, (150.0, yy), 1.9, "MIDDLE_LEFT")
        yy -= 3.4
    relleno_circulo(msp, (198.6, 83.8), 2.1, (255, 255, 255))
    circulo(msp, (198.6, 83.8), 2.1, "CONTORNO", ROJO, lw=50)
    relleno_circulo(msp, (198.6, 83.8), 1.0, ROJO)
    linea(msp, (200.7, 83.8), (202.0, 83.8), "CONTORNO", ROJO)
    t(msp, "hidrante", (203.0, 83.8), 1.9, "MIDDLE_LEFT")
    relleno_circulo(msp, (198.6, 80.4), 1.5, ARBOL)
    circulo(msp, (198.6, 80.4), 1.5, "FINO", ARBOL_L)
    t(msp, "cortina forestal", (203.0, 80.4), 1.9, "MIDDLE_LEFT")

    # ---------------- notas
    notas(msp, [
        "1. El predio Rev. C (72 × 76 m) no se modifica: se amplía 48 m hacia el Este (Sector Este).",
        "2. Nuevos sectores de incendio independientes: S4 depósito y S5 biogás (ver planos 15 y 16).",
        "3. Biodigestores a más de 36 m del hogar; antorcha a más de 12 m de los gasómetros; círculo punteado = zona clasificada (3 m).",
        "4. El vado sanitario lleva desinfectante: su efluente NO va al biodigestor (se retira como residuo).",
        "5. Coordenadas en m con origen en el vértice Sudoeste de la nave (igual que los planos 01, 08 y 11).",
    ], 26.0, 58.0, altura=1.9, interlineado=1.5, titulo=None)
    subtitulo(msp, "NOTAS", 26.0, 60.8, 2.5)

    # ---------------- panel derecho
    X = 280.0
    subtitulo(msp, "REFERENCIAS (Rev. C, ver planos 01 y 11)", X, 266.5, 2.5)
    notas(msp, ["1 Playa de recepción · 4 Secador de cinta · 8 Acopio",
                "9 Hogar · 13 Silo de cáscara · 18 Ciclón · 19 Lavador",
                "22 Sala de control (TGF) · 27 Tanque de incendio 20 m³",
                "30 Báscula 40 t · 31 Garita · calles R1 a R5"], X, 264.2, altura=1.85, interlineado=1.4)
    subtitulo(msp, "AGREGADOS REV. D", X, 247.6, 2.5)
    agregados = [
        ("E1", "Limpieza y desinfección de vehículos (vado + arco)"),
        ("E2", "Lavadero de camiones en playón P1"),
        ("E3", "Campana de recepción, extractor y biofiltro"),
        ("E4-E6", "Zaranda, ensacadora 25 kg y bolsas chicas (zona 28)"),
        ("E7", "Depósito de expedición (sector de incendio S4)"),
        ("E8.1", "Fosa de guano excedente y tanque de mezcla"),
        ("E8.2", "Biodigestores BD-1 y BD-2 Ø6,5 m (silos de biogás)"),
        ("E8.3", "Tanque de digestato Ø8 m y separador"),
        ("E8.4", "Cogeneración 25 kWe y tratamiento del gas"),
        ("E8.5", "Antorcha de seguridad"),
        ("E8.6", "Línea de biogás al quemador piloto"),
        ("E9", "Calles R6, R7, R8, portón de emergencia"),
        ("D7", "Recirculación de aire (ver plano 18)"),
        ("HI-1..4", "Hidrantes con gabinete (ver plano 15)"),
        ("P3", "Portón nuevo 2,5 m en muro Este (pallets)"),
    ]
    yy = 244.3
    for cod, desc in agregados:
        tn(msp, cod, (X, yy), 1.85, "MIDDLE_LEFT")
        t(msp, desc, (293.0, yy), 1.85, "MIDDLE_LEFT")
        yy -= 3.3

    subtitulo(msp, "CUADRO DE SUPERFICIES", X, 189.8, 2.5)
    sup = [["Destino", "m²", "%"],
           ["Nave de proceso (33,0 × 18,0)", "594", "6,5"],
           ["Anexo del generador", "52", "0,6"],
           ["Depósito de expedición", "240", "2,6"],
           ["Sala de cogeneración y garita", "27", "0,3"],
           ["Biodigestores, digestato y mezcla", "126", "1,4"],
           ["Biofiltro", "38", "0,4"],
           ["Calles, playones y báscula", "2.748", "30,1"],
           ["Verde y cortina forestal", "5.295", "58,1"],
           ["PREDIO (120 × 76 m)", "9.120", "100,0"]]
    tabla(msp, X, 188.0, [74, 26, 26], sup, h_fila=3.3, altura=1.85, alin=["L", "R", "R"],
          negrita_ultima=True, sombras={9: (240, 240, 240)})

    subtitulo(msp, "CIRCUITOS DE VEHÍCULOS", X, 150.0, 2.5)
    cir = [["Circuito", "Recorrido"],
           ["A guano húmedo", "pesa · calles Sur y Oeste · P1 · lavadero · vado · sale"],
           ["B producto a granel", "pesa · calle Sur · P2 · pesa · sale"],
           ["C cáscara de arroz", "pesa · calle Este · dársena PL3 · silo"],
           ["D producto embolsado", "pesa · R6 · dársena del depósito · pesa"],
           ["E guano excedente", "pesa · R6 · R7 · fosa de biogás"],
           ["F bomberos", "portón de emergencia · R8 · R6 / R7 (sin báscula)"]]
    tabla(msp, X, 148.0, [36, 90], cir, h_fila=3.3, altura=1.85)

    exportar_lamina(doc, 13)


if __name__ == "__main__":
    main()
