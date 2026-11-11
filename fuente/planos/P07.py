"""P07 - Tablero general (TGF): disposición y materiales, escala 1:10, Rev. D.

Redibujo vectorial de la lámina PNG Rev. C: A placa de montaje (puerta retirada), B puerta,
C lateral, lista de materiales y especificaciones. Gabinete 2000 x 1000 x 400 + zócalo 100.
Las placas de fabricante (B&S y CSE) son recortes raster del original (fuente/planos/img).
"""
import os

from lamina_secadora import (FECHA, circulo, cota, exportar_lamina, factor, imagen, lamina, linea,
                             notas, rayado, rect, relleno_circulo, relleno_rect, subtitulo, t,
                             titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
K = factor("1:10")
Y0 = 80.3                      # nivel del piso del gabinete (arriba del zócalo) en el papel
XA, XB, XC = 32.0, 150.0, 268.0

F_EQ = (245, 245, 245)
F_VFD = (228, 236, 245)
F_RL = (240, 238, 228)
F_PLC = (234, 243, 234)
F_BAT = (246, 238, 230)
F_CANAL = (225, 225, 225)
F_BARRA = (215, 190, 150)


def P(x0, rx, ry):
    return (x0 + rx * K, Y0 + ry * K)


def caja(msp, x0, rx0, ry0, rx1, ry1, fondo=None, capa="CONTORNO", lw=None):
    a, b = P(x0, rx0, ry0), P(x0, rx1, ry1)
    if fondo:
        relleno_rect(msp, a[0], a[1], b[0], b[1], fondo)
    rect(msp, a[0], a[1], b[0], b[1], capa, lw=lw)
    return a, b


def rotulo(msp, x0, rx0, ry0, rx1, ry1, l1, l2=None, h1=2.0, h2=1.6):
    cx, cy = P(x0, (rx0 + rx1) / 2, (ry0 + ry1) / 2)
    if l2:
        tn(msp, l1, (cx, cy + h1 * 0.7), h1, "MIDDLE_CENTER")
        t(msp, l2, (cx, cy - h2 * 0.9), h2, "MIDDLE_CENTER")
    else:
        tn(msp, l1, (cx, cy), h1, "MIDDLE_CENTER")


def riel(msp, x0, ry, rx0=20, rx1=960):
    linea(msp, P(x0, rx0, ry), P(x0, rx1, ry), lw=50)


def canal(msp, x0, ry0, ry1):
    caja(msp, x0, 30, ry0, 955, ry1, F_CANAL)
    t(msp, "canal 60x60", P(x0, 500, (ry0 + ry1) / 2), 1.6, "MIDDLE_CENTER")


def vista_a(msp):
    x0 = XA
    titulo_vista(msp, "A - PLACA DE MONTAJE (puerta retirada)  -  ESC. 1:10", 25, 282.4, 2.8)
    caja(msp, x0, 0, 0, 1000, 2000, lw=50)                      # gabinete
    caja(msp, x0, 30, 30, 970, 1970, lw=50)                     # placa de montaje
    # zócalo
    a, b = P(x0, 0, -100), P(x0, 1000, 0)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.6)
    rect(msp, a[0], a[1], b[0], b[1], lw=50)
    relleno_rect(msp, a[0] + 33, a[1] + 2.5, b[0] - 33, b[1] - 2.5, (255, 255, 255))
    t(msp, "zócalo 100", P(x0, 500, -50), 2.0, "MIDDLE_CENTER")
    # fila 1: QG, DPS, MM, TR, FA, QA, QTS, QL, QC
    riel(msp, x0, 1790)
    fila1 = [(49, 1690, 192, 1890, "QG", "4P 125 A"), (199, 1730, 272, 1850, "DPS", "T2"),
             (283, 1740, 382, 1837, "MM", "multimed."), (394, 1709, 525, 1851, "TR", "380/230"),
             (539, 1719, 631, 1845, "FA", "24 Vcc"), (645, 1726, 682, 1815, "QA", None),
             (694, 1726, 768, 1815, "QTS", None), (780, 1726, 854, 1815, "QL", None),
             (865, 1726, 938, 1815, "QC", None)]
    for rx0, ry0, rx1, ry1, n, d in fila1:
        caja(msp, x0, rx0, ry0, rx1, ry1, F_EQ)
        rotulo(msp, x0, rx0, ry0, rx1, ry1, n, d, h1=1.8 if n != "QA" else 1.4, h2=1.5)
    # barras con cubrebarras
    caja(msp, x0, 44, 1601, 956, 1665, F_BARRA)
    for ry in (1612, 1626, 1640, 1654):
        linea(msp, P(x0, 52, ry), P(x0, 948, ry), "FINO")
    caja(msp, x0, 260, 1620, 740, 1646, (255, 255, 255), "FINO")
    t(msp, "barras Cu 30x5 - L1 L2 L3 N (cubrebarras)", P(x0, 500, 1633), 1.6, "MIDDLE_CENTER")
    canal(msp, x0, 1529, 1591)
    # guardamotores
    riel(msp, x0, 1440)
    bordes = [49, 104, 159, 215, 259, 304, 349, 394, 439, 484, 529, 574, 619, 664, 709, 753]
    for i in range(15):
        caja(msp, x0, bordes[i], 1369, bordes[i + 1], 1511, F_EQ)
        tn(msp, f"Q{i + 1}", P(x0, (bordes[i] + bordes[i + 1]) / 2, 1440), 1.8, "MIDDLE_CENTER", rotacion=90)
    canal(msp, x0, 1295, 1356)
    # contactores, K0 y barra PE
    riel(msp, x0, 1210)
    kms = ["KM9", "KM10", "KM11", "KM13", "KM14", "KM15"]
    for i, n in enumerate(kms):
        a0 = 49 + 45.8 * i
        caja(msp, x0, a0, 1151, a0 + 45.8, 1271, F_EQ)
        tn(msp, n, P(x0, a0 + 22.9, 1210), 1.6, "MIDDLE_CENTER", rotacion=90)
    caja(msp, x0, 336, 1151, 382, 1271, F_EQ)
    tn(msp, "K0", P(x0, 359, 1235), 1.6, "MIDDLE_CENTER")
    t(msp, "RS", P(x0, 359, 1180), 1.4, "MIDDLE_CENTER")
    caja(msp, x0, 396, 1151, 506, 1271, F_EQ)
    tn(msp, "PE", P(x0, 451, 1235), 1.6, "MIDDLE_CENTER")
    t(msp, "barra PE", P(x0, 451, 1180), 1.4, "MIDDLE_CENTER")
    canal(msp, x0, 1071, 1130)
    # variadores grandes
    for rx0, ry0, rx1, n, d, f in ((49, 601, 251, "VFD1", "15 kW", F_VFD), (265, 601, 466, "VFD2", "15 kW", F_VFD),
                                   (480, 592, 711, "VFD3", "22 kW", F_VFD), (725, 762, 851, "VFD4", "4 kW", F_VFD),
                                   (865, 762, 956, "RL", "x4", F_RL)):
        caja(msp, x0, rx0, ry0, rx1, 1042, f)
        cy = (ry0 + 1042) / 2 if ry0 < 700 else 940
        tn(msp, n, P(x0, (rx0 + rx1) / 2, cy + 25), 1.8, "MIDDLE_CENTER")
        t(msp, d, P(x0, (rx0 + rx1) / 2, cy - 20), 1.6, "MIDDLE_CENTER")
    canal(msp, x0, 520, 580)
    # variadores chicos, PLC, switch y batería
    riel(msp, x0, 420)
    for (rx0, rx1), n in zip(((49, 123), (129, 201), (207, 280), (286, 357), (364, 437)),
                             ("VFD5", "VFD6", "VFD7", "VFD8", "VFD12")):
        caja(msp, x0, rx0, 325, rx1, 501, F_VFD)
        tn(msp, n, P(x0, (rx0 + rx1) / 2, 413), 1.4, "MIDDLE_CENTER")
    caja(msp, x0, 451, 362, 560, 460, F_PLC)
    rotulo(msp, x0, 451, 362, 560, 460, "CPU", "1214C", 1.6, 1.4)
    for (rx0, rx1), n in zip(((567, 610), (616, 658), (663, 704), (709, 751)), ("RTD", "AI", "DQ", "DI")):
        caja(msp, x0, rx0, 362, rx1, 460, F_PLC)
        tn(msp, n, P(x0, (rx0 + rx1) / 2, 411), 1.5, "MIDDLE_CENTER", rotacion=90)
    caja(msp, x0, 760, 362, 822, 460, F_EQ)
    rotulo(msp, x0, 760, 362, 822, 460, "SW", "PN", 1.5, 1.4)
    caja(msp, x0, 831, 340, 951, 481, F_BAT)
    rotulo(msp, x0, 831, 340, 951, 481, "BAT", "10 kVAr", 1.6, 1.4)
    canal(msp, x0, 261, 321)
    # relés de interfaz y borneras
    riel(msp, x0, 182)
    for (rx0, rx1, n) in ((49, 363, 24), (380, 953, 64)):
        caja(msp, x0, rx0, 130, rx1, 233)
        paso = (rx1 - rx0) / n
        for i in range(1, n):
            linea(msp, P(x0, rx0 + paso * i, 136), P(x0, rx0 + paso * i, 227), "FINO", lw=25 if n == 24 else 18)
    t(msp, "24 relés de interfaz 24 Vcc", P(x0, 206, 110), 1.6, "MIDDLE_CENTER")
    t(msp, "borneras X1 (fuerza) / X2 (señales)", P(x0, 666, 110), 1.6, "MIDDLE_CENTER")
    caja(msp, x0, 30, 41, 955, 93, (255, 255, 255))
    t(msp, "entrada de cables por el piso - prensacables", P(x0, 500, 67), 1.8, "MIDDLE_CENTER")
    # cotas
    cota(msp, P(x0, 0, -100), P(x0, 0, 2000), distancia=7.0, escala=K)
    cota(msp, P(x0, 1000, 0), P(x0, 1000, 2000), distancia=-6.0, escala=K)
    cota(msp, P(x0, 0, -100), P(x0, 1000, -100), distancia=-6.0, escala=K)


def vista_b(doc, msp):
    x0 = XB
    titulo_vista(msp, "B - PUERTA  -  ESC. 1:10", x0, 282.4, 2.8)
    caja(msp, x0, 0, 0, 1000, 2000, lw=50)
    caja(msp, x0, 20, 20, 980, 1980, lw=50)
    # placa de características
    caja(msp, x0, 225, 1858, 775, 1949, (238, 236, 230))
    tn(msp, "TGF - TABLERO GENERAL DE FUERZA", P(x0, 500, 1922), 1.6, "MIDDLE_CENTER")
    t(msp, "3 x 380/220 V - 50 Hz - Icc 6 kA - IP54 - IEC 61439", P(x0, 500, 1884), 1.4, "MIDDLE_CENTER")
    # manija del QG
    caja(msp, x0, 79, 1713, 162, 1863, (232, 195, 90))
    c = P(x0, 121, 1784)
    circulo(msp, c, 2.7, lw=50)
    relleno_rect(msp, c[0] - 0.75, c[1], c[0] + 0.75, c[1] + 5.0, (40, 40, 40))
    linea(msp, P(x0, 121, 1840), P(x0, 121, 1850), "FINO")
    tn(msp, "QG 125 A", P(x0, 121, 1693), 1.6, "MIDDLE_CENTER")
    # HMI
    a, b = caja(msp, x0, 393, 1418, 607, 1576, (50, 55, 62))
    relleno_rect(msp, a[0] + 1.8, a[1] + 1.8, b[0] - 1.8, b[1] - 1.8, (122, 152, 178))
    tn(msp, 'HMI 7"', P(x0, 500, 1497), 2.0, "MIDDLE_CENTER")
    t(msp, "KTP700 (214 x 158)", P(x0, 500, 1392), 1.7, "MIDDLE_CENTER")
    # luces piloto
    t(msp, "luces piloto Ø22", P(x0, 500, 1328), 1.7, "MIDDLE_CENTER")
    pil = [("RED", (90, 90, 90)), ("EXTR.", (90, 90, 90)), ("VENT.", (90, 90, 90)), ("HOGAR", (90, 90, 90)),
           ("CINTAS", (90, 90, 90)), ("DOSIF.", (90, 90, 90)), ("ALARMA", (232, 195, 90)), ("FALLA", (220, 0, 0))]
    for i, (n, col) in enumerate(pil):
        rx = 151 + 100 * i
        c = P(x0, rx, 1278)
        relleno_circulo(msp, c, 1.7, col)
        circulo(msp, c, 1.7, lw=50)
        caja(msp, x0, rx - 43, 1227, rx + 43, 1251, (255, 255, 255))
        t(msp, n, P(x0, rx, 1239), 1.4, "MIDDLE_CENTER")
    # selectores
    t(msp, "selectores y pulsadores Ø22", P(x0, 500, 1148), 1.7, "MIDDLE_CENTER")
    sel = ["A-0-M", "CINTAS", "DOSIF.", "HOGAR", "VENT.", "SINF.", "BOMBA", "ELEV."]
    for i, n in enumerate(sel):
        rx = 151 + 100 * i
        c = P(x0, rx, 1099)
        circulo(msp, c, 1.7, lw=50)
        linea(msp, (c[0] - 1.5, c[1]), (c[0] + 1.5, c[1]), lw=50)
        caja(msp, x0, rx - 43, 1047, rx + 43, 1071, (255, 255, 255))
        t(msp, n, P(x0, rx, 1059), 1.4, "MIDDLE_CENTER")
    # pulsadores
    for rx, n, col in ((301, "MARCHA", (80, 80, 80)), (411, "PARADA", (220, 0, 0)), (521, "RESET", (120, 150, 180))):
        c = P(x0, rx, 928)
        relleno_circulo(msp, c, 1.6, col)
        circulo(msp, c, 1.6, lw=50)
        t(msp, n, P(x0, rx, 887), 1.5, "MIDDLE_CENTER")
    # hongo de emergencia
    c = P(x0, 721, 928)
    relleno_circulo(msp, c, 5.0, (232, 195, 90))
    circulo(msp, c, 5.0, lw=50)
    circulo(msp, c, 3.6, lw=35)
    relleno_circulo(msp, c, 2.6, (220, 0, 0))
    circulo(msp, c, 2.6, "FINO")
    tn(msp, "PARADA DE\nEMERGENCIA", P(x0, 721, 868), 1.6, "TOP_CENTER")
    # cerradura
    circulo(msp, P(x0, 961, 899), 1.2, lw=50)
    t(msp, "cerradura", P(x0, 919, 852), 1.5, "MIDDLE_CENTER")
    # cartel de riesgo
    caja(msp, x0, 299, 318, 702, 460, (253, 235, 150))
    tn(msp, "RIESGO ELÉCTRICO - 380 V", P(x0, 500, 403), 2.0, "MIDDLE_CENTER")
    t(msp, "TGF - IRAM 10005", P(x0, 500, 368), 1.7, "MIDDLE_CENTER")
    # ventilación y placas del fabricante
    t(msp, "placas del fabricante", P(x0, 500, 273), 1.5, "MIDDLE_CENTER")
    t(msp, "ventilador + filtro (2 x 230 m³/h)", P(x0, 205, 253), 1.5, "MIDDLE_CENTER")
    t(msp, "rejilla de salida", P(x0, 848, 253), 1.5, "MIDDLE_CENTER")
    for rx0 in (81, 771):
        caja(msp, x0, rx0, 79, rx0 + 152, 229, lw=50)
        for j in range(7):
            ry = 98 + 19 * j
            linea(msp, P(x0, rx0 + 10, ry), P(x0, rx0 + 142, ry), lw=50)
    lado = 15.0
    for rx0, arch in ((262, "P07_logo_BS.png"), (589, "P07_logo_CSE.png")):
        a = P(x0, rx0, 79)
        imagen(doc, msp, os.path.join(AQUI, "img", arch), a[0], a[1], lado, lado)
        rect(msp, a[0] - 0.3, a[1] - 0.3, a[0] + lado + 0.3, a[1] + lado + 0.3, lw=50)


def vista_c(msp):
    x0 = XC
    titulo_vista(msp, "C - LATERAL  -  ESC. 1:10", 256, 282.4, 2.8)
    caja(msp, x0, 0, 0, 400, 2000, lw=50)
    # piso del gabinete
    a, b = P(x0, 0, 0), P(x0, 400, 12)
    rayado(msp, [a, (b[0], a[1]), b, (a[0], b[1])], escala=0.25)
    # placa de montaje (3 mm) y equipos (profundidad)
    linea(msp, P(x0, 42, 28), P(x0, 42, 1971), lw=70)
    t(msp, "placa 3 mm", P(x0, 46, 1985), 1.4, "MIDDLE_LEFT")
    for ry0, ry1, prof in ((1689, 1887, 136), (1369, 1509, 156), (1149, 1269, 166), (589, 1039, 275),
                           (319, 501, 221), (131, 231, 120)):
        caja(msp, x0, 42, ry0, prof, ry1)
    # puerta y elementos montados en ella
    caja(msp, x0, 400, 20, 421, 1980)
    caja(msp, x0, 421, 1713, 449, 1863)          # manija del QG
    caja(msp, x0, 379, 1418, 400, 1576)          # HMI
    caja(msp, x0, 421, 878, 470, 978)            # hongo de emergencia
    caja(msp, x0, 361, 79, 400, 229)             # ventilador con filtro
    t(msp, "prof. 400", P(x0, 200, 70), 1.5, "MIDDLE_CENTER")


MATERIALES = [
    ["It.", "Cant.", "Descripción", "Obs."],
    ["1", "1", "Gabinete autoportante IP54 2000x1000x400 + zócalo 100", "chapa 2 mm, RAL 7032"],
    ["2", "1", "Interruptor automático QG 4P 125 A, Icu 25 kA", "bobina de mínima + manija"],
    ["3", "1", "Descargador de sobretensión T2 4P", "In 20 kA"],
    ["4", "1", "Multimedidor + 3 TI 150/5 A", "V, A, kW, cos φ, THD"],
    ["5", "15", "Guardamotores (Q1 a Q15)", "rangos según plano 05"],
    ["6", "6", "Contactores AC-3 9-12 A (KM9-15)", "bobina 24 Vcc"],
    ["7", "2+1+1", "VFD 15 kW / 22 kW / 4 kW + filtro EMC", "con STO"],
    ["8", "5", "VFD 0,75-1,5 kW (M5-M8, M12)", "con STO"],
    ["9", "4", "Reactancias de línea 3 % (VFD1 a VFD4)", ""],
    ["10", "1", "PLC S7-1200 CPU 1214C + 4 módulos", "RTD, AI, DQ16, DI16"],
    ["11", "1", "HMI KTP700 Basic + switch Profinet", ""],
    ["12", "1", "Relé de seguridad cat. 3 (K0)", "EN ISO 13849"],
    ["13", "1", "Transformador 380/230 V 500 VA + fuente 24 Vcc 10 A", ""],
    ["14", "1", "Batería 10 kVAr (2x5) con reactancia p = 7 %", "regulador 2 pasos"],
    ["15", "24", "Relés de interfaz 24 Vcc con base", ""],
    ["16", "1", "Barras Cu 30x5 160 A + cubrebarras + barra PE", ""],
    ["17", "gl.", "Borneras, canales 60x60, riel DIN, cableado", "numerado"],
    ["18", "2+2", "Ventiladores con filtro 230 m³/h + rejillas", "termostato"],
    ["19", "8+8+3", "Pilotos LED, selectores y pulsadores Ø22 con rótulos", "24 Vcc"],
    ["20", "1", "Hongo de parada de emergencia Ø40 con disco amarillo", "enclavable, NC doble"],
    ["21", "1", "Manija rotativa del QG en la puerta", "bloqueo con candado"],
    ["22", "1+2", "Placa de características IEC 61439 + placas del fabricante", "B&S / CSE"],
]


def tabla_ajustada(msp, x, y, anchos, filas, h_fila=4.0, altura=2.0, alin=None, sombras=None, negrita_ultima=False):
    """Como tabla() de la biblioteca, pero achica cada texto con un ancho de letra más real (Arial)."""
    alin = alin or ["L"] * len(anchos)
    xs = [x]
    for w in anchos:
        xs.append(xs[-1] + w)
    sombras = dict(sombras or {})
    sombras.setdefault(0, (226, 232, 238))
    for i, rgb in sombras.items():
        yy = y - (i + 1) * h_fila
        relleno_rect(msp, x, yy, xs[-1], yy + h_fila, rgb)
    for i, fila in enumerate(filas):
        yy = y - (i + 1) * h_fila
        rect(msp, x, yy, xs[-1], yy + h_fila, "FINO")
        neg = i == 0 or (negrita_ultima and i == len(filas) - 1)
        for j, val in enumerate(fila):
            if not val:
                continue
            ca, cb = xs[j], xs[j + 1]
            fa = 0.80 if neg else 0.72          # ancho medio de letra / altura (Arial, medido en el PDF)
            hh = min(altura, (cb - ca - 1.6) / (fa * len(val)))
            if hh < 1.5 and " " in val and h_fila >= 4.6:
                # en dos renglones, cortando en el espacio más cercano a la mitad
                cortes = [k for k, ch in enumerate(val) if ch == " "]
                k = min(cortes, key=lambda k: abs(k - len(val) / 2))
                val = val[:k] + "\n" + val[k + 1:]
                largo = max(len(r) for r in val.split("\n"))
                hh = min(altura, (cb - ca - 1.6) / (fa * largo), 1.5)
            hh = max(1.3, hh)
            if alin[j] == "C":
                pos, al = ((ca + cb) / 2, yy + h_fila / 2), "MIDDLE_CENTER"
            elif alin[j] == "R":
                pos, al = (cb - 0.8, yy + h_fila / 2), "MIDDLE_RIGHT"
            else:
                pos, al = (ca + 0.8, yy + h_fila / 2), "MIDDLE_LEFT"
            t(msp, val, pos, hh, al, estilo="NEGRITA" if neg else None)
    for c in xs[1:-1]:
        linea(msp, (c, y), (c, y - len(filas) * h_fila), "FINO")
    rect(msp, x, y - len(filas) * h_fila, xs[-1], y, "CONTORNO")
    return y - len(filas) * h_fila


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Equipos dentro del gabinete; HMI tamaño real (KTP700); VFD a escala; materiales"),
            ("C", "09/2026", "Manija QG frente al QG; placa de caract.; hongo c/disco amarillo; placas B&S/CSE"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(7, "TABLERO GENERAL (TGF) - DISPOSICIÓN Y MATERIALES" + " " * 10, "1:10", revs)
    assert Y0 > z["reservado"][3], z["reservado"]
    vista_a(msp)
    vista_b(doc, msp)
    vista_c(msp)
    subtitulo(msp, "LISTA DE MATERIALES DEL TGF", 316.6, 272.0, 2.8)
    y = tabla_ajustada(msp, 316.6, 269.5, [6.0, 8.5, 51.5, 22.9], MATERIALES, h_fila=5.2, altura=1.6,
              alin=["C", "C", "L", "L"])
    notas(msp, ["- Pérdidas de los VFD ≈ 1,4 kW: ventilación forzada 460 m³/h con termostato.",
                "- Cableado: fuerza negro 1 kV, mando 24 V azul, N celeste, PE verde-amarillo.",
                "- Ensayos IEC 61439: continuidad PE, rigidez dieléctrica, funcional.",
                "- Ubicación: sala de control (22), con ventana al secador."],
          316.6, y - 6.0, altura=1.6, interlineado=1.75, titulo="ESPECIFICACIONES")
    exportar_lamina(doc, 7)


if __name__ == "__main__":
    main()
