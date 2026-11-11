"""P11 - Implantación del predio y circulación de camiones, esc. 1:400.

Geometría en metros de fuente/datos/layout_planta.json (x al Este, y al Norte, origen en el
vértice SO de la nave). Los recorridos de los camiones (que en el JSON figuran omitidos) se
transcriben del plano original Rev. C con el mismo criterio: eje trasero del camión rígido.
Incluye el perfil transversal tipo de calle (H 1:100 - V 1:25).
"""
import json
import math
import os

from lamina_secadora import (FECHA, circulo, cota, escala_grafica, exportar_lamina, factor,
                             globo, lamina, linea, norte, notas, poli, rayado, rect, relleno,
                             relleno_circulo, relleno_rect, subtitulo, t, tabla, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

K = factor("1:400")          # mm reales -> mm de papel
M = K * 1000.0               # 1 m real = 2,5 mm de papel
OX, OY = 90.0, 149.7         # posición en la hoja del origen (vértice SO de la nave)

# colores del original
VERDE = (233, 242, 225)
PAVIM = (218, 218, 214)
PLAYON = (206, 206, 204)
NAVE = (246, 246, 246)
ANEXO = (240, 236, 232)
VEREDA = (238, 238, 234)
CALZADA = (207, 207, 202)
BANQUINA = (228, 222, 206)
ARBOL = (196, 222, 184)
MURO = (60, 60, 59)
R_GUANO = (150, 88, 28)
R_SECO = (39, 127, 74)
R_CASC = (222, 132, 0)
ENVOLV = (110, 110, 110)
PUESTO = (241, 213, 110)
TANQUE = (220, 225, 235)


def titulo(msp, contenido, x, y, altura):
    """Título subrayado doble con el largo real del texto (Arial negrita mayúsculas ~0,79 h)."""
    tn(msp, contenido, (x, y), altura, "BOTTOM_LEFT")
    largo = 0.79 * altura * len(contenido)
    msp.add_line((x, y - 1.0), (x + largo, y - 1.0), dxfattribs={"layer": "CONTORNO"})
    msp.add_line((x, y - 1.8), (x + largo, y - 1.8), dxfattribs={"layer": "FINO"})


def P(x, y):
    """Coordenadas reales (m) -> papel (mm)."""
    return (OX + x * M, OY + y * M)


def PL(pts):
    return [P(x, y) for x, y in pts]


def relleno_con_huecos(msp, ext, huecos, color):
    h = msp.add_hatch(dxfattribs={"layer": "RELLENO"})
    h.rgb = color
    h.paths.add_polyline_path(ext, is_closed=True, flags=1)
    for hu in huecos:
        h.paths.add_polyline_path(hu, is_closed=True, flags=16)
    return h


# ---------------------------------------------------------------- recorridos

def empalme(pts, radios, n=14):
    """Polilínea con esquinas redondeadas: radios[i] para el vértice interior i (0 = canto vivo)."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        r = radios[i - 1] if i - 1 < len(radios) else 0
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if not r:
            out.append(b)
            continue
        u = (a[0] - b[0], a[1] - b[1]); lu = math.hypot(*u); u = (u[0] / lu, u[1] / lu)
        v = (c[0] - b[0], c[1] - b[1]); lv = math.hypot(*v); v = (v[0] / lv, v[1] / lv)
        ang = math.acos(max(-1, min(1, u[0] * v[0] + u[1] * v[1])))
        d = r / math.tan(ang / 2)
        p0 = (b[0] + u[0] * d, b[1] + u[1] * d)
        p1 = (b[0] + v[0] * d, b[1] + v[1] * d)
        bis = (u[0] + v[0], u[1] + v[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
        dc = r / math.sin(ang / 2)
        cc = (b[0] + bis[0] * dc, b[1] + bis[1] * dc)
        a0 = math.atan2(p0[1] - cc[1], p0[0] - cc[0])
        a1 = math.atan2(p1[1] - cc[1], p1[0] - cc[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            aa = a0 + da * k / n
            out.append((cc[0] + r * math.cos(aa), cc[1] + r * math.sin(aa)))
    out.append(pts[-1])
    return out


def arco_pts(c, r, a0, a1, n=24):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def punta(msp, p, ang, color, tam=1.5):
    a = (p[0] - tam * math.cos(ang) - tam * 0.38 * math.sin(ang), p[1] - tam * math.sin(ang) + tam * 0.38 * math.cos(ang))
    b = (p[0] - tam * math.cos(ang) + tam * 0.38 * math.sin(ang), p[1] - tam * math.sin(ang) - tam * 0.38 * math.cos(ang))
    h = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    h.rgb = color
    h.paths.add_polyline_path([p, a, b], is_closed=True)


def recorrido(msp, pts_m, color, cada=22.0, tipo=None, lw=35, desde=6.0):
    """Dibuja un recorrido (puntos en m) con puntas de flecha cada 'cada' metros."""
    pp = PL(pts_m)
    e = poli(msp, pp, "COTAS", color=color, lw=lw, tipo=tipo)
    if tipo:
        e.dxf.ltscale = 2.0
    # flechas a lo largo
    acum, prox = 0.0, desde * M
    for a, b in zip(pp[:-1], pp[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        while L > 0 and acum + L >= prox:
            f = (prox - acum) / L
            q = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            punta(msp, q, math.atan2(b[1] - a[1], b[0] - a[0]), color)
            prox += cada * M
        acum += L


def recortar_x(pts, xmin, xmax):
    """Recorta una polilínea (m) a la franja xmin <= x <= xmax (para la calle pública)."""
    out = []
    for p in pts:
        out.append((min(max(p[0], xmin), xmax), p[1]))
    return out


# ---------------------------------------------------------------- símbolos

def camion(msp, frente, ang, color_caja=(250, 248, 240), chevrones=False, gris=False):
    """Camión rígido 7,6 x 2,5 m visto en planta. frente = punto medio del paragolpes (m),
    ang = rumbo hacia donde mira la cabina (grados)."""
    c = G["camion"]
    L, A = c["L"], c["A"]
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -uy, ux

    def q(s, n):  # s hacia atrás desde el frente, n lateral
        return P(frente[0] - ux * s + nx * n, frente[1] - uy * s + ny * n)

    caja = [q(c["caja"][0], -A / 2), q(L, -A / 2), q(L, A / 2), q(c["caja"][0], A / 2)]
    cab = [q(0, -A / 2 + 0.1), q(1.9, -A / 2 + 0.1), q(1.9, A / 2 - 0.1), q(0, A / 2 - 0.1)]
    if gris:
        poli(msp, caja + [q(0, A / 2), q(0, -A / 2)], "FINO", cerrada=False, color=ENVOLV)
        return
    relleno(msp, caja, color_caja)
    relleno(msp, cab, (255, 255, 255))
    poli(msp, caja, "CONTORNO", cerrada=True, lw=70)
    poli(msp, cab, "CONTORNO", cerrada=True, lw=50)
    poli(msp, [q(0.35, -A / 2 + 0.3), q(0.35, A / 2 - 0.3), q(1.0, A / 2 - 0.3), q(1.0, -A / 2 + 0.3)], "FINO", cerrada=True)
    # ruedas
    for s in (c["eje_del"], c["eje_tras"]):
        for n in (-A / 2 - 0.05, A / 2 + 0.05):
            poli(msp, [q(s - 0.5, n - 0.12), q(s + 0.5, n - 0.12), q(s + 0.5, n + 0.12), q(s - 0.5, n + 0.12)],
                 "CONTORNO", cerrada=True, lw=50)
    if chevrones:
        for s in (3.1, 4.0, 4.9, 5.8, 6.7):
            poli(msp, [q(s + 0.45, -0.85), q(s, 0), q(s + 0.45, 0.85)], "CONTORNO", lw=50)


def pose_puntos(frente, ang):
    c = G["camion"]
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -uy, ux
    return [(frente[0] - ux * s + nx * n, frente[1] - uy * s + ny * n)
            for s, n in ((0, -c["A"] / 2), (c["L"], -c["A"] / 2), (c["L"], c["A"] / 2), (0, c["A"] / 2))]


def envolvente(msp, eje_pts, ang_de):
    """Envolvente de barrido de una maniobra en marcha atrás: posiciones del camión cada tanto y
    trayectoria de las esquinas extremas. eje_pts: puntos del eje trasero (m);
    ang_de(i): rumbo de la cabina en el punto i."""
    c = G["camion"]
    traz = [[], [], [], []]
    n = len(eje_pts)
    for i, e in enumerate(eje_pts):
        a = ang_de(i)
        fr = (e[0] + math.cos(math.radians(a)) * c["eje_tras"], e[1] + math.sin(math.radians(a)) * c["eje_tras"])
        esq = pose_puntos(fr, a)
        for j in range(4):
            traz[j].append(esq[j])
        if i in (0, n // 2):
            poli(msp, PL(esq), "FINO", cerrada=True, color=ENVOLV, lw=35)
    for j in range(4):
        poli(msp, PL(traz[j]), "FINO", color=ENVOLV, lw=35)


def farola(msp, x, y):
    c = P(x, y)
    circulo(msp, c, 1.15, "CONTORNO", lw=35)
    linea(msp, (c[0] - 2.1, c[1]), (c[0] + 2.1, c[1]), "CONTORNO", lw=35)
    linea(msp, (c[0], c[1] - 2.1), (c[0], c[1] + 2.1), "CONTORNO", lw=35)
    h = msp.add_hatch(dxfattribs={"layer": "CONTORNO"})
    h.paths.add_edge_path().add_arc(c, 0.4, 0, 360)


def arbol(msp, x, y, r):
    c = P(x, y)
    relleno_circulo(msp, c, r * M, ARBOL)
    circulo(msp, c, r * M, "CONTORNO", lw=50)
    relleno_rect(msp, c[0] - 0.25, c[1] - 0.25, c[0] + 0.25, c[1] + 0.25, (90, 90, 90))


def cruz(msp, c, s=0.75):
    linea(msp, (c[0] - s, c[1] - s), (c[0] + s, c[1] + s), "CONTORNO", lw=50)
    linea(msp, (c[0] - s, c[1] + s), (c[0] + s, c[1] - s), "CONTORNO", lw=50)


def puesto(msp, num, c, s=2.3):
    pts = [(c[0], c[1] + s), (c[0] + s, c[1]), (c[0], c[1] - s), (c[0] - s, c[1])]
    relleno(msp, pts, PUESTO)
    poli(msp, pts, "CONTORNO", cerrada=True, lw=35)
    tn(msp, str(num), c, 1.8, "MIDDLE_CENTER")


def globo_a(msp, txt, c, r=2.1):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, "COTAS", color=R_GUANO, lw=50)
    tn(msp, txt, c, 1.8, "MIDDLE_CENTER", color=R_GUANO)


def globo_b(msp, txt, c, a, r=3.0):
    relleno_circulo(msp, c, r, (255, 255, 255))
    globo(msp, txt, c, a, radio=r)
    msp.query("CIRCLE")[-1].dxf.lineweight = 50


def auto(msp, x, y):
    x0, y0 = P(x - 0.9, y - 2.3)
    x1, y1 = P(x + 0.9, y + 2.3)
    relleno_rect(msp, x0, y0, x1, y1, (255, 255, 255))
    rect(msp, x0, y0, x1, y1, "CONTORNO", lw=35)
    rect(msp, x0 + 0.5, y0 + 2.2, x1 - 0.5, y1 - 2.0, "FINO")
    linea(msp, (x0 + 0.5, y1 - 1.2), (x1 - 0.5, y1 - 1.2), "FINO")


# ---------------------------------------------------------------- planta

def planta(msp):
    pr = G["predio"]
    calle = G["calle"]
    XMIN, XMAX = -23.8, 51.9          # recorte de la calle pública en la hoja

    # ---- calle pública, vereda y banquina
    relleno_rect(msp, *P(XMIN, calle["y1"]), *P(XMAX, pr["y0"]), VEREDA)
    relleno_rect(msp, *P(XMIN, calle["y0"]), *P(XMAX, calle["y1"]), CALZADA)
    yb = calle["y0"] - calle["banquina"]
    relleno_rect(msp, *P(XMIN, yb), *P(XMAX, calle["y0"]), BANQUINA)
    for i in range(48):
        x = XMIN + 0.8 + i * 1.6
        if x > XMAX - 0.5:
            break
        yy = yb + (0.45 if i % 2 else 1.0)
        relleno_circulo(msp, P(x, yy), 0.13, (110, 100, 80))
    # línea central discontinua
    x = XMIN + 1.0
    while x < XMAX - 1:
        x1 = min(x + 3.0, XMAX - 1)
        linea(msp, P(x, -42.5), P(x1, -42.5), "FINO", color=(255, 255, 255), lw=50)
        x += 6.0
    # entrada vehicular (desde la calle)
    relleno(msp, PL(G["entrada_vehicular"]), PAVIM)
    ev = G["entrada_vehicular"]
    poli(msp, PL([p for p in ev if p[0] < 0 and p[1] < -36.0]), "CONTORNO", lw=50)
    poli(msp, PL([p for p in ev if p[0] > 8.9 and p[1] < -36.0]), "CONTORNO", lw=50)
    linea(msp, P(XMIN, calle["y1"]), P(-4.0, calle["y1"]), "CONTORNO", lw=50)
    linea(msp, P(12.0, calle["y1"]), P(XMAX, calle["y1"]), "CONTORNO", lw=50)
    linea(msp, P(XMIN, calle["y0"]), P(XMAX, calle["y0"]), "CONTORNO", lw=50)
    linea(msp, P(XMIN, yb), P(XMAX, yb), "CONTORNO", lw=50)
    linea(msp, P(XMAX, yb), P(XMAX, pr["y0"]), "CONTORNO", lw=50)
    # corte de la calle (línea de interrupción)
    xa = P(XMIN, 0)[0]
    poli(msp, [(xa, P(0, pr["y0"])[1]), (xa, P(0, -41.4)[1]), (xa - 1.8, P(0, -41.9)[1]),
               (xa + 1.0, P(0, -42.4)[1]), (xa, P(0, -42.8)[1]), (xa, P(0, yb)[1])], "CONTORNO", lw=50)

    # ---- predio: verde, pavimento y playones
    relleno_rect(msp, *P(pr["x0"], pr["y0"]), *P(pr["x1"], pr["y1"]), VERDE)
    pav = G["pavimento"][0]
    relleno_con_huecos(msp, PL(pav["ext"]), [PL(h) for h in pav["holes"]], PAVIM)
    for pl in G["playones"]:
        relleno_rect(msp, *P(pl["x0"], pl["y0"]), *P(pl["x1"], pl["y1"]), PLAYON)
    # báscula
    b = G["bascula"]
    relleno_rect(msp, *P(b["x0"], b["y0"]), *P(b["x1"], b["y1"]), (190, 190, 186))
    relleno_rect(msp, *P(b["x0"] + 0.35, b["y0"] + 0.35), *P(b["x1"] - 0.35, b["y1"] - 0.35), (212, 212, 208))
    # bordes del pavimento
    poli(msp, PL(pav["ext"]), "CONTORNO", cerrada=True, lw=50)
    for h in pav["holes"]:
        poli(msp, PL(h), "CONTORNO", cerrada=True, lw=50)
    for pl in G["playones"]:
        rect(msp, *P(pl["x0"], pl["y0"]), *P(pl["x1"], pl["y1"]), "CONTORNO", lw=50)
    rect(msp, *P(b["x0"], b["y0"]), *P(b["x1"], b["y1"]), "CONTORNO", lw=100)
    rect(msp, *P(b["x0"] + 0.35, b["y0"] + 0.35), *P(b["x1"] - 0.35, b["y1"] - 0.35), "FINO")

    # ---- estacionamiento (4 autos)
    e = G["estacionamiento"]
    paso = (e["x1"] - e["x0"]) / e["n"]
    for i in range(e["n"] + 1):
        linea(msp, P(e["x0"] + i * paso, e["y0"]), P(e["x0"] + i * paso, e["y1"]), "CONTORNO", lw=50)
    for i in (0, 2):
        auto(msp, e["x0"] + (i + 0.5) * paso, (e["y0"] + e["y1"]) / 2)

    # ---- nave de proceso, anexo y equipos exteriores
    n = G["nave"]
    relleno_rect(msp, *P(0, 0), *P(n["L"], n["A"]), NAVE)
    huecos = {"O": [], "S": [], "E": [], "N": []}
    for pp in G["portones"] + G["puertas"]:
        huecos[pp["muro"]].append((pp["a"], pp["b"]))

    def muro(a, b, lado, largo):
        cortes = sorted(huecos[lado])
        s = 0.0
        tramos = []
        for c0, c1 in cortes:
            tramos.append((s, c0))
            s = c1
        tramos.append((s, largo))
        for s0, s1 in tramos:
            pa = (a[0] + (b[0] - a[0]) * s0 / largo, a[1] + (b[1] - a[1]) * s0 / largo)
            pb = (a[0] + (b[0] - a[0]) * s1 / largo, a[1] + (b[1] - a[1]) * s1 / largo)
            linea(msp, P(*pa), P(*pb), "CONTORNO", color=MURO, lw=100)

    muro((0, 0), (n["L"], 0), "S", n["L"])
    muro((n["L"], 0), (n["L"], n["A"]), "E", n["A"])
    muro((0, n["A"]), (n["L"], n["A"]), "N", n["L"])
    muro((0, 0), (0, n["A"]), "O", n["A"])
    linea(msp, P(0, 9.0), P(n["L"], 9.0), "COTAS", color=R_CASC, lw=35)
    t(msp, "cumbrera +8,35", (P(16.5, 9.0)[0], P(0, 9.0)[1] + 1.2), 1.8, "BOTTOM_CENTER")
    tn(msp, "NAVE DE PROCESO", P(13.0, 6.2), 3.0, "MIDDLE_CENTER")
    t(msp, "33,0 x 18,0 m - 594 m² (plano 01)", P(13.0, 3.9), 2.0, "MIDDLE_CENTER")
    t(msp, "1  playa de descarga", P(1.9, 11.2), 1.9, "MIDDLE_LEFT")
    t(msp, "8  acopio", P(27.2, 6.0), 2.0, "MIDDLE_LEFT")
    # minicargadora en el acopio (puesto 6)
    relleno_rect(msp, *P(29.4, 0.15), *P(30.9, 1.75), PUESTO)
    rect(msp, *P(29.4, 0.15), *P(30.9, 1.75), "CONTORNO", lw=50)
    rect(msp, *P(29.65, 0.5), *P(30.65, 1.4), "FINO")

    a = G["anexo"]
    relleno_rect(msp, *P(a["x0"], a["y0"]), *P(a["x1"], a["y1"]), ANEXO)
    rect(msp, *P(a["x0"], a["y0"]), *P(a["x1"], a["y1"]), "CONTORNO", lw=70)
    tn(msp, "ANEXO", P(24.5, 22.0), 2.4, "MIDDLE_CENTER")
    t(msp, "generador", P(24.5, 20.2), 1.9, "MIDDLE_CENTER")
    for eq, d in ((G["ciclon"], G["ciclon"]["D"]), (G["scrubber"], G["scrubber"]["D"]), (G["tanque_sol"], G["tanque_sol"]["D"])):
        relleno_circulo(msp, P(eq["x"], eq["y"]), d / 2 * M, (255, 255, 255))
        circulo(msp, P(eq["x"], eq["y"]), d / 2 * M, "CONTORNO", lw=50)
    ex = G["extractor"]
    circulo(msp, P(ex["chim_x"], ex["chim_y"]), ex["chim_D"] / 2 * M, "CONTORNO", lw=50)
    ch = a["chimenea"]
    circulo(msp, P(ch["x"], ch["y"]), ch["D"] / 2 * M, "CONTORNO", lw=50)
    s = G["silo"]
    relleno_circulo(msp, P(s["x"], s["y"]), s["D"] / 2 * M, (255, 255, 255))
    circulo(msp, P(s["x"], s["y"]), s["D"] / 2 * M, "CONTORNO", lw=50)
    t(msp, "silo 13", (P(s["x"], 0)[0], P(0, s["y"] + s["D"] / 2)[1] + 2.0), 1.8, "BOTTOM_CENTER")
    linea(msp, P(s["x"] + s["D"] / 2, s["y"]), P(37.5, s["y"]), "CONTORNO", lw=35)
    t(msp, "manguera", (P(35.5, 0)[0], P(0, s["y"])[1] + 0.7), 1.4, "BOTTOM_CENTER")
    tn(msp, "PL1", P(-8.2, 7.2), 2.2, "MIDDLE_LEFT")
    tn(msp, "P1", P(-1.0, 17.8), 2.2, "MIDDLE_RIGHT")
    tn(msp, "PL2", P(24.6, -1.5), 2.2, "MIDDLE_LEFT")
    tn(msp, "PL3", P(35.5, 25.0), 2.2, "MIDDLE_CENTER")
    # cámara de lixiviados 26
    cl = G["camara_lix"]
    rect(msp, *P(cl["x"] - cl["a"] / 2, cl["y"] - cl["a"] / 2), *P(cl["x"] + cl["a"] / 2, cl["y"] + cl["a"] / 2), "CONTORNO", lw=50)
    tn(msp, "26", (P(cl["x"], 0)[0], P(0, cl["y"] - cl["a"] / 2)[1] - 0.8), 1.6, "TOP_CENTER")

    # ---- tanque de incendio y casilla de bomba (fuera del cerco Oeste, dentro del predio)
    ti = G["tanque_incendio"]
    relleno_circulo(msp, P(ti["x"], ti["y"]), ti["D"] / 2 * M, TANQUE)
    circulo(msp, P(ti["x"], ti["y"]), ti["D"] / 2 * M, "CONTORNO", lw=50)
    t(msp, "tanque 27", (P(ti["x"], 0)[0], P(0, ti["y"] + ti["D"] / 2)[1] + 1.6), 1.7, "BOTTOM_CENTER")
    cb = G["casilla_bomba"]
    relleno_rect(msp, *P(cb["x"] - 1.0, cb["y"] - 0.7), *P(cb["x"] + 1.0, cb["y"] + 0.7), ANEXO)
    rect(msp, *P(cb["x"] - 1.0, cb["y"] - 0.7), *P(cb["x"] + 1.0, cb["y"] + 0.7), "CONTORNO", lw=50)
    t(msp, "bomba", P(cb["x"], cb["y"]), 1.5, "MIDDLE_CENTER")

    # ---- garita, portón y pilar
    g = G["garita"]
    relleno_rect(msp, *P(g["x0"], g["y0"]), *P(g["x1"], g["y1"]), ANEXO)
    rect(msp, *P(g["x0"], g["y0"]), *P(g["x1"], g["y1"]), "CONTORNO", lw=50)
    linea(msp, P(g["x1"] + 0.1, -33.9), P(g["x1"] + 0.1, -32.0), "CONTORNO", lw=100)
    pz = G["porton_predio"]
    linea(msp, P(pz["x0"] - 10.3, pz["y"] + 0.1), P(pz["x0"] - 0.1, pz["y"] + 0.1), "CONTORNO", lw=140)
    for xx in (pz["x0"], pz["x1"]):
        c = P(xx, pz["y"])
        relleno_rect(msp, c[0] - 0.6, c[1] - 0.6, c[0] + 0.6, c[1] + 0.6, (60, 60, 60))
    pa = G["pilar_acometida"]
    relleno_rect(msp, *P(pa["x"] - 0.6, pa["y"] - 0.35), *P(pa["x"] + 0.6, pa["y"] + 0.35), (90, 90, 90))
    t(msp, "pilar de acometida (medidor + NH00 160 A, pl. 05)", (P(pa["x"], 0)[0] + 2.6, P(0, pa["y"])[1]), 1.7, "MIDDLE_LEFT")

    # ---- cruce peatonal y senda
    poli(msp, PL(G["senda"]), "COTAS", color=R_SECO, lw=35)
    for i in range(8):
        y0 = -6.15 - i * 1.08
        relleno_rect(msp, *P(-1.35, y0 - 0.45), *P(0.8, y0), (255, 255, 255))
        rect(msp, *P(-1.35, y0 - 0.45), *P(0.8, y0), "CONTORNO", lw=35)
    t(msp, "senda peatonal", P(4.5, -2.2), 1.7, "MIDDLE_CENTER")
    t(msp, "estacionamiento", P(17.25, -7.7), 1.7, "MIDDLE_CENTER")
    # livianos
    linea(msp, P(0.5, -34.8), P(0.5, -36.0), "CONTORNO", lw=35)
    linea(msp, P(0.5, -34.8), P(-3.75, -34.8), "CONTORNO", lw=35)
    punta(msp, P(-3.75, -34.8), math.pi, (0, 0, 0), 1.4)
    t(msp, "livianos", P(2.3, -34.0), 1.6, "MIDDLE_CENTER")
    # semáforos de la báscula
    for xx, yy in ((3.4, -16.5), (8.1, -33.7)):
        relleno_circulo(msp, P(xx, yy), 0.8, R_GUANO)
        circulo(msp, P(xx, yy), 0.8, "CONTORNO", lw=35)

    # ---- recorridos de camiones (eje trasero)
    # A - guano húmedo
    a_ida = empalme([(XMIN, -44.8), (6.2, -44.8), (6.2, -8.4), (-10.3, -8.4), (-10.3, 21.0)], [6, 4.6, 4.3])
    recorrido(msp, a_ida, R_GUANO, desde=10)
    c_atras = (-3.8, 21.0)
    a_atras = arco_pts(c_atras, 6.5, 180, 270) + [(-2.2, 14.5)]
    recorrido(msp, a_atras, R_GUANO, cada=40, tipo="ATRAS", desde=4)
    a_vuelta = empalme([(-2.2, 14.9), (-14.6, 14.9), (-14.6, -12.8), (5.3, -12.8), (5.3, -44.8), (XMAX, -44.8)],
                       [9.5, 3.5, 3.8, 6])
    recorrido(msp, a_vuelta, R_GUANO, desde=12)
    # B - producto seco
    b_ida = empalme([(XMAX, -39.8), (6.8, -39.8), (6.8, -13.4), (37.5, -13.4)], [4, 4])
    recorrido(msp, b_ida, R_SECO, desde=12)
    b_atras = arco_pts((36.0, -6.4), 6.0, 270, 180) + [(30.0, -2.65)]
    recorrido(msp, b_atras, R_SECO, cada=40, tipo="ATRAS", desde=4)
    b_vuelta = empalme([(30.0, -7.0), (30.0, -9.9), (20.0, -9.9), (14.0, -8.2), (4.7, -8.2), (4.7, -45.4), (XMAX, -45.4)],
                       [2.5, 0, 0, 4, 6])
    recorrido(msp, b_vuelta, R_SECO, desde=8)
    # C - cáscara de arroz
    c_rec = empalme([(XMIN, -46.1), (7.4, -46.1), (7.4, -14.0), (43.9, -14.0), (43.9, 8.2), (40.35, 16.4),
                     (40.35, 35.8), (-16.0, 35.8), (-16.0, -14.0), (4.1, -14.0), (4.1, -46.1), (XMAX, -46.1)],
                    [6, 4, 8.3, 0, 0, 8, 10, 4, 3.6, 6])
    recorrido(msp, c_rec, R_CASC, cada=24, desde=14)

    # ---- envolventes de barrido de las dos maniobras en marcha atrás
    ang = lambda pts: (lambda i: math.degrees(math.atan2(
        pts[max(i - 1, 0)][1] - pts[min(i + 1, len(pts) - 1)][1],
        pts[max(i - 1, 0)][0] - pts[min(i + 1, len(pts) - 1)][0])))
    ea = arco_pts(c_atras, 6.5, 180, 270, 12)
    envolvente(msp, ea, ang(ea))
    eb = arco_pts((36.0, -6.4), 6.0, 270, 180, 12)
    envolvente(msp, eb, ang(eb))
    # radios de giro
    for c, r, a_ in ((c_atras, 6.5, 205), ((36.0, -6.4), 6.0, 215)):
        p1 = (c[0] + r * math.cos(math.radians(a_)), c[1] + r * math.sin(math.radians(a_)))
        linea(msp, P(*c), P(*p1), "CONTORNO", lw=35)
        punta(msp, P(*p1), math.radians(a_), (0, 0, 0), 1.6)
        relleno_circulo(msp, P(*c), 0.45, (0, 0, 0))
        m = ((c[0] + p1[0]) / 2, (c[1] + p1[1]) / 2)
        t(msp, f"R {r:.1f} m".replace(".", ","), (P(*m)[0] + 0.3, P(*m)[1] + 1.0), 1.7, "BOTTOM_CENTER",
          rotacion=a_ - 180)

    # ---- camiones
    camion(msp, (-2.2, 14.6), 180, chevrones=True)                 # descargando en P1 (A5)
    camion(msp, (5.75, -19.4), 90, chevrones=True)                 # en la báscula
    camion(msp, (30.05, -8.2), 270, color_caja=(245, 252, 245))    # cargando en P2
    camion(msp, (38.8, 25.1), 90)                                  # descargando cáscara en PL3

    # ---- cerco, árboles y alumbrado
    rect(msp, *P(pr["x0"], pr["y0"]), *P(pr["x1"], pr["y1"]), "CONTORNO", lw=70)
    marcas = []
    for x in range(-18, 50, 4):
        marcas.append((x, pr["y1"]))
        if not (-12 <= x <= 12):
            marcas.append((x + 0.0, pr["y0"]))
    for y in range(36, -36, -4):
        marcas += [(pr["x0"], y), (pr["x1"], y)]
    for x in (-9.4, -5.4):       # cerco detrás del portón abierto
        marcas.append((x, pr["y0"]))
    arboles = G["arboles"]
    for mx, my in marcas:
        if any(math.hypot(mx - ax, my - ay) < ar + 0.3 for ax, ay, ar in arboles):
            continue
        cruz(msp, P(mx, my))
    for ax, ay, ar in arboles:
        arbol(msp, ax, ay, ar)
    for fx, fy in G["farolas"]:
        farola(msp, fx, fy)
    t(msp, "cerco olímpico h 2,0 m", (P(-8.5, 0)[0], P(0, pr["y1"])[1] + 3.0), 1.8, "MIDDLE_CENTER")

    # ---- nombres de calles y textos
    tn(msp, "CALLE NORTE (R5)", P(12.0, 32.5), 2.4, "MIDDLE_CENTER")
    tn(msp, "CALLE SUR (R2)", P(21.0, -10.5), 2.4, "MIDDLE_CENTER")
    tn(msp, "CALLE OESTE (R3)", P(-12.6, 1.5), 2.4, "MIDDLE_CENTER", rotacion=90)
    tn(msp, "CALLE ESTE (R4)", P(40.6, 4.0), 2.4, "MIDDLE_CENTER", rotacion=90)
    tn(msp, "ACCESO (R1)", P(2.2, -26.0), 2.2, "MIDDLE_CENTER", rotacion=90)
    t(msp, "báscula", P(8.2, -20.7), 1.8, "MIDDLE_LEFT")
    tn(msp, "PORTÓN CORREDIZO 10 m", P(-12.6, -37.6), 1.8, "MIDDLE_CENTER")
    tn(msp, "INGRESO Y EGRESO DE CAMIONES", P(22.0, -37.6), 1.8, "MIDDLE_CENTER")
    t(msp, "vereda", P(40.0, -37.6), 1.8, "MIDDLE_CENTER")
    tn(msp, "CALLE PÚBLICA DE ACCESO", P(31.0, -41.2), 2.6, "MIDDLE_CENTER")
    t(msp, "banquina", P(31.0, -46.75), 1.6, "MIDDLE_CENTER")

    # ---- referencias (globos) y puestos de trabajo
    globo_b(msp, "27", (33.2, 149.7), (39.4, 152.4))
    globo_b(msp, "32", (49.7, 142.1), P(-11.6, -2.9))
    globo_b(msp, "33", (89.5, 253.5), P(-0.6, pr["y1"]), r=2.7)
    globo_b(msp, "31", (62.3, 70.9), P(-6.6, -33.0))
    globo_b(msp, "30", (117.1, 69.0), P(5.6, -30.4))
    globo_b(msp, "34", (115.9, 151.7), P(12.4, -2.8))
    for txt, c in (("A1", (115.2, 81.0)), ("A2", (73.3, 138.7)), ("A3", (74.3, 217.7)), ("A4", (85.2, 205.3)),
                   ("A5", (109.6, 190.2)), ("A6", (81.9, 105.2))):
        globo_a(msp, txt, c)
    puesto(msp, 2, (83.5, 179.7))
    puesto(msp, 5, (178.0, 193.3))
    puesto(msp, 6, (174.6, 154.1))
    puesto(msp, 7, P(-5.75, -32.75), 2.0)

    # ---- cotas
    cota(msp, P(pr["x0"], pr["y1"]), P(pr["x1"], pr["y1"]), distancia=7.5, escala=K)
    cota(msp, P(pr["x0"], pr["y1"]), P(pr["x0"], pr["y0"]), distancia=-8.6, escala=K)
    cota(msp, P(37.0, 14.0), P(44.0, 14.0), distancia=0.01, escala=K)
    cota(msp, P(XMAX, calle["y1"]), P(XMAX, calle["y0"]), distancia=-1.5, escala=K)


# ---------------------------------------------------------------- cuadros de la derecha

def panel(msp):
    X = 228.0
    subtitulo(msp, "REFERENCIAS", X, 271.6, 2.9)
    refs = [("30", "Báscula para camiones 40 t (16 x 3 m), usada al entrar y al salir"),
            ("31", "Garita de control y balanza (portería)"),
            ("32", "Calles de 7 m, sobreanchos y playones de hormigón (PL1 a PL3)"),
            ("33", "Cerco perimetral y portón corredizo de 10 m"),
            ("34", "Estacionamiento del personal (4 autos)"),
            ("27", "Tanque de agua contra incendio y casilla de bomba"),
            ("13", "Silo de cáscara - 18 ciclón - 19 lavador - 21 tanque de solución")]
    for i, (n, txt) in enumerate(refs):
        y = 268.0 - i * 4.4
        circulo(msp, (X + 2.3, y), 1.95, "CONTORNO", lw=50)
        tn(msp, n, (X + 2.3, y), 1.6, "MIDDLE_CENTER")
        t(msp, txt, (X + 5.8, y), 2.1, "MIDDLE_LEFT")

    subtitulo(msp, "CIRCUITOS DE CAMIONES", X, 234.0, 2.9)
    filas = [["", "Carga", "Frecuencia", "Recorrido", "Tiempo"],
             ["A", "Guano húmedo", "1 por día, ≈ 8 t", "pesa - calles Sur y Oeste - marcha atrás a P1 - vuelca - pesa y sale", "≈ 25 min"],
             ["B", "Producto seco", "1 c/ 4 días, ≈ 11 t", "pesa - calle Sur - marcha atrás a P2 - carga con minicargadora - pesa", "≈ 60 min"],
             ["C", "Cáscara de arroz", "1 c/ 3 días, ≈ 8 t", "pesa - calle Este - dársena PL3 - descarga neumática al silo - pesa", "≈ 45 min"]]
    y = tabla(msp, X, 231.5, [9, 25, 29, 95.8, 18.9], filas, h_fila=4.3, altura=2.0,
              alin=["R", "L", "L", "L", "C"], sombras={2: (245, 245, 245)})
    for i, col in enumerate((R_GUANO, R_SECO, R_CASC)):
        yy = 231.5 - (i + 1.5) * 4.3
        relleno_rect(msp, X + 1.0, yy - 1.0, X + 4.2, yy + 1.0, col)
    # simbología
    ly1, ly2 = y - 3.0, y - 6.6
    for x0, txt, col, tipo in ((X, "marcha adelante", R_GUANO, None), (X + 52, "marcha atrás", R_GUANO, "DASHED"),
                               (X + 89, "envolvente de barrido (camión 7,6 m)", ENVOLV, None)):
        e = poli(msp, [(x0, ly1), (x0 + 8, ly1)], "COTAS", color=col, lw=50, tipo=tipo)
        if tipo:
            e.dxf.ltscale = 2.0
        t(msp, txt, (x0 + 10, ly1), 1.9, "MIDDLE_LEFT")
    poli(msp, [(X, ly2), (X + 8, ly2)], "COTAS", color=R_SECO, lw=50)
    t(msp, "senda peatonal demarcada", (X + 10, ly2), 1.9, "MIDDLE_LEFT")
    c = (X + 49.0, ly2)
    poli(msp, [(c[0], c[1] + 1.6), (c[0] + 1.6, c[1]), (c[0], c[1] - 1.6), (c[0] - 1.6, c[1])], "CONTORNO", cerrada=True, lw=50)
    t(msp, "puesto de trabajo", (X + 51.5, ly2), 1.9, "MIDDLE_LEFT")
    cf = (X + 92.5, ly2)
    circulo(msp, cf, 1.15, "CONTORNO", lw=35)
    linea(msp, (cf[0] - 1.8, cf[1]), (cf[0] + 1.8, cf[1]), "CONTORNO", lw=35)
    linea(msp, (cf[0], cf[1] - 1.8), (cf[0], cf[1] + 1.8), "CONTORNO", lw=35)
    t(msp, "alumbrado LED", (X + 96, ly2), 1.9, "MIDDLE_LEFT")
    relleno_circulo(msp, (X + 118.5, ly2), 1.7, ARBOL)
    circulo(msp, (X + 118.5, ly2), 1.7, "CONTORNO", lw=50)
    t(msp, "cortina forestal", (X + 121.5, ly2), 1.9, "MIDDLE_LEFT")

    subtitulo(msp, "SECUENCIA DEL CAMIÓN DE GUANO", X, 201.6, 2.9)
    seq = ["A1  Ingresa, se pesa (bruto) y la garita le da paso con el semáforo.",
           "A2  Circula por la calle Sur y la calle Oeste a 10 km/h como máximo.",
           "A3  Se detiene pasando el portón P1; el señalero (2) dirige la maniobra.",
           "A4  Entra marcha atrás en curva (R 6,5 m al eje trasero) hasta el tope.",
           "A5  Vuelca la caja a 50° sobre la pila, la baja y sale hacia adelante.",
           "A6  Vuelve por las calles Oeste y Sur, se pesa (tara) y sale al Este."]
    for i, s in enumerate(seq):
        t(msp, s, (X + 1.0, 198.1 - i * 3.4), 2.0, "MIDDLE_LEFT")

    subtitulo(msp, "CUADRO DE SUPERFICIES", X, 174.9, 2.9)
    filas = [["Destino", "m²", "%"],
             ["Nave de proceso (33,0 x 18,0 m)", "594", "10,9"],
             ["Anexo del generador y garita", "64", "1,2"],
             ["Calles, sobreanchos, playones, báscula y estacionamiento", "1.970", "36,0"],
             ["Verde y cortina forestal", "2.844", "52,0"],
             ["PREDIO (72 x 76 m)", "5.472", "100,0"]]
    tabla(msp, X, 172.5, [107.8, 34.2, 35.7], filas, h_fila=3.9, altura=2.0, alin=["L", "R", "R"],
          negrita_ultima=True)

    subtitulo(msp, "NOTAS", X, 143.9, 2.9)
    notas(msp, ["1. Recorridos dibujados por el eje trasero del camión rígido de 2 ejes (7,6 x 2,5 m; entre ejes 4,2 m).",
                "2. Los sobreanchos del pavimento cubren la envolvente de barrido de todas las maniobras (+0,30 m).",
                "3. Calles de 7,0 m, doble mano, por la derecha, 10 km/h. Báscula de un carril con semáforos (garita).",
                "4. Circuito sucio (guano húmedo, lado Oeste) separado del limpio (producto seco, lados Sur y Este).",
                "5. Coordenadas en m con origen en el vértice Sudoeste de la nave (planos 01 y 08)."],
          X + 1.0, 141.3, altura=1.85, interlineado=1.6)


def perfil(msp):
    """Perfil transversal tipo de calle: H 1:100, V 1:25."""
    X = 228.0
    titulo(msp, "PERFIL TRANSVERSAL TIPO DE CALLE", X, 122.0, 3.0)
    t(msp, "ESC. H 1:100 - V 1:25", (X, 119.0), 1.8, "TOP_LEFT")
    kh, kv = 0.01, 0.04                 # mm reales -> papel
    xc, dy = 287.8, 3.0
    s = 3500 * kh                       # semiancho de calzada
    yc = 104.0 + dy                     # coronamiento
    ye = yc - 3500 * 0.02 * kv          # borde (2 %)
    los = 180 * kv
    bas = 200 * kv
    ext = 38.2                          # base granular sobresale
    # subrasante
    yb_c, yb_e = yc - los - bas, ye - los - bas
    sub = [(X + 9.7, yb_e - 6.0), (X + 110.3, yb_e - 6.0), (X + 110.3, yb_e), (xc + ext, yb_e), (xc, yb_c),
           (xc - ext, yb_e), (X + 9.7, yb_e)]
    rayado(msp, sub, escala=1.1, capa="CONTORNO", color=(0, 0, 0))
    linea(msp, (X + 9.7, yb_e - 6.0), (X + 110.3, yb_e - 6.0), "CONTORNO", lw=70)
    # base granular (con puntos)
    base = [(xc - ext, ye - los), (xc - s, ye - los), (xc, yc - los), (xc + s, ye - los), (xc + ext, ye - los),
            (xc + ext, yb_e), (xc, yb_c), (xc - ext, yb_e)]
    relleno(msp, base, (255, 255, 255))
    import random
    rnd = random.Random(11)
    for _ in range(170):
        x = rnd.uniform(xc - ext + 0.6, xc + ext - 0.6)
        f = abs(x - xc) / s if abs(x - xc) < s else 1.0
        ytop = (yc - los) - (yc - ye) * f
        ybot = yb_c - (yb_c - yb_e) * min(abs(x - xc) / ext, 1.0)
        y = rnd.uniform(ybot + 0.5, ytop - 0.5)
        relleno_circulo(msp, (x, y), 0.17, (80, 80, 80))
    poli(msp, base, "CONTORNO", cerrada=True, lw=50)
    # losa
    losa = [(xc - s, ye), (xc, yc), (xc + s, ye), (xc + s, ye - los), (xc, yc - los), (xc - s, ye - los)]
    relleno(msp, losa, (204, 206, 200))
    poli(msp, losa, "CONTORNO", cerrada=True, lw=50)
    linea(msp, (xc, yc), (xc, yb_c), "COTAS", color=R_CASC, lw=35)
    # cordones y cunetas
    hc = ye + 150 * kv
    for sg in (-1, 1):
        x0, x1 = xc + sg * s, xc + sg * (s + 1.5)
        relleno(msp, [(x0, ye - los), (x1, ye - los), (x1, hc), (x0, hc)], (150, 150, 150))
        poli(msp, [(x0, ye - los), (x1, ye - los), (x1, hc), (x0, hc)], "CONTORNO", cerrada=True, lw=50)
        poli(msp, [(x1, hc - 1.0), (xc + sg * (s + 7.6), hc - 3.8), (xc + sg * (s + 10.8), hc - 12.3),
                   (xc + sg * (s + 14.6), hc - 3.2)], "CONTORNO", lw=50)
    # pendientes
    for sg in (-1, 1):
        t(msp, "2 %", (xc + sg * 18.7, yc + 3.3), 1.8, "BOTTOM_CENTER")
        a, b = (xc + sg * 11.6, yc + 1.2), (xc + sg * 26.0, yc + 0.0)
        linea(msp, a, b, "CONTORNO", lw=35)
        punta(msp, b, math.atan2(b[1] - a[1], b[0] - a[0]), (0, 0, 0), 1.6)
    # cotas
    cota(msp, (xc - s, hc), (xc, hc), distancia=4.3, escala=kh)
    cota(msp, (xc, hc), (xc + s, hc), distancia=4.3, escala=kh)
    # referencias
    xt = X + 115.6
    for txt, p, y in (("cordón 15 cm y cuneta de césped", (xc + s + 9.2, hc - 5.6), hc + 0.3),
                      ("losa H-30, e = 18 cm (juntas c/ 4,5 m y central)", (xc + s - 5.0, ye - los / 2 + 0.2), ye - los / 2 + 0.2),
                      ("base granular, e = 20 cm (98 % P.T.)", (xc + s - 5.0, yb_e + bas / 2 + 0.4), yb_e + bas / 2 + 0.4),
                      ("subrasante compactada (95 % P.T.)", (xc + s + 8.0, yb_e - 3.3), yb_e - 3.3)):
        linea(msp, p, (xt - 3.0, y), "CONTORNO", lw=35)
        linea(msp, (xt - 3.0, y), (xt - 1.0, y), "CONTORNO", lw=70)
        relleno_circulo(msp, p, 0.55, (0, 0, 0))
        t(msp, txt, (xt, y), 1.9, "MIDDLE_LEFT")


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Lámina nueva (B1): predio, cerco, garita, báscula, calles, playones, maniobras"),
            ("C", "09/2026", "Norte separado del título; pilar con seccionador NH00 160 A (plano 05)"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    doc, msp, z = lamina(11, "IMPLANTACIÓN DEL PREDIO Y\nCIRCULACIÓN DE CAMIONES", "1:400", revs)
    titulo(msp, "IMPLANTACIÓN GENERAL DEL PREDIO Y CIRCULACIÓN DE VEHÍCULOS  -  ESC. 1:400", 28, 279.4, 3.4)
    if "ATRAS" not in doc.linetypes:   # trazos para la marcha atrás
        doc.linetypes.add("ATRAS", pattern=[2.3, 1.5, -0.8], description="Marcha atras __ __ __")
    planta(msp)
    escala_grafica(msp, 140, 265.6, "1:400", 20, 5)
    norte(msp, 212, 263.0, 5.0)
    panel(msp)
    perfil(msp)
    exportar_lamina(doc, 11)


if __name__ == "__main__":
    main()
