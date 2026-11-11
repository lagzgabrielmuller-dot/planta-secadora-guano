"""P12 - Cinta transportadora de alimentación con bordes y tacos (ítem 3) y tolva (ítem 2).

Redibujo vectorial de la lámina P12 Rev. C (PNG aprobado). Geometría de la cinta, la tolva y el
secador tomada de fuente/datos/layout_planta.json (G.cinta, G.tolva, G.secador), en metros.
Vistas: A lateral 1:50, B planta 1:50, C-C 1:10, D-D 1:25.
"""
import json
import math
import os

from lamina_secadora import (FECHA, circulo, cota, exportar_lamina, factor, flecha, globo,
                             lamina, linea, nivel, poli, rayado, rect, relleno, relleno_rect,
                             subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
C, TV, SEC = G["cinta"], G["tolva"], G["secador"]

TAN = (222, 205, 175)        # guano dentro de la tolva
GUANO = (200, 160, 110)      # capa de guano sobre la banda
NEGRO = (30, 30, 30)

# ---------------------------------------------------------------- perfil de la cinta (m)
X_COLA, X_CURVA, X_CAB = C["x_cola"], C["x_curva"], C["x_cabeza"]
Z_CARGA, R, ANG = C["z_carga"], C["R"], math.radians(C["ang"])
L1 = X_CURVA - X_COLA
L2 = R * ANG
X_FIN_CURVA = X_CURVA + R * math.sin(ANG)
Z_FIN_CURVA = Z_CARGA + R * (1 - math.cos(ANG))
L3 = (X_CAB - X_FIN_CURVA) / math.cos(ANG)
LT = L1 + L2 + L3            # 12,11 m = G.cinta.L


def perfil(s, off=0.0):
    """Punto de la línea de carga de la banda a la distancia s (m) desde la cola, desplazado off (m)
    según la normal (positivo hacia arriba)."""
    if s <= L1:
        x, z, nx, nz = X_COLA + s, Z_CARGA, 0.0, 1.0
    elif s <= L1 + L2:
        th = (s - L1) / R
        x, z = X_CURVA + R * math.sin(th), Z_CARGA + R * (1 - math.cos(th))
        nx, nz = -math.sin(th), math.cos(th)
    else:
        u = s - L1 - L2
        x, z = X_FIN_CURVA + u * math.cos(ANG), Z_FIN_CURVA + u * math.sin(ANG)
        nx, nz = -math.sin(ANG), math.cos(ANG)
    return x + off * nx, z + off * nz


def tangente(s):
    a = 0.0 if s <= L1 else (s - L1) / R if s <= L1 + L2 else ANG
    return math.cos(a), math.sin(a)


def tramo(s0, s1, off=0.0, n=80):
    return [perfil(s0 + (s1 - s0) * i / n, off if not callable(off) else off(s0 + (s1 - s0) * i / n))
            for i in range(n + 1)]


def z_banda(x):
    """Cota de la línea de carga en la abscisa x (m)."""
    if x <= X_CURVA:
        return Z_CARGA
    if x <= X_FIN_CURVA:
        return Z_CARGA + R - math.sqrt(R * R - (x - X_CURVA) ** 2)
    return Z_FIN_CURVA + (x - X_FIN_CURVA) * math.tan(ANG)


# ---------------------------------------------------------------- helpers de dibujo

def marca_corte(msp, p, d, letra, largo=8.0, h=3.6, lado=1):
    """Marca de plano de corte: trazo grueso, flecha en dirección d (unitaria) y letra."""
    nx, nz = -d[1], d[0]
    a = (p[0] - nx * 2.5, p[1] - nz * 2.5)
    b = (p[0] + nx * 2.5, p[1] + nz * 2.5)
    linea(msp, a, b, "CONTORNO", lw=70)
    q = (p[0] + d[0] * largo, p[1] + d[1] * largo)
    flecha(msp, p, q, "CONTORNO", tam=2.4)
    tn(msp, letra, (q[0] + d[0] * 2.8 * lado, q[1] + d[1] * 2.8 + 0.0), h, "MIDDLE_CENTER")


def nivel_izq(msp, x, y, texto):
    """Nivel con el texto a la izquierda del triángulo (para no invadir lo que está a la derecha)."""
    s = 1.6
    poli(msp, [(x - s, y + s * 1.2), (x + s, y + s * 1.2), (x, y)], "COTAS", cerrada=True)
    linea(msp, (x + s * 2, y), (x - s * 6, y), "COTAS")
    t(msp, texto, (x - s * 1.3, y + s * 1.4), 2.2, "BOTTOM_RIGHT")


def zigzag_v(msp, x, y0, y1, capa="FINO"):
    ym = (y0 + y1) / 2
    poli(msp, [(x, y0), (x, ym - 1.5), (x + 1.4, ym - 0.6), (x - 1.4, ym + 0.6), (x, ym + 1.5), (x, y1)], capa)


def zigzag_h(msp, x0, x1, y, capa="FINO"):
    xm = (x0 + x1) / 2
    poli(msp, [(x0, y), (xm - 1.5, y), (xm - 0.6, y - 1.4), (xm + 0.6, y + 1.4), (xm + 1.5, y), (x1, y)], capa)


def piso(msp, x0, x1, y, alto=2.6):
    rayado(msp, [(x0, y - alto), (x1, y - alto), (x1, y), (x0, y)], escala=0.45)
    linea(msp, (x0, y), (x1, y), "CONTORNO", lw=70)


# ================================================================= A - VISTA LATERAL 1:50
def vista_lateral(msp):
    k = factor("1:50") * 1000.0          # mm de papel por metro
    OX, OZ = 37.0, 176.25

    def P(x, z):
        return (OX + x * k, OZ + z * k)

    def PP(pts):
        return [P(x, z) for x, z in pts]

    # muro Oeste y piso
    rayado(msp, [P(-0.2, 0), P(0, 0), P(0, 4.85), P(-0.2, 4.85)], escala=0.25)
    rect(msp, *P(-0.2, 0), *P(0, 4.85))
    t(msp, "muro Oeste", (30.8, 236), 1.9, "MIDDLE_CENTER", rotacion=90)
    piso(msp, 29.5, 302, OZ)

    # ---- tolva (ítem 2)
    x0, x1, zb = TV["x0"], TV["x1"], TV["z_boca"]
    rx0, rx1, zr = TV["ranura_x"][0], TV["ranura_x"][1], TV["z_ranura"]
    cuerpo = [(x0 + 0.04, zb - 0.05), (x1 - 0.04, zb - 0.05), (rx1 + 0.01, zr), (rx0 - 0.01, zr)]
    relleno(msp, PP(cuerpo), TAN)
    poli(msp, PP([(x0, zb), (rx0, zr)]), "CONTORNO")
    poli(msp, PP([(x1, zb), (rx1, zr)]), "CONTORNO")
    linea(msp, P(rx0, zr), P(rx1, zr), "CONTORNO")
    linea(msp, P(x0 - 0.05, zb), P(x1 + 0.05, zb), "CONTORNO", lw=70)
    linea(msp, P(x0, zb - 0.04), P(x1, zb - 0.04), "FINO")
    xx = x0 + 0.05
    while xx < x1:                                         # rejilla de la boca
        linea(msp, P(xx, zb - 0.04), P(xx, zb), "FINO")
        xx += 0.15
    for xp in (x0, x1 - 0.08):                              # bastidor de la tolva
        rect(msp, *P(xp, 0), *P(xp + 0.08, zb))
    # faldones bajo la ranura y compuerta de altura de capa
    for xf in (rx0, rx1):
        linea(msp, P(xf, zr), P(xf, Z_CARGA + 0.07), "CONTORNO")
    linea(msp, P(rx0, Z_CARGA + 0.07), P(rx1, Z_CARGA + 0.07), "FINO")
    rect(msp, *P(rx1 + 0.03, Z_CARGA + 0.07), *P(rx1 + 0.08, 1.25))
    linea(msp, P(rx1 + 0.08, 1.05), P(x1 - 0.08, 1.05), "FINO")

    # ---- cinta: banda, bordes, tacos, largueros, retorno
    poli(msp, PP(tramo(0, LT, 0.06, 160)), "FINO")                  # borde ondulado h 60
    poli(msp, PP(tramo(0, LT, 0.0, 160)), "CONTORNO", lw=70)        # banda (ramal de carga)
    s = 0.12
    while s < LT - 0.1:                                             # tacos h 50 c/250
        linea(msp, P(*perfil(s, 0)), P(*perfil(s, 0.05)), "CONTORNO")
        s += C["paso"]
    poli(msp, PP(tramo(0.15, LT - 0.3, -0.06, 160)), "CONTORNO")    # larguero UPN 140
    poli(msp, PP(tramo(0.15, LT - 0.3, -0.20, 160)), "CONTORNO")

    def off_ret(sv):
        return -0.25 if sv < LT - 0.7 else -0.25 - 0.07 * (sv - (LT - 0.7)) / 0.7
    poli(msp, PP(tramo(0, LT, off_ret, 160)), "CONTORNO")           # ramal de retorno

    # tambores
    cc = perfil(0, -C["D_cola"] / 2)
    circulo(msp, P(*cc), C["D_cola"] / 2 * k, lw=70)
    circulo(msp, P(*cc), 0.03 * k)
    ch = perfil(LT, -C["D_motriz"] / 2)
    circulo(msp, P(*ch), C["D_motriz"] / 2 * k, lw=70)
    circulo(msp, P(*ch), 0.05 * k)
    # tensor a tornillo de la cola (3.3)
    rect(msp, *P(0.36, cc[1] - 0.035), *P(cc[0] - 0.02, cc[1] + 0.035))
    linea(msp, P(0.2, cc[1]), P(0.36, cc[1]), "CONTORNO")
    linea(msp, P(cc[0] - 0.3, cc[1]), P(cc[0] + 0.3, cc[1]), "EJES")
    # cabeza: soporte del reductor pendular, capota (3.7), rascador, bajada al secador
    rect(msp, *P(ch[0] - 0.2, ch[1] - 0.2), *P(ch[0] + 0.2, ch[1] + 0.2))
    linea(msp, P(ch[0] - 0.28, ch[1]), P(ch[0] + 0.3, ch[1]), "EJES")
    t(msp, "M8", P(ch[0] - 0.25, ch[1] - 0.32), 1.8, "TOP_LEFT")
    linea(msp, P(ch[0] + 0.12, ch[1] - 0.18), P(ch[0] + 0.33, ch[1] - 0.33), "CONTORNO")   # rascador PU
    poli(msp, PP([(11.63, 4.23), (11.63, 4.63), (12.56, 4.63), (12.56, 4.2), (12.58, SEC["H"])]), "CONTORNO")
    linea(msp, P(12.11, 3.87), P(12.17, SEC["H"]), "CONTORNO")
    linea(msp, P(12.17, SEC["H"] + 0.02), P(12.58, SEC["H"] + 0.02), "CONTORNO", lw=140)

    # rodillos portantes Ø89 (11), de retorno Ø60 (12) y ruedas de desvío Ø150 (8; 4 por lado)
    portantes = [3.3, 4.0] + [5.5 + 0.75 * i for i in range(9)]
    for sp in portantes:
        circulo(msp, P(*perfil(sp, -0.045)), 0.0445 * k)
    for i in range(12):
        sr = 0.8 + i * (11.3 - 0.8) / 11
        circulo(msp, P(*perfil(sr, off_ret(sr) - 0.03)), 0.03 * k)
    ruedas = [L1 + R * math.radians(a) for a in (3.75, 11.25, 18.75, 26.25)]
    for sw in ruedas:
        circulo(msp, P(*perfil(sw, 0.075)), 0.075 * k)

    # cordón de parada de emergencia (lado Sur, visto en primer plano)
    s_c0, s_c1 = 3.98 - X_COLA, L1 + L2 + 0.55
    poli(msp, PP(tramo(s_c0, s_c1, 0.2, 40)), "FINO")
    for sc in (s_c0, s_c1):
        px, pz = P(*perfil(sc, 0.2))
        rect(msp, px - 1.6, pz - 0.9, px + 0.6, pz + 0.9)

    # ---- estructura (3.8): patas 80×80 bajo los largueros, arriostramiento
    tops = {}
    for xa in C["apoyos_x"]:
        zt = z_banda(xa) - 0.20 / math.cos(0 if xa <= X_CURVA else ANG)
        tops[xa] = zt
        rect(msp, *P(xa - 0.04, 0), *P(xa + 0.04, zt))
        linea(msp, P(xa - 0.15, 0.01), P(xa + 0.15, 0.01), "CONTORNO", lw=100)
    a, b, c = 7.71, 10.11, 11.35
    linea(msp, P(a + 0.04, 0.35), P(c - 0.04, 0.35), "CONTORNO")
    linea(msp, P(a + 0.04, 0.35), P(b - 0.04, tops[b] - 0.05), "CONTORNO")
    linea(msp, P(b + 0.04, 0.35), P(c - 0.04, tops[c] - 0.05), "CONTORNO")

    # ---- secador (ítem 4), cortado
    xs0, h, hp = SEC["x0"], SEC["H"], SEC["h_patas"]
    poli(msp, PP([(13.18, hp), (xs0, hp), (xs0, h), (13.18, h)]), "CONTORNO")
    zigzag_v(msp, *P(13.18, hp), P(13.18, h)[1])
    for xl in (xs0 + 0.05, xs0 + 0.13):
        linea(msp, P(xl, 0), P(xl, hp), "CONTORNO")
    tn(msp, "4  SECADOR (plano 02)", P(12.3, 2.0), 1.9, "MIDDLE_CENTER")

    # ---- niveles
    nivel(msp, 48.0, OZ + Z_CARGA * k, "+0,65", lado=-1)
    nivel(msp, 47.0, OZ + zb * k, "+2,00")
    nivel_izq(msp, *P(11.2, C["z_cabeza"] + 0.08), "+4,35")
    nivel_izq(msp, *P(13.12, h + 0.05), "+3,40")

    # ---- marcas de corte
    sC = L1 + L2 + 2.6
    d = tangente(sC)
    up = perfil(sC, 0.42)
    dn = perfil(sC, -0.62)
    marca_corte(msp, P(*up), d, "C", largo=7)
    marca_corte(msp, P(*dn), d, "C", largo=7)
    xD = 2.69
    marca_corte(msp, P(xD, 2.32), (-1, 0), "D", largo=7)
    marca_corte(msp, P(xD, 0.12), (-1, 0), "D", largo=7)

    # ---- radio y ángulo de la curva
    cR = (X_CURVA, Z_CARGA + R)
    pR = (cR[0] + R * math.sin(math.radians(25)), cR[1] - R * math.cos(math.radians(25)))
    linea(msp, P(*cR), P(*pR), "COTAS")
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc(P(*cR), 0.55, 0, 360)
    t(msp, "R 2000", (P(*cR)[0] - 1.5, P(*cR)[1] + 1.6), 2.2, "BOTTOM_RIGHT")
    xi = X_FIN_CURVA - (Z_FIN_CURVA - Z_CARGA) / math.tan(ANG)        # intersección de la recta a 30°
    linea(msp, P(xi, Z_CARGA - 0.02), P(xi + 1.6, Z_CARGA - 0.02), "COTAS")
    ra = 1.3
    msp.add_arc(P(xi, Z_CARGA - 0.02), ra * k, 0, 30, dxfattribs={"layer": "COTAS"})
    t(msp, "30°", P(xi + ra + 0.12, Z_CARGA + 0.22), 2.2, "MIDDLE_LEFT")

    # ---- cotas
    cota(msp, P(X_COLA, 0), P(X_CURVA, 0), distancia=-11, escala=k / 1000)
    cota(msp, P(X_CURVA, 0), P(X_CAB, 0), distancia=-11, escala=k / 1000)
    cota(msp, P(x0, zb), P(x1, zb), distancia=15, escala=k / 1000)

    # ---- textos y referencias
    flecha_texto(msp, (109.0, P(x1, 1.1)[1]), (120.0, 200.6), "compuerta de altura de capa")
    pcd = P(*perfil(L1 + 0.15, 0.2))
    flecha_texto(msp, pcd, (160.0, 181.0), "cordón de parada de emergencia", quiebre=(152.0, 181.0))
    globo(msp, "2", (66.0, 226.0), P(2.1, 1.6), 3.6)
    globo(msp, "3.3", (44.0, 203.0), P(0.45, cc[1]), 3.6)
    globo(msp, "3.5", (160.0, 205.0), P(*perfil(ruedas[2], 0.075)), 3.6)
    globo(msp, "3.6", (104.8, 179.6), P(2.5, Z_CARGA + 0.07), 3.6)
    globo(msp, "3.1", (177.0, 224.0), P(*perfil(L1 + L2 + 2.1, 0.0)), 3.6)
    globo(msp, "3.4", (234.0, 220.0), P(*perfil(portantes[6], -0.045)), 3.6)
    globo(msp, "3.8", (203.5, 188.0), P(7.75, 0.8), 3.6)
    globo(msp, "3.7", (298.0, 271.0), P(12.56, 4.5), 3.6)
    globo(msp, "3.2", (298.0, 258.0), P(*ch), 3.6)


def flecha_texto(msp, punto, pos_texto, texto, quiebre=None, h=1.9):
    """Referencia con punto lleno y texto a la derecha (estilo del original)."""
    pts = [punto] + ([quiebre] if quiebre else []) + [(pos_texto[0] - 0.8, pos_texto[1])]
    poli(msp, pts, "COTAS")
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc(punto, 0.55, 0, 360)
    t(msp, texto, pos_texto, h, "MIDDLE_LEFT")


# ================================================================= B - PLANTA 1:50
def planta(msp):
    k = factor("1:50") * 1000.0
    OX, OY, YC = 37.0, 130.2, C["y"]

    def P(x, y):
        return (OX + x * k, OY + (y - YC) * k)

    # muro Oeste
    rayado(msp, [(33, 115.5), (37, 115.5), (37, 154), (33, 154)], escala=0.25)
    poli(msp, [(33, 115.5), (33, 154), (37, 154), (37, 115.5)], "CONTORNO")
    zigzag_h(msp, 31, 39, 115.5)

    # largueros (±0,35 / ±0,40) y banda (bordes ±0,165, cantos ±0,25)
    for yy in (0.35, 0.40):
        for sg in (1, -1):
            linea(msp, P(0.6, YC + sg * yy), P(12.3, YC + sg * yy), "CONTORNO")
    for sg in (1, -1):
        linea(msp, P(X_COLA - 0.125, YC + sg * 0.25), P(X_CAB + 0.16, YC + sg * 0.25), "CONTORNO")
        linea(msp, P(X_COLA, YC + sg * 0.165), P(X_CAB, YC + sg * 0.165), "CONTORNO", lw=70)
    xx = TV["x1"] + 0.1
    while xx < X_CAB - 0.1:
        linea(msp, P(xx, YC - 0.165), P(xx, YC + 0.165), "FINO")
        xx += C["paso"]
    # cola: tambor y tensores
    rect(msp, *P(X_COLA - 0.125, YC - 0.30), *P(X_COLA + 0.125, YC + 0.30))
    for sg in (1, -1):
        y0, y1 = sorted((YC + sg * 0.36, YC + sg * 0.47))
        rect(msp, *P(0.36, y0), *P(1.02, y1))
    linea(msp, P(X_COLA, YC - 0.6), P(X_COLA, YC + 0.6), "EJES")
    # cabeza: bastidor, tambor, UCP 50, motorreductor M8 al Norte
    rect(msp, *P(11.62, YC - 0.45), *P(12.56, YC + 0.45))
    rect(msp, *P(X_CAB - 0.16, YC - 0.30), *P(X_CAB + 0.16, YC + 0.30))
    for sg in (1, -1):
        y0, y1 = sorted((YC + sg * 0.31, YC + sg * 0.42))
        rect(msp, *P(X_CAB - 0.08, y0), *P(X_CAB + 0.08, y1))
    rect(msp, *P(11.98, YC + 0.5), *P(12.38, YC + 0.95))
    rect(msp, *P(11.55, YC + 0.6), *P(11.98, YC + 0.86))
    t(msp, "M8", P(11.6, YC + 0.73), 1.6, "MIDDLE_LEFT")
    linea(msp, P(12.38, YC + 0.62), P(12.62, YC + 0.48), "CONTORNO")
    linea(msp, P(X_CAB, YC - 0.55), P(X_CAB, YC + 0.55), "EJES")
    flecha(msp, P(10.0, YC + 0.73), P(11.53, YC + 0.73), "COTAS", tam=2.0)
    t(msp, "M8 al Norte (la pasarela del secador está al Sur)", P(9.85, YC + 0.73), 1.8, "MIDDLE_RIGHT")

    # tolva: boca 2600 × 1600, ranura 2200
    x0, x1, y0, y1 = TV["x0"], TV["x1"], TV["y0"], TV["y1"]
    rx0, rx1 = TV["ranura_x"]
    relleno_rect(msp, *P(x0, y0), *P(x1, y1), (255, 255, 255))
    rect(msp, *P(x0, y0), *P(x1, y1), lw=70)
    rect(msp, *P(x0 + 0.07, y0 + 0.07), *P(x1 - 0.07, y1 - 0.07))
    ya, yb = YC - 0.275, YC + 0.275
    rect(msp, *P(rx0, ya), *P(rx1, yb))
    for (xa, ya_), (xb, yb_) in (((x0, y1), (rx0, yb)), ((x0, y0), (rx0, ya)),
                                 ((x1, y1), (rx1, yb)), ((x1, y0), (rx1, ya))):
        linea(msp, P(xa, ya_), P(xb, yb_), "CONTORNO")
    # vibrador M15 (lado Sur)
    rect(msp, *P(2.35, y0 - 0.25), *P(2.66, y0))
    t(msp, "M15", P(2.72, y0 - 0.15), 1.8, "MIDDLE_LEFT")

    # cordón de parada (lado Sur)
    linea(msp, P(1.01, YC - 0.62), P(11.6, YC - 0.62), "CONTORNO")
    t(msp, "cordón de parada (lado Sur)", P(7.0, YC - 0.86), 1.8, "MIDDLE_CENTER")

    # secador (ítem 4), cortado
    sy0, sy1, sx0 = SEC["y0"], SEC["y0"] + SEC["A"], SEC["x0"]
    poli(msp, [P(13.18, sy1), P(sx0, sy1), P(sx0, sy0), P(13.18, sy0)], "CONTORNO")
    zigzag_v(msp, P(13.18, 0)[0], P(0, sy0)[1], P(0, sy1)[1])
    t(msp, "secador", P(12.85, sy0 + 0.4), 1.9, "MIDDLE_CENTER")

    # norte
    flecha(msp, (141.0, 141.0), (141.0, 149.5), "CONTORNO", tam=2.0)
    tn(msp, "N", (141.0, 151.0), 2.6, "BOTTOM_CENTER")

    # cotas
    cota(msp, P(rx0, y1), P(rx1, y1), distancia=4.2, escala=k / 1000, valor="<> ranura")
    cota(msp, P(x0, y1), P(x0, y0), distancia=-20.2, escala=k / 1000)
    cota(msp, P(12.62, YC + 0.25), P(12.62, YC - 0.25), distancia=3.5, escala=k / 1000)


# ================================================================= C-C 1:10
def corte_cc(msp):
    k = factor("1:10")
    OX, OY = 80.2, 59.9

    def P(x, y):
        return (OX + x * k, OY + y * k)

    def R(x0, y0, x1, y1, capa="CONTORNO", lw=None):
        rect(msp, *P(x0, y0), *P(x1, y1), capa, lw=lw)

    # guano y banda
    relleno(msp, [P(-150, 0), P(150, 0), P(150, 35), P(-150, 35)], GUANO)
    t(msp, "guano", P(-60, 17), 1.8, "MIDDLE_CENTER")
    relleno(msp, [P(-250, -6), P(250, -6), P(250, 0), P(-250, 0)], NEGRO)
    R(-250, -6, 250, 0)
    # bordes ondulados h 60 y taco en T h 50
    for sg in (1, -1):
        pts = [P(sg * 150, 0), P(sg * 171, 0), P(sg * 171, 60), P(sg * 150, 60)]
        relleno(msp, pts, NEGRO)
        poli(msp, pts, "CONTORNO", cerrada=True)
    linea(msp, P(-150, 50), P(150, 50), "CONTORNO", lw=70)
    # rodillo portante Ø89 × 600 (3.4) y soportes
    R(-300, -98, 300, -8)
    linea(msp, P(-345, -53), P(345, -53), "EJES")
    for sg in (1, -1):
        R(sg * 310, -37, sg * 335, -137)
    # largueros UPN 140 (perfil C, alas hacia adentro)
    for sg in (1, -1):
        pts = [(400, -68), (338, -68), (338, -76), (392, -76), (392, -198), (338, -198), (338, -206), (400, -206)]
        q = [P(sg * x, y) for x, y in pts]
        relleno(msp, q, NEGRO)
        poli(msp, q, "CONTORNO", cerrada=True)
    # travesaño, colgantes, ramal de retorno y rodillos de retorno Ø60 (3.4)
    linea(msp, P(-400, -227), P(400, -227), "CONTORNO")
    linea(msp, P(-400, -248), P(400, -248), "CONTORNO")
    for sg in (1, -1):
        R(sg * 338, -206, sg * 347, -360)
        R(sg * 160, -300, sg * 171, -360)
        circulo(msp, P(sg * 215, -334), 30 * k)
    relleno(msp, [P(-250, -293), P(250, -293), P(250, -287), P(-250, -287)], NEGRO)
    linea(msp, P(-160, -324), P(160, -324), "CONTORNO")
    linea(msp, P(-160, -347), P(160, -347), "CONTORNO")
    # cordón de parada (lado Sur)
    R(-530, -137, -511, -20)
    circulo(msp, P(-520, -12), 12 * k)
    linea(msp, P(-511, -137), P(-400, -137), "CONTORNO")
    t(msp, "cordón", P(-549, 18), 1.8, "BOTTOM_LEFT")

    # cotas
    cota(msp, P(-150, 60), P(150, 60), distancia=3.5, escala=k)
    cota(msp, P(-250, 0), P(250, 0), distancia=14.5, escala=k)
    cota(msp, P(-171, 50), P(-171, 0), distancia=-4.5, escala=k)
    cota(msp, P(171, 0), P(171, 60), distancia=-4.5, escala=k)
    cota(msp, P(-400, -206), P(400, -206), distancia=-20.4, escala=k)

    # referencias
    flecha_texto2(msp, P(-49, 50), (P(-275, 190)), "taco en T h 50 c/250")
    flecha_texto2(msp, P(-161, 60), (P(-275, 162)), "borde ondulado h 60")
    globo(msp, "3.1", P(300, 118), P(110, 2), 3.6)
    globo(msp, "3.4", P(449, -29), P(250, -60), 3.6)
    globo(msp, "3.4", P(470, -330), P(215, -334), 3.6)
    globo(msp, "3.8", P(-493, -297), P(-400, -180), 3.6)
    flecha_texto(msp, P(400, -150), (122.0, 44.0), "larguero UPN 140", quiebre=(121.0, 44.0), h=1.8)


def flecha_texto2(msp, punto, pos_fin_texto, texto, h=1.8):
    """Referencia con texto a la izquierda (termina en pos_fin_texto)."""
    poli(msp, [punto, (pos_fin_texto[0] + 0.8, pos_fin_texto[1])], "COTAS")
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc(punto, 0.55, 0, 360)
    t(msp, texto, pos_fin_texto, h, "MIDDLE_RIGHT")


# ================================================================= D-D 1:25
def corte_dd(msp):
    k = factor("1:25")
    OX, OY = 180.0, 14.5

    def P(x, z):
        return (OX + x * k, OY + z * k)

    # tolva: guano, paredes inox 3 mm, faldones (3.6)
    relleno(msp, [P(-745, 1945), P(745, 1945), P(152, 836), P(-152, 836)], TAN)
    relleno(msp, [P(-150, 650), P(150, 650), P(150, 705), P(-150, 705)], GUANO)
    for sg in (1, -1):
        linea(msp, P(sg * 802, 2000), P(sg * 164, 836), "CONTORNO", lw=70)
        rect(msp, *P(sg * 152, 709), *P(sg * 188, 836))
        linea(msp, P(sg * 152, 836), P(sg * 152, 650), "FINO")
    # boca con rejilla
    linea(msp, P(-830, 2000), P(830, 2000), "CONTORNO", lw=70)
    linea(msp, P(-830, 1975), P(830, 1975), "FINO")
    for i in range(-7, 8):
        linea(msp, P(i * 100, 1975), P(i * 100, 2000), "FINO")
    # bastidor de la tolva y pata central 80×80
    for sg in (1, -1):
        rect(msp, *P(sg * 800, 0), *P(sg * 861, 1804))
    rect(msp, *P(-40, 0), *P(40, 428))
    # banda + placa UHMW, largueros UPN 140, ramal de retorno
    rect(msp, *P(-272, 612), *P(272, 650))
    for sg in (1, -1):
        q = [P(sg * 323, 428), P(sg * 403, 428), P(sg * 403, 575), P(sg * 323, 575)]
        relleno(msp, q, NEGRO)
        poli(msp, q, "CONTORNO", cerrada=True)
    linea(msp, P(-250, 400), P(250, 400), "CONTORNO", lw=70)
    # vibrador M15
    rect(msp, *P(-1049, 1154), *P(-861, 1403))
    t(msp, "M15", P(-955, 1278), 1.8, "MIDDLE_CENTER")
    piso(msp, OX - 1007 * k, OX + 1010 * k, OY, alto=1.5)

    # cotas
    cota(msp, P(861, 0), P(861, 2000), distancia=-7.9, escala=k)
    cota(msp, P(-272, 0), P(-272, 650), distancia=17.2, escala=k)
    cota(msp, P(-150, 650), P(150, 650), distancia=-8.9, escala=k)

    # referencias
    flecha_texto2(msp, P(-505, 1450), P(-890, 1560), "inox 3 mm")
    globo(msp, "2", P(450, 1750), P(300, 1500), 3.6)
    globo(msp, "3.6", P(560, 900), P(188, 770), 3.6)
    globo(msp, "3.6", (204.5, 42.0), P(272, 630), 3.6)


# ================================================================= tablas y notas
def tablas(msp):
    subtitulo(msp, "DATOS Y CÁLCULO (DIN 22101 simplificado)", 306, 275.5, 3.0)
    filas = [["Magnitud", "Valor", "Observación"],
             ["Caudal requerido", "1,25 m³/h", "1000 kg/h a 800 kg/m³"],
             ["Caudal máximo (v = 0,10 m/s)", "3,24 m³/h", "bolsillo 60 % lleno"],
             ["Velocidad de trabajo", "3,9 cm/s", "VFD al 39 %"],
             ["Desarrollo / desnivel", "12,1 / 3,70 m", "4,2 m horiz. + R 2 m + 30°"],
             ["F rodadura (f = 0,030)", "104 N", "banda, rodillos, carga"],
             ["F elevación", "261 N", "q·H·g"],
             ["F extracción bajo tolva", "2165 N", "Janssen + faldones"],
             ["F total en el tambor", "2780 N", "+ rascadores 250 N"],
             ["Potencia a 0,10 m/s", "0,33 kW", "η = 0,85"],
             ["Motor elegido M8", "0,75 kW", "arranque x1,5 = 0,49 kW"],
             ["T1 / T2 (μ = 0,35; 180°)", "4168 / 1388 N", "Euler"],
             ["Tensión por mm de banda", "8,3 N/mm", "EP 400/3: CS = 48"],
             ["Tambor motriz", "Ø320 - 6,0 rpm", "i ≈ 1:235"],
             ["Par en el eje motriz", "445 N·m", "reductor pendular"]]
    y = tabla(msp, 306, 273.0, [42, 27, 34], filas, h_fila=3.65, altura=2.0, alin=["L", "R", "L"])

    subtitulo(msp, "LISTA DE PARTES", 306, y - 6.0, 3.0)
    filas = [["N°", "Denominación", "Cant."],
             ["2", "Tolva de recepción 3,1 m³ (inox 304)", "1"],
             ["3.1", "Banda EP 400/3 500 mm, bordes 60, tacos 50", "24,6 m"],
             ["3.2", "Tambor motriz Ø320 engomado + UCP 50", "1"],
             ["3.3", "Tambor de cola Ø250 + tensor a tornillo", "1"],
             ["3.4", "Rodillos portantes Ø89 / retorno Ø60", "11 / 12"],
             ["3.5", "Ruedas de desvío Ø150 (curva R 2 m)", "8"],
             ["3.6", "Faldones 12 mm y placa UHMW 2,4 m", "1 cj."],
             ["3.7", "Capota inox, rascador PU y bajada", "1"],
             ["3.8", "Largueros UPN 140, patas 80x80, cordón", "1 cj."],
             ["M8", "Motorreductor 0,75 kW 6 rpm con VFD", "1"],
             ["M15", "Vibrador de tolva 0,25 kW", "1"]]
    y = tabla(msp, 306, y - 8.5, [10, 74, 19], filas, h_fila=3.65, altura=2.0, alin=["C", "L", "C"])

    subtitulo(msp, "POR QUÉ CINTA CON TACOS Y NO SINFÍN", 306, y - 6.0, 3.0)
    yn = y - 8.0
    for nota in [
        "1. El guano húmedo (72 %) es pastoso y se pega: en un sinfín a 30° gira con la hélice y resbala "
        "hacia atrás (rendimiento 40 a 50 %, atascos). En la cinta viaja quieto en bolsillos de "
        "300 x 50 x 250 mm y no retrocede.",
        "2. El tramo horizontal bajo la tolva extrae y dosifica: la compuerta fija la capa en 55 mm y el "
        "variador fija el caudal.",
        "3. Carga a +0,65 m: la boca de la tolva queda a +2,00 m y la pala la llena sin rampa.",
        "4. La banda se ve y se limpia: rascador en V en la cola y de poliuretano en la cabeza.",
        "5. Motorreductor al Norte; cordón de parada del lado Sur, donde circula el operario de secado.",
        "6. Cotas en mm; niveles en m desde el piso terminado (±0,00).",
    ]:
        t(msp, nota, (306, yn), 1.8, "TOP_LEFT", ancho=101)
        renglones = math.ceil(len(nota) * 1.8 * 0.6 / 101)
        yn -= renglones * 1.8 * 1.45 + 1.4


# ================================================================= main
def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Lámina nueva (B1): cinta con bordes y tacos en vez del sinfín (plano 06: M8)"),
            ("C", "09/2026", "Título de planta B libre (cruzaba el muro Oeste); rótulos de vista A separados"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(12, "CINTA TRANSPORTADORA DE ALIMENTACIÓN", "INDICADAS", revs)
    for e in msp.query('TEXT[layer=="ROTULO"]'):     # que entren en sus casillas del rótulo
        if e.dxf.text == "INDICADAS":
            e.dxf.height = 2.6
        elif e.dxf.text == "CINTA TRANSPORTADORA DE ALIMENTACIÓN":
            e.dxf.height = 3.6

    titulo_vista(msp, "CINTA TRANSPORTADORA DE ALIMENTACIÓN CON BORDES Y TACOS (ítem 3) Y TOLVA (ítem 2)",
                 28, 280.5, 3.5)
    vista_lateral(msp)
    titulo_vista(msp, "A - VISTA LATERAL DESDE EL SUR  -  ESC. 1:50", 28, 157.0, 3.3)
    planta(msp)
    titulo_vista(msp, "B - PLANTA  -  ESC. 1:50", 28, 105.0, 3.3)
    corte_cc(msp)
    titulo_vista(msp, "C-C  CORTE DEL TRAMO A 30°  -  ESC. 1:10", 28, 97.8, 3.1)
    corte_dd(msp)
    titulo_vista(msp, "D-D  CORTE BAJO LA TOLVA  -  ESC. 1:25", 133, 97.8, 3.1)
    tablas(msp)
    exportar_lamina(doc, 12)


if __name__ == "__main__":
    main()
