"""P06 - Diagrama de proceso e instrumentación (P&ID simplificado) y balances, Rev. D.

Redibujo vectorial de la lámina PNG Rev. C: equipos numerados, corrientes en rombos,
instrumentos ISA (círculo = campo; círculo en cuadrado = función del PLC), señales punteadas,
tabla de corrientes, lazos de control, enclavamientos, leyenda y balances.
"""
import math

from lamina_secadora import (FECHA, circulo, exportar_lamina, flecha, flecha_poli, lamina,
                             linea, poli, rayado, rect, relleno, relleno_circulo, subtitulo, t, tabla, titulo_vista, tn)

C_PROD = (139, 90, 43)
C_FRIO = (31, 150, 200)
C_CAL = (214, 40, 40)
C_AGOT = (46, 139, 87)
C_HUMO = (110, 110, 110)
C_AGUA = (31, 150, 200)
NEGRO = (0, 0, 0)
LW = 50


def flujo(msp, pts, color, punta=True):
    if punta:
        flecha_poli(msp, pts, "CONTORNO", color, tam=2.0, lw=LW) if len(pts) > 2 else \
            flecha(msp, pts[0], pts[1], "CONTORNO", color, tam=2.0, lw=LW)
    else:
        poli(msp, pts, "CONTORNO", color=color, lw=LW)


def senal(msp, pts, trazo=2.0, hueco=1.2):
    """Señal 4-20 mA / red: línea de trazos dibujada como segmentos (se ve igual en DXF y PDF)."""
    resto, dibuja = trazo, True
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.dist(a, b)
        if L == 0:
            continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        s = 0.0
        while s < L - 1e-9:
            d = min(resto, L - s)
            if dibuja:
                linea(msp, (a[0] + ux * s, a[1] + uy * s), (a[0] + ux * (s + d), a[1] + uy * (s + d)), lw=35)
            s += d
            resto -= d
            if resto <= 1e-9:
                dibuja = not dibuja
                resto = trazo if dibuja else hueco


def rombo(msp, n, c, a=2.6):
    x, y = c
    pts = [(x - a * 1.15, y), (x, y + a * 0.85), (x + a * 1.15, y), (x, y - a * 0.85)]
    relleno(msp, pts, (255, 255, 255))
    poli(msp, pts, "CONTORNO", cerrada=True, lw=35)
    tn(msp, str(n), c, 2.0, "MIDDLE_CENTER")


def inst(msp, tag, num, c, r=3.4, plc=False):
    """Instrumento ISA: círculo (campo) o círculo en cuadrado con línea media (función del PLC)."""
    relleno_circulo(msp, c, r, (255, 255, 255))
    if plc:
        rect(msp, c[0] - r, c[1] - r, c[0] + r, c[1] + r, lw=35)
        linea(msp, (c[0] - r, c[1]), (c[0] + r, c[1]), lw=35)
    circulo(msp, c, r, lw=35)
    tn(msp, tag, (c[0], c[1] + 1.15), 1.8 if len(tag) <= 2 else 1.6, "MIDDLE_CENTER")
    t(msp, num, (c[0], c[1] - 1.35), 1.5 if len(num) <= 2 else 1.3, "MIDDLE_CENTER")


def mot(msp, etiqueta, c, r=2.3, lado="R", dentro=False):
    relleno_circulo(msp, c, r, (255, 255, 255))
    circulo(msp, c, r, lw=35)
    if dentro:
        t(msp, etiqueta, c, 1.6, "MIDDLE_CENTER")
    elif lado == "R":
        t(msp, etiqueta, (c[0] + r + 0.6, c[1]), 1.8, "MIDDLE_LEFT")
    elif lado == "B":
        t(msp, etiqueta, (c[0], c[1] - r - 0.8), 1.8, "TOP_CENTER")
    else:
        t(msp, etiqueta, (c[0] - r - 0.6, c[1]), 1.8, "MIDDLE_RIGHT")


def cinta(msp, x0, x1, y, r=1.5):
    """Cinta horizontal: dos tambores y los ramales."""
    linea(msp, (x0, y + r), (x1, y + r))
    linea(msp, (x0, y - r), (x1, y - r))
    for x in (x0, x1):
        relleno_circulo(msp, (x, y), r, (255, 255, 255))
        circulo(msp, (x, y), r)


CORR = [["N°", "Corriente", "Caudal", "T °C", "Observaciones"],
        ["1", "Guano húmedo", "1.000 kg/h", "18", "72 % b.h. (280 kg/h de sólido seco)"],
        ["2", "Aire caliente al secador", "26.600 kg a.s./h", "100", "Y = 7,8 g/kg - 28.400 m³/h (máx. 135 °C)"],
        ["3", "Aire agotado", "26.600 kg a.s./h", "33", "Y = 33,0 g/kg, HR 99 % (+671 kg/h de vapor)"],
        ["4", "Guano seco (producto)", "329 kg/h", "74", "15 % b.h. - retención 1 h ≥ 70 °C y enfriado < 40 °C"],
        ["5", "Cáscara de arroz", "219 kg/h", "amb.", "PCI 13,5 MJ/kg - 1,8 t/día (314 kg/h a 135 °C)"],
        ["6", "Humos del hogar", "1.590 kg/h", "850", "exceso de aire 40 % (2.280 kg/h a 135 °C)"],
        ["7", "Humos a chimenea", "1.590 kg/h", "200", "después del ciclón de cenizas"],
        ["8", "Aire ambiente", "26.600 kg a.s./h", "18", "60 % HR - filtros de bolsa"],
        ["9", "Cenizas", "40 kg/h", "< 100", "sílice amorfa - 320 kg/día"],
        ["10", "Gases tratados", "27.480 kg/h", "33", "saturado, Y = 33,0 g/kg; NH3 -90 %"],
        ["11", "Aire de combustión", "1.410 kg/h", "18", "primario 70 % / secundario 30 %"],
        ["12", "Agua de reposición", "≈ 0,06 m³/h", "18", "repone la purga: el escape llega casi saturado"],
        ["13", "Purga del lavador", "≈ 0,06 m³/h", "40", "sulfato de amonio -> venta como fertilizante"],
        ["14", "Polvo del ciclón", "≈ 5 kg/h", "60", "vuelve al producto"],
        ["15", "Lixiviados", "eventual", "amb.", "cámara estanca -> tolva (sin vertido)"],
        ["16", "Aire de enfriamiento", "900 m³/h", "25→45", "enfriador bajo la tolva de retención (M40) -> escape"]]

LAZOS = [["Lazo", "Variable / consigna", "Actúa sobre"],
         ["TIC-01", "T aire entrada: consigna 90-150 °C de MIC-01", "velocidad M12 (cáscara) y M4"],
         ["MIC-01", "humedad producto 15 % (PI, en cascada)", "consigna de TIC-01 (0,8 K/punto, Ti 45 min)"],
         ["PIC-01", "presión plenum 1.500 Pa", "velocidad ventiladores M1-M2"],
         ["AIC-01", "pH del lavador = 3", "bomba dosificadora de ácido"],
         ["FY-01", "cintas atadas al dosificador (capa 30 mm)", "velocidad cintas M5-M6-M7"]]


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Aire amb.->vent.->interc.; aire de comb. al hogar; lavador sin vertido; lazos"),
            ("C", "09/2026", "Potencia instalada en formato decimal (66,9 kW); señal TT-07 a la chimenea 15"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24"),
            ("E", "11/2026", "Lazo de humedad en cascada sobre TIC-01; corrientes del punto de trabajo real")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(6, "DIAGRAMA DE PROCESO E INSTRUMENTACIÓN\n(P&ID SIMPLIFICADO) Y BALANCES", "S/E", revs)
    titulo_vista(msp, "DIAGRAMA DE PROCESO E INSTRUMENTACIÓN - SECADO DE GUANO 8 t/día (1 turno de 8 h)", 25, 281.5, 3.4)

    # =============== 1 recepción, 26 cámara, 2 tolva, 3 cinta con tacos
    poli(msp, [(27.9, 236.1), (46.0, 236.1), (37.0, 248.1)], cerrada=True)
    tn(msp, "1", (37.0, 239.8), 2.4, "MIDDLE_CENTER")
    tn(msp, "RECEPCIÓN", (37.0, 232.2), 2.0, "MIDDLE_CENTER")
    flujo(msp, [(31.5, 230.4), (31.5, 221.2)], C_AGUA)                 # 15 lixiviados
    rombo(msp, 15, (26.5 + 0.8, 225.8))
    rect(msp, 27.9, 212.2, 42.0, 221.2)
    tn(msp, "26", (35.0, 218.2), 2.0, "MIDDLE_CENTER")
    t(msp, "cámara", (35.0, 214.6), 1.8, "MIDDLE_CENTER")
    flujo(msp, [(42.0, 216.6), (52.1, 216.6), (58.0, 237.6)], C_AGUA)
    flujo(msp, [(46.5, 243.0), (57.0, 243.0)], C_PROD)                  # 1 guano húmedo
    rombo(msp, 1, (51.5, 248.3))
    poli(msp, [(54.2, 252.3), (72.0, 252.3), (66.8, 238.2), (58.6, 238.2)], cerrada=True)
    tn(msp, "2", (63.2, 246.2), 2.4, "MIDDLE_CENTER")
    t(msp, "TOLVA 3 m³", (60.0, 256.5), 1.9, "MIDDLE_LEFT")
    inst(msp, "LS", "01", (46.8, 262.1))
    senal(msp, [(48.3, 259.0), (55.5, 252.3)])
    mot(msp, "M15", (75.0, 246.4))
    linea(msp, (62.7, 238.2), (62.7, 233.2))                         # descarga de la tolva sobre la cinta
    # cinta con tacos: tramo horizontal + tramo inclinado
    T, K, H = (58.5, 231.0), (80.0, 231.0), (104.4, 258.4)
    ang = math.atan2(H[1] - K[1], H[0] - K[0])
    off = 1.5
    nx, ny = -math.sin(ang), math.cos(ang)
    Kb = (K[0] + 1.6, K[1])
    poli(msp, [(T[0], T[1] + off), (K[0], K[1] + off), (H[0] + nx * off, H[1] + ny * off)])
    poli(msp, [(T[0], T[1] - off), (Kb[0], Kb[1] - off), (H[0] - nx * off, H[1] - ny * off)])
    for c in (T, H):
        relleno_circulo(msp, c, off, (255, 255, 255))
        circulo(msp, c, off)
    for i in range(4):                                                   # tacos
        x = 61.5 + 3.5 * i
        linea(msp, (x, T[1] + off), (x, T[1] + off + 1.6))
    for i in range(1, 8):
        f = i / 8.5
        px, py = K[0] + (H[0] - K[0]) * f + nx * off, K[1] + (H[1] - K[1]) * f + ny * off
        linea(msp, (px, py), (px + nx * 1.6, py + ny * 1.6))
    tn(msp, "3 CINTA CON TACOS 30°", (67.0, 226.6), 1.9, "MIDDLE_LEFT")
    mot(msp, "M8", (103.7, 266.4), dentro=True)
    linea(msp, (103.7, 264.1), (103.9, 260.0))
    inst(msp, "SC", "", (96.0, 272.0))
    linea(msp, (98.4, 269.6), (102.0, 268.0))
    flujo(msp, [(108.2, 262.4), (113.4, 262.4), (118.2, 258.4)], C_PROD)

    # =============== 4 secador de cinta
    rect(msp, 111.9, 196.0, 215.9, 258.2)
    tn(msp, "4  SECADOR DE CINTA - 3 PISOS - 72 m²", (163.8, 254.4), 2.4, "MIDDLE_CENTER")
    mot(msp, "M9", (128.9, 249.1), r=2.0)
    t(msp, "33 °C", (145.0, 249.1), 2.0, "MIDDLE_LEFT")
    for (x0, x1, y, m, lado, sentido) in ((119.9, 207.9, 240.7, "M5", "R", 1), (123.0, 211.0, 226.6, "M6", "L", -1),
                                          (119.9, 207.9, 212.6, "M7", "R", 1)):
        cinta(msp, x0, x1, y)
        t(msp, m, (x1 + 2.6, y) if lado == "R" else (x0 - 2.6, y), 1.8, "MIDDLE_LEFT" if lado == "R" else "MIDDLE_RIGHT")
        a, b = (157.9, 170.5) if sentido > 0 else (170.5, 157.9)
        flecha(msp, (a, y + 3.7), (b, y + 3.7), "CONTORNO", C_PROD, tam=1.8, lw=LW)
    t(msp, "100 °C (máx. 135)", (176.0, 201.7), 2.0, "MIDDLE_LEFT")
    inst(msp, "TT", "02/04", (142.0, 264.0))
    linea(msp, (142.0, 260.6), (142.0, 258.2))
    inst(msp, "PT", "01", (160.0, 202.6))
    linea(msp, (160.0, 199.2), (160.0, 194.6))
    # 3 aire agotado -> ciclón
    flujo(msp, [(134.0, 258.2), (134.0, 272.0), (310.0, 272.0), (310.0, 263.2)], C_AGOT)
    rombo(msp, 3, (151.6, 272.0))
    # 4 producto -> 6 sinfín de descarga
    flujo(msp, [(213.0, 205.0), (213.0, 198.6), (222.2, 199.6)], C_PROD)
    rombo(msp, 4, (219.0, 193.6))

    # =============== 6 sinfín de descarga, 7 elevador, 8 acopio
    rect(msp, 222.2, 196.0, 244.0, 200.8)
    tn(msp, "6", (236.0, 198.4), 2.2, "MIDDLE_CENTER")
    inst(msp, "MIC", "01", (227.9, 207.4), plc=True)
    linea(msp, (227.9, 204.0), (227.9, 200.8))
    inst(msp, "MT", "01", (227.9, 191.6))
    linea(msp, (227.9, 195.0), (227.9, 196.0))
    # Rev. F: MIC-01 en cascada fija la consigna de TIC-01
    senal(msp, [(224.5, 207.4), (172.0, 207.4), (172.0, 195.4)])
    mot(msp, "M10", (248.0, 198.4), lado="B")
    flujo(msp, [(244.0, 198.4), (253.3, 198.4)], C_PROD)
    rect(msp, 253.3, 196.0, 260.0, 254.0)
    tn(msp, "7", (256.65, 226.0), 2.4, "MIDDLE_CENTER")
    mot(msp, "M11", (256.6, 258.3))
    flujo(msp, [(260.0, 250.0), (267.8, 250.0), (278.3, 229.4)], C_PROD)
    poli(msp, [(270.3, 214.0), (296.1, 214.0), (283.2, 228.1)], cerrada=True)
    tn(msp, "8", (283.2, 218.6), 2.4, "MIDDLE_CENTER")
    tn(msp, "ACOPIO", (283.2, 210.2), 2.0, "MIDDLE_CENTER")
    # 14 polvo del ciclón -> vuelve al producto (sinfín 6)
    flujo(msp, [(310.0, 236.1), (310.0, 230.2), (298.8, 230.2), (298.8, 203.6), (242.0, 203.6), (242.0, 200.8)], C_PROD)
    rombo(msp, 14, (285.2, 200.0))

    # =============== 18 ciclón, 19 lavador, 20 extractor M3, 10 chimenea, 21 tanque
    rect(msp, 303.0, 247.0, 316.9, 263.2)
    poli(msp, [(303.0, 247.0), (307.7, 236.1), (312.3, 236.1), (316.9, 247.0)])
    tn(msp, "18", (309.95, 256.3), 2.4, "MIDDLE_CENTER")
    tn(msp, "CICLÓN", (308.0, 266.5), 2.0, "MIDDLE_RIGHT")
    flujo(msp, [(316.9, 257.1), (321.7, 257.1), (321.7, 230.0), (328.0, 230.0)], C_AGOT)
    rect(msp, 328.0, 222.2, 344.0, 266.1)
    tn(msp, "LAVADOR", (336.0, 269.6), 2.0, "MIDDLE_CENTER")
    tn(msp, "19", (336.0, 260.6), 2.4, "MIDDLE_CENTER")
    pk = [(329.4, 236.1), (342.6, 236.1), (342.6, 252.3), (329.4, 252.3)]
    rayado(msp, pk, escala=0.5, angulo=45, patron="ANSI37", color=(0, 0, 0))
    poli(msp, pk, cerrada=True)
    for x in (332.0, 336.0, 340.0):
        linea(msp, (x, 252.3), (x, 254.3), color=C_AGUA, lw=LW)
    flujo(msp, [(344.0, 262.2), (352.0, 262.2), (352.0, 256.1), (357.2, 256.1)], C_AGOT)
    mot(msp, "M3", (361.0, 256.1), r=3.8, dentro=True)
    tn(msp, "20", (361.0, 262.6), 2.2, "MIDDLE_CENTER")
    flujo(msp, [(364.8, 256.1), (370.7, 256.1), (370.7, 250.4), (375.9, 250.4)], C_AGOT)
    rect(msp, 375.9, 244.1, 381.8, 276.0)
    flujo(msp, [(378.85, 276.0), (378.85, 281.6)], C_AGOT)
    rombo(msp, 10, (386.0, 276.0))
    t(msp, "chimenea\n10 m", (378.85, 242.4), 1.8, "TOP_CENTER")
    # recirculación del lavador (bomba M14)
    mot(msp, "M14", (350.9, 212.2), lado="B")
    flujo(msp, [(353.2, 212.2), (355.0, 212.2), (355.0, 249.0), (344.0, 249.0)], C_AGUA)
    inst(msp, "AT", "01", (352.0 - 2.0, 234.4))
    inst(msp, "AIC", "01", (365.0, 234.4), plc=True)
    linea(msp, (353.4, 234.4), (361.6, 234.4))
    senal(msp, [(365.0, 231.0), (365.0, 222.2), (344.0, 222.2)])
    t(msp, "ácido H2SO4", (368.0, 222.2), 1.8, "MIDDLE_LEFT")
    circulo(msp, (336.0, 212.2), 5.3)
    tn(msp, "21", (336.0, 212.2), 2.4, "MIDDLE_CENTER")
    t(msp, "tanque", (338.0, 205.2), 1.8, "MIDDLE_LEFT")
    flujo(msp, [(336.0, 217.5), (336.0, 222.2)], C_AGUA)
    flujo(msp, [(316.0, 212.2), (330.7, 212.2)], C_AGUA)
    t(msp, "agua de reposición", (318.0, 208.8), 1.8, "MIDDLE_CENTER")
    rombo(msp, 12, (324.0, 216.6))
    flujo(msp, [(336.0, 206.9), (336.0, 200.2), (347.5, 200.2)], C_AGUA)
    t(msp, "purga: sulfato de amonio", (348.6, 200.2), 1.8, "MIDDLE_LEFT")
    rombo(msp, 13, (341.9, 195.8))

    # =============== aire: 8 ambiente -> filtro -> 11 ventiladores M1/M2 -> 10 intercambiador
    t(msp, "aire 18 °C", (97.5, 170.2), 1.8, "MIDDLE_RIGHT")
    flujo(msp, [(98.0, 170.2), (113.0, 170.2)], C_FRIO)
    rombo(msp, 8, (103.1, 174.8))
    rect(msp, 113.0, 166.8, 119.1, 173.6)
    linea(msp, (113.0, 166.8), (119.1, 173.6))
    t(msp, "filtro", (116.05, 164.4), 1.8, "MIDDLE_CENTER")
    flujo(msp, [(119.1, 170.2), (128.6, 170.2)], C_FRIO, punta=False)
    relleno_circulo(msp, (132.7, 170.2), 4.1, (255, 255, 255))
    circulo(msp, (132.7, 170.2), 4.1, lw=35)
    t(msp, "M1/M2", (132.7, 170.2), 1.6, "MIDDLE_CENTER")
    tn(msp, "11", (132.7, 163.8), 2.2, "MIDDLE_CENTER")
    flujo(msp, [(136.8, 170.2), (149.9, 170.2)], C_FRIO)
    rect(msp, 149.9, 158.2, 205.8, 184.0)
    tn(msp, "10  INTERCAMBIADOR", (178.1, 181.4), 2.2, "MIDDLE_CENTER")
    t(msp, "carcasa: aire", (178.1, 160.9), 1.8, "MIDDLE_CENTER")
    # humos del hogar por el haz de tubos y a la chimenea 15 por el ciclón de cenizas
    poli(msp, [(218.4, 177.1), (153.1, 177.1), (153.1, 171.7), (202.9, 171.7), (202.9, 166.2), (145.2, 166.2),
               (145.2, 155.0), (103.4, 155.0)], color=C_HUMO, lw=LW)
    flecha(msp, (104.5, 155.0), (102.9, 155.0), "CONTORNO", C_HUMO, tam=2.0)
    flecha(msp, (190.0, 177.1), (187.0, 177.1), "CONTORNO", C_HUMO, tam=2.0)
    rombo(msp, 6, (213.6, 181.2))
    rombo(msp, 7, (149.5, 160.4))
    # ciclón de cenizas y chimenea 15
    rect(msp, 94.9, 150.2, 102.9, 160.1)
    poli(msp, [(94.9, 150.2), (98.0, 145.4), (99.8, 145.4), (102.9, 150.2)])
    t(msp, "ciclón", (98.9, 163.0), 1.8, "MIDDLE_CENTER")
    flujo(msp, [(94.9, 155.0), (84.0, 155.0)], C_HUMO)
    rect(msp, 78.1, 141.6, 84.0, 189.1)
    flujo(msp, [(81.05, 189.1), (81.05, 196.2)], C_HUMO)
    tn(msp, "15", (76.6, 186.8), 2.2, "MIDDLE_RIGHT")
    t(msp, "chim.\n12 m", (76.6, 146.0), 1.8, "BOTTOM_RIGHT")
    inst(msp, "TT", "07", (89.9, 205.0))
    senal(msp, [(89.9, 201.6), (89.9, 186.3), (84.0, 186.3)])
    # 9 cenizas al contenedor 16
    rect(msp, 205.0, 141.0, 214.8, 148.4)
    tn(msp, "16", (209.9, 144.7), 2.2, "MIDDLE_CENTER")
    flujo(msp, [(226.3, 154.2), (226.3, 152.0), (209.9, 152.0), (209.9, 148.4)], NEGRO)
    flujo(msp, [(98.9, 145.4), (98.9, 142.4), (205.0, 142.4)], NEGRO)
    rombo(msp, 9, (219.2, 148.6))

    # =============== 2 aire caliente al secador
    flujo(msp, [(190.0, 184.0), (190.0, 192.0), (200.0, 192.0), (200.0, 196.0)], C_CAL)
    rombo(msp, 2, (194.8, 188.0))

    # =============== 9 hogar
    ho = (218.4, 154.2, 248.0, 188.0)
    e = 2.4
    anillo = [(ho[0], ho[1]), (ho[2], ho[1]), (ho[2], ho[3]), (ho[0], ho[3])]
    for (a0, b0, a1, b1) in ((ho[0], ho[1], ho[2], ho[1] + e), (ho[0], ho[3] - e, ho[2], ho[3]),
                             (ho[0], ho[1] + e, ho[0] + e, ho[3] - e), (ho[2] - e, ho[1] + e, ho[2], ho[3] - e)):
        rayado(msp, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], escala=0.45, color=(0, 0, 0))
    poli(msp, anillo, cerrada=True, lw=50)
    rect(msp, ho[0] + e, ho[1] + e, ho[2] - e, ho[3] - e, "FINO")
    tn(msp, "9  HOGAR", (233.2, 178.2), 2.3, "MIDDLE_CENTER")
    t(msp, "parrilla 0,6 m²", (233.2, 174.4), 1.8, "MIDDLE_CENTER")
    poli(msp, [(223.0, 165.6), (228.0, 165.6), (228.0, 163.2), (232.6, 163.2), (232.6, 160.6), (237.6, 160.6),
               (237.6, 158.6), (242.0, 158.6)])
    inst(msp, "TT", "06", (253.9, 184.2))
    linea(msp, (248.0, 184.2), (250.5, 184.2))
    inst(msp, "BE", "01", (253.9, 175.6))
    linea(msp, (248.0, 175.6), (250.5, 175.6))
    # 5 cáscara: silo 13 -> M12 -> alimentador al hogar
    rect(msp, 248.6, 161.3, 264.2, 164.3)
    flecha(msp, (250.2, 162.8), (246.0, 162.8), "CONTORNO", C_PROD, tam=1.8, lw=LW)
    mot(msp, "M12", (258.1, 158.4))
    flujo(msp, [(273.75, 151.3), (273.75, 147.8), (258.1, 147.8), (258.1, 156.1)], C_PROD)
    rombo(msp, 5, (266.0, 150.7))
    rect(msp, 265.9, 160.1, 281.8, 186.3)
    poli(msp, [(265.9, 160.1), (270.3, 151.3), (277.2, 151.3), (281.8, 160.1)])
    tn(msp, "13", (273.85, 180.6), 2.4, "MIDDLE_CENTER")
    tn(msp, "SILO", (273.85, 176.4), 1.9, "MIDDLE_CENTER")
    t(msp, "70 m³", (273.85, 173.0), 1.8, "MIDDLE_CENTER")
    inst(msp, "LS", "02", (290.0, 182.1))
    linea(msp, (281.8, 182.1), (286.6, 182.1))
    inst(msp, "TS", "01", (290.0, 170.2))
    linea(msp, (281.8, 170.2), (286.6, 170.2))
    # 11 aire de combustión (M4)
    mot(msp, "M4", (236.0, 146.0), dentro=True)
    flujo(msp, [(236.0, 148.3), (236.0, 154.2)], C_FRIO)
    rombo(msp, 11, (229.2, 146.0))

    # =============== lazos (PLC)
    inst(msp, "PIC", "01", (149.9, 191.4), plc=True)
    senal(msp, [(160.0, 194.6), (153.3, 191.4)])
    senal(msp, [(146.5, 191.4), (136.9, 191.4), (133.6, 174.3)])
    inst(msp, "TIC", "01", (172.0, 192.0), plc=True)
    inst(msp, "TT", "01", (210.8, 190.6))
    senal(msp, [(207.4, 190.6), (175.4, 192.0)])
    senal(msp, [(172.0, 188.6), (172.0, 186.3), (244.0, 186.3), (244.0, 167.0), (250.0, 167.0), (250.0, 164.3)])
    senal(msp, [(244.0, 167.0), (244.0, 150.0), (238.2, 147.0)])

    # =============== tabla de corrientes y balances
    subtitulo(msp, "TABLA DE CORRIENTES", 25, 139.6, 2.8)
    tabla(msp, 25, 137.6, [8.0, 42.2, 34.0, 12.0, 106.7], CORR, h_fila=4.0, altura=1.9,
          alin=["C", "L", "L", "C", "L"])
    subtitulo(msp, "BALANCES (por hora de marcha)", 25, 66.0, 2.8)
    t(msp, "\n".join([
        "Masa: 1.000 kg/h guano = 329 kg/h producto + 671 kg/h agua evaporada.",
        "Energía (modelo térmico): generador 617 kW con aire a 100 °C; 882 kW es el máximo, a 135 °C.",
        "Consumo específico: 3,3 MJ/kg de agua (4,7 a 135 °C). Potencia eléctrica instalada: 66,9 kW.",
        "Lavador: el escape llega casi saturado y casi no evapora; la reposición iguala a la purga."]), (25, 64.0), 1.9, "TOP_LEFT")

    # =============== lazos, enclavamientos y leyenda
    subtitulo(msp, "LAZOS DE CONTROL (PLC S7-1200)", 232, 139.6, 2.8)
    tabla(msp, 232, 137.6, [18.1, 70.2, 86.7], LAZOS, h_fila=3.2, altura=1.8)
    subtitulo(msp, "ENCLAVAMIENTOS", 232, 114.0, 2.8)
    t(msp, "\n".join([
        "TT-01 > 160 °C, TT-06 > 950 °C, falla de M3 o sin llama (BE-01) -> corta M12 y abre by-pass de humos.",
        "Arranque: M3 -> M14 -> M1/M2 -> hogar -> cintas -> M8. Parada en orden inverso.",
        "LS-01 / LS-02 nivel bajo: alarma. ZS (puertas) y SS (giro de bandas): paran cintas y M8."]),
      (232, 112.0), 1.8, "TOP_LEFT")
    subtitulo(msp, "LEYENDA", 232, 99.0, 2.8)
    ley = [((232, 94.5), C_PROD, "producto / sólidos"), ((275, 94.5), C_FRIO, "aire frío"),
           ((318, 94.5), C_CAL, "aire caliente"), ((361, 94.5), C_AGOT, "aire agotado"),
           ((232, 90.3), C_HUMO, "humos"), ((275, 90.3), C_AGUA, "agua / solución")]
    for (x, y), col, txt in ley:
        linea(msp, (x, y), (x + 8, y), color=col, lw=LW)
        t(msp, txt, (x + 10, y), 1.8)
    senal(msp, [(318, 90.3), (326, 90.3)], trazo=2.6, hueco=2.8)
    t(msp, "señal (4-20 mA / red)", (328, 90.3), 1.8)
    inst(msp, "XX", "00", (235.6, 84.6))
    t(msp, "instrumento de campo", (240.5, 84.6), 1.8)
    inst(msp, "XIC", "00", (281.6, 84.6), plc=True)
    t(msp, "función del PLC", (286.5, 84.6), 1.8)
    rombo(msp, "", (325.0, 84.6))
    t(msp, "N° de corriente", (329.5, 84.6), 1.8)

    exportar_lamina(doc, 6)


if __name__ == "__main__":
    main()
