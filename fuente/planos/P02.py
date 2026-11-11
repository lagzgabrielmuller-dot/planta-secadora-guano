"""P02 - Secador de cinta: corte longitudinal B-B y planta (1:50), lista de partes 4.x y datos.

Redibujo vectorial de la lámina P02 Rev. C (PNG). Geometría del secador tomada de
fuente/datos/layout_planta.json (G.secador, G.cinta, G.elevador, G.sinfin_desc), en metros,
con coordenadas locales del secador: x desde el extremo Oeste, y desde la cara Sur, z desde el piso.
"""
import json
import math
import os

from lamina_secadora import (COL, FECHA, arco, circulo, exportar_lamina, factor, flecha, globo,
                             lamina, linea, nivel, poli, rect, relleno, relleno_rect,
                             subtitulo, suelo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
S = G["secador"]
CI = G["cinta"]
EL = G["elevador"]
SF = G["sinfin_desc"]

k = factor("1:50")          # mm reales -> mm de papel
KM = k * 1000.0             # metros -> mm de papel
X0 = 52.0                   # x = 0 del secador (extremo Oeste) en las dos vistas
Z0 = 189.0                  # nivel ±0,00 del corte
Y0 = 101.0                  # cara Sur del secador en la planta

GRIS = (150, 150, 150)
OSC = (60, 60, 60)
GUANO = COL["guano"]
CAL = COL["aire_caliente"]
AGO = COL["aire_agotado"]


def X(x):
    return X0 + x * KM


def Z(z):
    return Z0 + z * KM


def Y(y):
    return Y0 + y * KM


def P(x, z):
    return (X(x), Z(z))


def Q(x, y):
    return (X(x), Y(y))


def cotap(msp, p1, p2, dist, valor=None, txt=2.5, asz=2.5):
    """Cota alineada con medida real a 1:50 y tamaño de texto/flecha ajustable."""
    ov = {"dimlfac": 1.0 / k, "dimtxt": txt, "dimasz": asz}
    d = msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, dimstyle="IRAM", text=valor or "<>",
                            override=ov, dxfattribs={"layer": "COTAS"})
    d.render()
    return d


def rotura(msp, x, y, h=3.0, vertical=True):
    """Símbolo de rotura (rayo) sobre una línea."""
    if vertical:
        poli(msp, [(x - 0.5, y - h / 2), (x + 0.6, y + 0.4), (x - 0.6, y - 0.4), (x + 0.5, y + h / 2)], "CONTORNO")
    else:
        poli(msp, [(x - h / 2, y - 0.5), (x - 0.4, y + 0.6), (x + 0.4, y - 0.6), (x + h / 2, y + 0.5)], "CONTORNO")


def eje_cruz(msp, c, r):
    linea(msp, (c[0] - r, c[1]), (c[0] + r, c[1]), "EJES")
    linea(msp, (c[0], c[1] - r), (c[0], c[1] + r), "EJES")


def panel(msp, x0, z0, x1, z1):
    """Panel sándwich en corte (gris lleno con contorno)."""
    pts = [P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)]
    relleno(msp, pts, GRIS)
    poli(msp, pts, "CONTORNO", cerrada=True)


# ====================================================================== corte B-B

def corte(msp):
    titulo_vista(msp, "CORTE LONGITUDINAL B-B (mirando al Norte)  -  ESC. 1:50", 150, 279.5, 3.6)
    L, H, e, hp = S["L"], S["H"], S["panel"], S["h_patas"]

    suelo(msp, 30, 357, Z0)

    # ---- estructura bajo el piso de la cámara (4.11)
    linea(msp, P(0, 0.28), P(L, 0.28), "CONTORNO")
    for xc in S["columnas_x"]:
        for dx in (-0.05, 0.05):
            linea(msp, P(xc + dx, 0), P(xc + dx, hp), "CONTORNO")
        relleno_rect(msp, X(xc - 0.16), Z(0), X(xc + 0.16), Z(0.03), OSC)
    # columnas interiores (líneas de estructura dentro de la cámara)
    for xc in S["columnas_x"][1:-1]:
        linea(msp, P(xc, hp + e), P(xc, H - e), "CONTORNO")

    # ---- envolvente de paneles 4.8 (aberturas: alimentación, campana, descarga)
    dx0, dx1 = S["descarga_x"]
    panel(msp, 0, hp, dx0, hp + e)                      # piso de la cámara
    panel(msp, dx1, hp, L, hp + e)
    panel(msp, 0, hp, e, H)                             # pared Oeste
    panel(msp, L - e, hp, L, H)                         # pared Este
    cx = S["campana_x"]
    panel(msp, 0, H - e, 0.7, H)                        # techo
    panel(msp, 1.1, H - e, cx - 0.4, H)
    panel(msp, cx + 0.4, H - e, L, H)
    # descarga del piso 3 hacia el sinfín
    linea(msp, P(dx0, hp), P(dx0, 0.35))
    linea(msp, P(dx1, hp), P(dx1, 0.35))

    # ---- campana de salida 4.12 (800 x 800) hacia el ciclón
    poli(msp, [P(cx - 0.4, H), P(cx - 0.4, 4.05), P(cx + 0.4, 4.05), P(cx + 0.4, H)])
    linea(msp, P(cx - 0.4, 3.72), P(cx + 0.4, 3.72), "FINO")
    rotura(msp, X(cx), Z(4.05), 3.4)
    linea(msp, P(cx, 3.3), P(cx, 4.25), "EJES")
    flecha(msp, P(cx, 3.15), P(cx, 3.95), "CONTORNO", AGO, tam=1.8)
    t(msp, "a ciclón (pl. 08)", (X(cx + 0.55), Z(4.0)), 2.0)
    globo(msp, "4.12", (X(3.95), Z(3.47)), (X(cx + 0.4), Z(3.55)))

    # ---- cinta de alimentación (ítem 3) llegando sobre el techo, a 30°
    ch = (CI["x_cabeza"] - S["x0"], CI["z_cabeza"] - CI["D_motriz"] / 2)   # centro del tambor motriz
    rm = CI["D_motriz"] / 2
    a = math.radians(CI["ang"])
    d = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))

    def pc(s, o):
        return P(ch[0] + s * d[0] + o * n[0], ch[1] + s * d[1] + o * n[1])

    s0 = -1.95
    for o in (0.30, rm, -rm, -0.30):
        linea(msp, pc(s0, o), pc(0, o), "CONTORNO" if abs(o) > 0.2 else "FINO")
    for i in range(1, 8):
        s = -i * CI["paso"]
        linea(msp, pc(s, rm), pc(s, rm + CI["h_taco"]), "FINO")
    poli(msp, [pc(s0, -0.36), pc(s0 - 0.05, -0.05), pc(s0 + 0.05, 0.05), pc(s0, 0.36)], "CONTORNO")
    circulo(msp, P(*ch), rm * KM)
    eje_cruz(msp, P(*ch), 0.32 * KM)
    # capota inox y bajada a la cámara
    poli(msp, [P(0.1, 3.82), P(0.1, 4.66), P(1.1, 4.66), P(1.06, 4.16)])
    linea(msp, P(0.76, 3.91), P(0.76, H))
    linea(msp, P(1.06, 4.16), P(1.06, H))
    t(msp, "capota inox", (X(0.08), Z(4.53)), 2.0, "MIDDLE_RIGHT")
    t(msp, "M8 lado Norte (0,75 kW)", (X(1.3), Z(4.53)), 2.0)
    globo(msp, "3", (39.0, 273.7), pc(-1.2, 0.30))
    flecha(msp, P(S["alimentacion_x"], 3.66), P(S["alimentacion_x"], 2.86), "CONTORNO", GUANO, tam=1.8)

    # ---- pisos: banda 4.1, tambores 4.2 / 4.3, rodillos 4.6, travesaños con guías 4.7
    radio = {}
    for p in S["pisos"]:
        zc = p["zc"]
        rcab, rcol = S["r_motriz"], S["r_reenvio"]
        tamb = {p["cabeza"]: rcab, p["cola"]: rcol}
        xa, xb = sorted(tamb)
        ra, rb = tamb[xa], tamb[xb]
        ca, cb = (xa, zc - ra), (xb, zc - rb)
        radio[p["n"]] = (ca, ra, cb, rb)
        # producto (guano) sobre la banda y banda
        linea(msp, P(xa, zc + 0.035), P(xb, zc + 0.035), "CONTORNO", GUANO)
        linea(msp, P(xa, zc), P(xb, zc), "CONTORNO")
        # ramal de retorno
        linea(msp, P(xa, ca[1] - ra), P(xb, cb[1] - rb), "CONTORNO")
        for c, r in ((ca, ra), (cb, rb)):
            circulo(msp, P(*c), r * KM)
            eje_cruz(msp, P(*c), (r + 0.2) * KM)
        # rodillos de retorno
        for xr in S["rodillos_retorno_x"]:
            zr = ca[1] - ra + (cb[1] - rb - (ca[1] - ra)) * (xr - xa) / (xb - xa)
            circulo(msp, P(xr, zr - 0.06), 0.0445 * KM)
        # travesaños L 50x50 c/1,0 m bajo la banda
        x = 1.05 if p["n"] != 3 else 0.8
        while x < xb - 0.2:
            rect(msp, X(x - 0.05), Z(zc - 0.13), X(x + 0.05), Z(zc - 0.03), "FINO")
            x += 1.0

    # tambor motriz con línea más gruesa (escalonados: el de cabeza es mayor)
    # tolvas de transferencia 4.10 y caída del producto
    linea(msp, P(12.9, 2.63), P(12.75, 1.93), "CONTORNO", lw=100)
    linea(msp, P(0.12, 1.79), P(0.26, 1.09), "CONTORNO", lw=100)
    flecha(msp, P(12.65, 2.42), P(12.65, 1.95), "CONTORNO", GUANO, tam=1.6)
    flecha(msp, P(0.375, 1.68), P(0.375, 1.03), "CONTORNO", GUANO, tam=1.6)
    flecha(msp, P(12.67, 0.83), P(12.67, 0.30), "CONTORNO", GUANO, tam=1.6)

    # esparcidor (5) y compuerta de altura de capa
    ce = (S["esparcidor_x"], 2.91)
    circulo(msp, P(*ce), 0.12 * KM)
    circulo(msp, P(*ce), 0.03 * KM)
    for i in range(6):
        ang = math.radians(30 + 60 * i)
        linea(msp, P(ce[0] + 0.03 * math.cos(ang), ce[1] + 0.03 * math.sin(ang)),
              P(ce[0] + 0.12 * math.cos(ang), ce[1] + 0.12 * math.sin(ang)), "FINO")
    linea(msp, P(S["compuerta_x"], H - e), P(S["compuerta_x"], 2.85), "CONTORNO", lw=70)

    # puertas de inspección 4.9 (700 x 600) y ventanas
    for pu in S["puertas"]:
        x, z0, z1 = pu["x"], pu["z0"], pu["z1"]
        rect(msp, X(x - 0.35), Z(z0), X(x + 0.35), Z(z1))
        rect(msp, X(x - 0.3), Z(z0 + 0.05), X(x + 0.3), Z(z1 - 0.05), "FINO")
    for v in S["ventanas"]:
        x, z0, z1 = v["x"], v["z0"], v["z1"]
        rect(msp, X(x - 0.15), Z(z0), X(x + 0.15), Z(z1))
        linea(msp, P(x - 0.15, z0), P(x + 0.15, z1), "FINO")

    # flujos de aire: caliente (rojo) sube entre pisos, agotado (verde) sale arriba
    xs_aire = [2.2, 5.2, 8.3, 11.2]
    for x in xs_aire:
        flecha(msp, P(x, 2.78), P(x, 3.12), "CONTORNO", AGO, tam=1.5)
        for z0, z1 in ((1.90, 2.22), (1.05, 1.37), (0.50, 0.70)):
            flecha(msp, P(x, z0), P(x, z1), "CONTORNO", CAL, tam=1.5)
    # entrada de aire 12 (ducto 1200 x 600, cara Norte)
    ea = S["entrada_aire"]
    pts = [P(ea["x0"], ea["z0"]), P(ea["x1"], ea["z0"]), P(ea["x1"], ea["z1"]), P(ea["x0"], ea["z1"])]
    poli(msp, pts, "CONTORNO", cerrada=True, color=CAL)
    for i in range(5):
        xa = ea["x0"] + 0.1 + i * 0.24
        linea(msp, P(xa, ea["z0"] + 0.02), P(xa + 0.16, ea["z1"] - 0.02), "FINO", CAL)
    flecha(msp, P(10.25, 0.65), P(7.0, 0.65), "CONTORNO", CAL, tam=1.8)
    flecha(msp, P(11.75, 0.65), P(12.35, 0.65), "CONTORNO", CAL, tam=1.6)
    t(msp, "aire 135 °C", (X(9.2), Z(0.70)), 1.9, "BOTTOM_CENTER")
    t(msp, "aire 65 °C", (X(5.2), Z(3.18)), 2.0, "BOTTOM_CENTER")
    cotap(msp, P(ea["x0"], 1.08), P(ea["x1"], 1.08), 0.0001, txt=2.3, asz=2.0)
    for xx in (ea["x0"], ea["x1"]):
        linea(msp, P(xx, ea["z1"] + 0.03), P(xx, 1.14), "COTAS")

    # rótulos de pisos con sentido de marcha
    for p in S["pisos"]:
        zc = p["zc"]
        relleno_rect(msp, X(6.5) - 5.5, Z(zc + 0.37) - 0.3, X(6.5) + 5.5, Z(zc + 0.37) + 2.8, (255, 255, 255))
        tn(msp, f"PISO {p['n']}", (X(6.5), Z(zc + 0.37)), 2.4, "BOTTOM_CENTER")
        if p["sentido"] > 0:
            flecha(msp, P(5.4, zc + 0.27), P(7.7, zc + 0.27), "CONTORNO", GUANO, tam=1.8)
        else:
            flecha(msp, P(7.7, zc + 0.27), P(5.4, zc + 0.27), "CONTORNO", GUANO, tam=1.8)

    # ---- sinfín de descarga (6) y elevador (7)
    xs0, xs1 = SF["x0"] - S["x0"], SF["x1"] - S["x0"] - 0.22
    ps = [P(xs0 - 0.1, 0.1), P(xs1, 0.1), P(xs1, 0.35), P(xs0 - 0.1, 0.35)]
    poli(msp, ps, "CONTORNO", cerrada=True)
    x = xs0
    while x < xs1 - 0.1:
        linea(msp, P(x, 0.12), P(x + 0.16, 0.33), "CONTORNO")
        x += 0.25
    xe = EL["x"] - S["x0"]
    rect(msp, X(xe - 0.34), Z(0), X(xe + 0.34), Z(0.76))
    poli(msp, [P(xe - 0.26, 0.76), P(xe - 0.26, 4.05), P(xe + 0.26, 4.05), P(xe + 0.26, 0.76)])
    linea(msp, P(xe - 0.31, 4.05), P(xe + 0.31, 4.05))
    for dx in (-0.16, 0.16):
        linea(msp, P(xe + dx, 0.76), P(xe + dx, 3.9), "FINO")
    rotura(msp, X(xe), Z(4.05), 3.4)
    rect(msp, X(xe + 0.34), Z(0.12), X(xe + 0.77), Z(0.35))
    t(msp, "M10", (X(xe + 0.555), Z(0.235)), 1.8, "MIDDLE_CENTER")

    # ---- cotas
    for (z0, z1) in ((hp, 1.0), (1.0, 1.85), (1.85, 2.7), (2.7, H)):
        cotap(msp, P(L, z0), P(L, z1), -(316 - X(L)))
    cotap(msp, P(L, 0), P(L, H), -(324.5 - X(L)))
    cotap(msp, P(0, 0), P(0, hp), (X(0) - 45))          # 400 (patas) del lado Oeste
    yb = Z0 - 5.4
    for xa, xb in ((0, 0.3), (0.3, 0.55), (12.45, 12.7), (12.7, 13.0)):
        cotap(msp, P(xa, 0), P(xb, 0), yb - Z0, txt=2.0, asz=1.4)
    cotap(msp, P(0.55, 0), P(12.45, 0), -8.8)
    cotap(msp, P(0, 0), P(L, 0), -13.0)

    # ---- niveles
    for z, txt in ((4.35, "+4,35"), (3.40, "+3,40"), (2.70, "+2,70"), (1.85, "+1,85"),
                   (1.00, "+1,00"), (0.40, "+0,40"), (0.0, "±0,00")):
        nivel(msp, 362, Z(z), txt)

    # ---- globos
    c1 = radio[1]
    globo(msp, "4.3", (55.2, 249.3), (X(c1[0][0] - 0.09), Z(c1[0][1] + 0.09)))
    globo(msp, "5", (88.0, 240.5), (X(ce[0] + 0.09), Z(ce[1] + 0.08)))
    globo(msp, "4.1", (110.0, 248.6), P(3.05, 2.7))
    globo(msp, "4.8", (232.9, 262.0), P(9.04, H))
    globo(msp, "4.9", (161.3, 239.0), P(5.2, 2.85))
    globo(msp, "4.6", (138.0, 230.0), P(4.5, 2.37))
    globo(msp, "4.2", (302.0, 252.0), (X(c1[2][0] + 0.11), Z(c1[2][1] + 0.11)))
    globo(msp, "4.10", (295.5, 230.2), P(12.84, 2.2))
    globo(msp, "7", (343.8, 239.2), P(xe, 2.5))
    globo(msp, "12", (255.8, 197.7), P(10.9, 0.62))
    globo(msp, "4.11", (190.9, 194.7), P(6.55, 0.33))
    globo(msp, "6", (318.0, 182.6), P(12.95, 0.2))


# ====================================================================== planta

def puerta_planta(msp, x, norte):
    """Puerta de inspección en planta: hoja a 45° y arco de giro."""
    yw = S["A"] if norte else 0.0
    sg = 1 if norte else -1
    r = 0.495
    hx = x - 0.35
    linea(msp, Q(hx, yw), Q(hx + r * 0.7071, yw + sg * r * 0.7071), "CONTORNO")
    if norte:
        arco(msp, Q(hx, yw), r * KM, 0, 45)
    else:
        arco(msp, Q(hx, yw), r * KM, -45, 0)


def apoyo_planta(msp, x0, x1, ya, yb, ejes):
    rect(msp, X(x0), Y(ya), X(x1), Y(yb), "CONTORNO")
    for xe in ejes:
        rect(msp, X(xe - 0.08), Y(ya), X(xe + 0.08), Y(yb), "FINO")


def planta(msp):
    titulo_vista(msp, "PLANTA (vista superior)  -  ESC. 1:50", 28, 170.3, 3.4)
    L, A, e = S["L"], S["A"], S["panel"]

    # pasarela 4.13 sobre el techo (lado Sur)
    pp = [Q(0.3, e), Q(12.7, e), Q(12.7, 0.88), Q(0.3, 0.88)]
    relleno(msp, pp, (232, 232, 232))
    hu = [(X(6.5) - 22, Y(0.48) - 2.0), (X(6.5) + 22, Y(0.48) - 2.0),
          (X(6.5) + 22, Y(0.48) + 2.0), (X(6.5) - 22, Y(0.48) + 2.0)]
    h = msp.add_hatch(dxfattribs={"layer": "FINO"})
    h.set_pattern_fill("ANSI37", scale=2.4, angle=0)
    h.paths.add_polyline_path(pp, is_closed=True, flags=1)
    h.paths.add_polyline_path(hu, is_closed=True, flags=16)
    poli(msp, pp, "CONTORNO", cerrada=True)
    t(msp, "4.13 pasarela 800 con baranda", (X(6.5), Y(0.48)), 2.0, "MIDDLE_CENTER")

    # envolvente
    rect(msp, X(0), Y(0), X(L), Y(A))
    rect(msp, X(e), Y(e), X(L - e), Y(A - e), "FINO")
    for xc in S["columnas_x"]:
        xc = min(max(xc, 0.12), L - 0.12)
        relleno_rect(msp, X(xc - 0.1), Y(0), X(xc + 0.1), Y(0.08), OSC)
        relleno_rect(msp, X(xc - 0.1), Y(A - 0.08), X(xc + 0.1), Y(A), OSC)
    tn(msp, "4  SECADOR - techo de paneles", (X(6.5), Y(1.75)), 2.5, "MIDDLE_CENTER")

    # puertas (una por piso y por lado) y su referencia
    for pu, nom in zip(S["puertas"], ("P1", "P2", "P3")):
        puerta_planta(msp, pu["x"], True)
        puerta_planta(msp, pu["x"], False)
        t(msp, nom, (X(pu["x"]), 88.5), 1.8, "MIDDLE_CENTER")

    # escalera marinera
    rect(msp, X(-0.54), Y(0.2), X(-0.04), Y(0.7))
    for i in range(1, 5):
        linea(msp, Q(-0.54, 0.2 + i * 0.1), Q(-0.04, 0.2 + i * 0.1), "FINO")
    t(msp, "escalera", (X(-0.62), Y(0.45)), 2.0, "MIDDLE_RIGHT")

    # cinta de alimentación (3) llegando desde el Oeste, capota y M8
    yc = S["yc"] - S["y0"]
    rect(msp, X(-1.05), Y(yc - 0.35), X(0.72), Y(yc + 0.35))
    linea(msp, Q(-1.05, yc - 0.24), Q(0.72, yc - 0.24), "FINO")
    linea(msp, Q(-1.05, yc + 0.24), Q(0.72, yc + 0.24), "FINO")
    linea(msp, Q(-1.05, yc - 0.45), Q(-1.05, yc + 0.45), "CONTORNO")
    x = -0.85
    while x < 0.6:
        linea(msp, Q(x, yc - 0.15), Q(x, yc + 0.15), "CONTORNO")
        x += 0.217
    rect(msp, X(0.1), Y(yc - 0.4), X(1.1), Y(yc + 0.4))
    rect(msp, X(0.36), Y(1.75), X(0.76), Y(2.3))
    t(msp, "M8", (X(0.56), Y(2.02)), 1.8, "MIDDLE_CENTER")

    # ejes de tambores y esparcidor, apoyos UCF y accionamientos
    for xe, y0, y1 in ((0.3, -0.2, 2.75), (0.55, -0.3, 2.75), (S["esparcidor_x"], -0.4, 2.7),
                       (12.45, -0.3, 2.75), (12.7, -0.2, 2.75)):
        linea(msp, Q(xe, y0), Q(xe, y1), "EJES")
    linea(msp, Q(-1.4, yc), Q(S["esparcidor_x"] - 0.02, yc), "EJES")
    apoyo_planta(msp, 0.05, 0.83, A + 0.03, A + 0.11, (0.3, 0.55))
    apoyo_planta(msp, 0.05, 0.83, -0.11, -0.03, (0.3, 0.55))
    apoyo_planta(msp, 12.17, 12.95, A + 0.03, A + 0.11, (12.45, 12.7))
    apoyo_planta(msp, 12.17, 12.95, -0.11, -0.03, (12.45, 12.7))
    # M6 (piso 2, motriz Oeste)
    rect(msp, X(0.33), Y(-0.25), X(0.79), Y(-0.11), lw=70)
    rect(msp, X(0.39), Y(-0.5), X(0.71), Y(-0.25))
    rect(msp, X(0.46), Y(-0.78), X(0.62), Y(-0.5))
    t(msp, "M6", (X(0.54), Y(-0.64)), 1.8, "MIDDLE_CENTER")
    # M5 y M7 (pisos 1 y 3, motrices Este)
    rect(msp, X(11.98), Y(-0.24), X(12.6), Y(-0.11), lw=70)
    for xm, nom in ((12.1, "M5"), (12.45, "M7")):
        rect(msp, X(xm - 0.16), Y(-0.5), X(xm + 0.16), Y(-0.24))
        rect(msp, X(xm - 0.08), Y(-0.78), X(xm + 0.08), Y(-0.5))
        t(msp, nom, (X(xm), Y(-0.64)), 1.8, "MIDDLE_CENTER")
    # M9 (esparcidor)
    rect(msp, X(1.21), Y(-0.41), X(1.49), Y(-0.06))
    t(msp, "M9", (X(1.35), Y(-0.24)), 1.8, "MIDDLE_CENTER")

    # campana 4.12 / conducto 17 Ø800 al ciclón
    cx = S["campana_x"]
    circulo(msp, Q(cx, yc), 0.4 * KM)
    linea(msp, Q(cx - 0.4, yc), Q(cx + 0.4, yc), "CONTORNO", AGO)
    for xx in (cx - 0.4, cx + 0.4):
        linea(msp, Q(xx, yc), Q(xx, 3.2), "CONTORNO", AGO)
    rotura(msp, X(cx), Y(3.2) - 0.5, 4.0)
    t(msp, "17  Ø800 (sube a +6,5)", (X(3.55), Y(1.98)), 2.0)

    # ducto de entrada de aire 12 (cara Norte) y corte C-C
    ea = S["entrada_aire"]
    pd = [Q(ea["x0"], A), Q(ea["x1"], A), Q(ea["x1"], A + 0.6), Q(ea["x0"], A + 0.6)]
    poli(msp, pd, "CONTORNO", cerrada=True, color=CAL)
    linea(msp, pd[0], pd[2], "FINO", CAL)
    linea(msp, pd[1], pd[3], "FINO", CAL)
    t(msp, "12 ducto 1200 x 600", (X(11.75), Y(2.88)), 2.0)
    xcc = X(11.0)
    for yy, ext in ((Y(A + 0.6) + 2.2, 1), (88.0, -1)):
        linea(msp, (xcc, yy - 2.0 * ext), (xcc, yy + 2.0 * ext), "CONTORNO", lw=70)
        flecha(msp, (xcc, yy), (xcc + 5.5, yy), "CONTORNO", tam=1.8)
        tn(msp, "C", (xcc + 7.0, yy), 4.0, "MIDDLE_LEFT")
    t(msp, "corte C-C: plano 09", (249.8, 172.6), 2.0)

    # sinfín de descarga (6) y elevador (7)
    xs0, xs1 = 12.4, EL["x"] - S["x0"] - EL["ax"] / 2 + 0.01
    rect(msp, X(xs0), Y(yc - 0.09), X(xs1), Y(yc + 0.09))
    xe = EL["x"] - S["x0"]
    rect(msp, X(xe - EL["ax"] / 2), Y(yc - EL["ay"] / 2), X(xe + EL["ax"] / 2), Y(yc + EL["ay"] / 2))
    linea(msp, Q(xe - EL["ax"] / 2, yc - EL["ay"] / 2), Q(xe + EL["ax"] / 2, yc + EL["ay"] / 2), "CONTORNO")
    rect(msp, X(xe + EL["ax"] / 2), Y(yc - 0.13), X(xe + EL["ax"] / 2 + 0.4), Y(yc + 0.12))
    tn(msp, "7", (X(xe) + 4.0, Y(yc + EL["ay"] / 2) + 4.8), 2.2, "MIDDLE_CENTER")

    # indicación de corte B-B (mirando al Norte)
    for xb, xl in ((25.6, 34.0), (344.0, 350.5)):
        linea(msp, (xb, Y(yc)), (xl, Y(yc)), "CONTORNO", lw=70)
        xm = 28.0 if xb < 100 else 347.0
        flecha(msp, (xm, Y(yc)), (xm, Y(yc) + 5.5), "CONTORNO", tam=1.8)
        tn(msp, "B", (xm + (2.6 if xb > 100 else 0), Y(yc) + 7.2), 4.5, "BOTTOM_CENTER")

    # ---- cotas
    yd = Y(A + 0.6) - Y(A)
    xs = [0, 0.9, 1.655, 3.0, 4.875, 8.125, 10.4]
    for xa, xb in zip(xs, xs[1:]):
        cotap(msp, Q(xa, A), Q(xb, A), yd, txt=2.3, asz=2.0)
    cotap(msp, Q(L, 0), Q(L, A), -(326 - X(L)))
    cotap(msp, Q(L, e), Q(L, 0.88), -(319 - X(L)), valor="800", txt=2.3, asz=2.0)
    cotap(msp, Q(0, 0), Q(L, 0), -(Y(0) - 82.5))


# ====================================================================== tablas

def tablas(msp):
    subtitulo(msp, "LISTA DE PARTES DEL SECADOR", 25, 72.6, 3.0)
    t(msp, "(la cinta de alimentación, 3.1 a 3.8, en el plano 12)", (98, 72.8), 2.0, "BOTTOM_LEFT")
    filas = [["N°", "Denominación", "Especificación"],
             ["4.1", "Banda de malla AISI 304", "Alambre trenzado Ø2 mm paso 5 mm, 2000 mm de ancho, cadenas laterales."],
             ["4.2", "Tambor motriz Ø300 × 2100", "Tubo 4 mm, discos 12 mm, goma romboidal 8 mm; eje SAE 1045 Ø60 (Ø50 en corona)."],
             ["4.3", "Tambor de reenvío Ø250 × 2100", "Con unidades tensoras UCT 210 a ambos lados (tensor M20)."],
             ["4.4", "Rodamiento con brida UCF 212", "Fuera de la cámara, sobre ménsula; sello de laberinto en el panel."],
             ["4.5", "Motorreductor 0,75 kW i = 1:300", "Doble sinfín-corona + cadena ASA 60 Z15/Z75; VFD a ≈ 20 Hz."],
             ["4.6", "Rodillo de retorno Ø89", "Cada 2,0 m en el ramal de retorno."],
             ["4.7", "Guías PTFE / UHMW-PE 40×20", "PTFE en pisos 2 y 3, UHMW-PE en el 1; faldón de sellado inox + labio de silicona."],
             ["4.8", "Panel sándwich 80 mm", "Lana de roca 100 kg/m³, cara interior inox 0,6 mm."],
             ["4.9", "Puerta de inspección 700 × 600", "Una por piso y por lado, cierre de leva y microinterruptor."],
             ["4.10", "Tolvas de transferencia", "Chapas deflectoras inox entre pisos (tambores escalonados)."],
             ["4.11", "Estructura UPN 120 / IPN 140", "Columnas c/3,25 m, placas base 200×200×12, brocas M16."],
             ["4.12", "Campana de salida 800 × 800", "En el techo, a 3,0 m del extremo Oeste."],
             ["4.13", "Pasarela superior con baranda", "Rejilla 0,8 m, baranda 1,0 m, escalera marinera."]]
    sombras = {i: (243, 245, 247) for i in range(2, len(filas), 2)}
    tabla(msp, 25, 70.7, [8.5, 40, 104], filas, h_fila=4.0, altura=1.8, alin=["C", "L", "L"], sombras=sombras)

    subtitulo(msp, "DATOS", 180, 72.6, 3.0)
    filas = [["Alimentación", "1.000 kg/h (72 %)"], ["Producto", "329 kg/h (15 %)"],
             ["Agua evap.", "671 kg/h"], ["Aire", "26.600 kg/h a.s."], ["Temperaturas", "100 (máx. 135) / 33 °C"],
             ["Superficie", "72 m² (3 pisos)"], ["Capa / carga", "30 mm / 24 kg/m²"],
             ["Velocidad", "0,37 m/min · VFD"], ["Residencia", "97 min"],
             ["T1 máx.", "4978 N (CS 1,6)"], ["Motores", "3 × 0,75 kW"], ["Transmisión", "1:300 + cad. 1:5"]]
    sombras = {i: (243, 245, 247) for i in range(1, len(filas), 2)}
    tabla(msp, 180, 70.7, [20, 28.5], filas, h_fila=4.0, altura=1.8, encabezado=False, sombras=sombras)


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Tambores escalonados, motriz en cabeza, aire lateral; B1: cinta c/tacos y capota"),
            ("C", "09/2026", "Partes solo del secador (4.x); las de la cinta (3.x) en plano 12; título planta"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24"),
            ("E", "11/2026", "Estudio térmico: guías PTFE en pisos 2 y 3, faldones de sellado, temperaturas")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(2, "SECADOR DE CINTA -\nPLANTA Y CORTE LONGITUDINAL", "1:50", revs)
    corte(msp)
    planta(msp)
    tablas(msp)
    exportar_lamina(doc, 2)


if __name__ == "__main__":
    main()
