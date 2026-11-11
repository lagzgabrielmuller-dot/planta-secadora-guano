"""P09 - Secador: corte transversal C-C (1:25) y detalles de borde de banda, pasaje del eje (1:5)
y puerta de inspección (1:10), con las notas generales del secador.

Redibujo vectorial de la lámina aprobada (Rev. C, PNG). Niveles y medidas del secador tomados de
fuente/datos/layout_planta.json (G.secador): H 3,4 m, A 2,6 m, panel 80 mm, patas 0,4 m, pisos
con zc 2,70 / 1,85 / 1,00 m, guías UHMW en y = 0,55 / 0,90 / 1,30 / 1,70 / 2,05 m.
"""
import json
import os

from lamina_secadora import (COL, FECHA, circulo, cota, exportar_lamina, factor, flecha,
                             globo, lamina, linea, nivel, notas, poli, rayado, rect, relleno,
                             relleno_rect, subtitulo, suelo, t, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
S = G["secador"]

GRIS_PANEL = (150, 150, 150)
GRIS_OSCURO = (70, 70, 70)
VERDE_GUIA = (215, 232, 210)
# producto: más oscuro (húmedo) arriba, más claro (seco) abajo
COLOR_PISO = {1: COL["guano"], 2: (176, 128, 70), 3: (200, 165, 110)}


def corte_roto(msp, x0, x1, y, alto=2.2, capa="CONTORNO"):
    """Línea de rotura horizontal con un zigzag en el medio."""
    xm = (x0 + x1) / 2
    poli(msp, [(x0, y), (xm - 0.6, y), (xm - 0.2, y + alto), (xm + 0.2, y - alto), (xm + 0.6, y), (x1, y)], capa)


def referencia(msp, punto, quiebre, texto, x_texto, altura=1.9):
    """Línea de referencia: punto lleno sobre la pieza, tramo inclinado, tramo horizontal y texto."""
    p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
    p.paths.add_edge_path().add_arc(punto, 0.5, 0, 360)
    poli(msp, [punto, quiebre, (x_texto - 0.8, quiebre[1])], "COTAS")
    t(msp, texto, (x_texto, quiebre[1]), altura, "MIDDLE_LEFT")


# ====================================================================== A - CORTE C-C 1:25
def corte_cc(msp):
    k = factor("1:25")
    X0, Z0 = 65.0, 96.0                       # cara exterior Norte y nivel ±0,00 en el papel
    X = lambda y: X0 + y * 1000 * k           # y en m (de Norte a Sur)
    Z = lambda z: Z0 + z * 1000 * k           # z en m
    A, H, e, hp = S["A"], S["H"], S["panel"], S["h_patas"]
    xi0, xi1 = X(e), X(A - e)                 # caras interiores

    titulo_vista(msp, "A - CORTE C-C (por la entrada de aire, mirando al Este)  -  ESC. 1:25", 25, 280.5, 3.5)

    # ---- suelo y patas (UPN 120 / IPN 140)
    suelo(msp, 25, 209, Z0)
    for xa, xb, ztop in ((X(0), X(0.06), 0.88), (X(A - 0.06), X(A), hp)):
        relleno_rect(msp, xa, Z0, xb, Z(ztop), GRIS_OSCURO)
        rect(msp, xa, Z0, xb, Z(ztop), "CONTORNO")
        relleno_rect(msp, xa - 2.6, Z0, xb + 2.6, Z0 + 0.6, (0, 0, 0))

    # ---- paneles en corte (sándwich 80 mm): techo, piso y paredes; pared Norte abierta en la entrada
    secciones = [
        [(X(0), Z(H - e)), (X(A), Z(H - e)), (X(A), Z(H)), (X(0), Z(H))],          # techo
        [(X(0), Z(hp)), (X(A), Z(hp)), (X(A), Z(hp + e)), (X(0), Z(hp + e))],      # piso
        [(X(0), Z(0.88)), (xi0, Z(0.88)), (xi0, Z(H - e)), (X(0), Z(H - e))],      # pared Norte
        [(xi1, Z(hp + e)), (X(A), Z(hp + e)), (X(A), Z(H - e)), (xi1, Z(H - e))],  # pared Sur
    ]
    for s in secciones:
        relleno(msp, s, GRIS_PANEL)
        poli(msp, s, "CONTORNO", cerrada=True)

    # ---- pisos: travesaño L, guías UHMW, banda con producto, guías laterales y ramal de retorno
    yb0, yb1 = 0.3, 2.3                                   # banda de 2000 mm centrada en 2,6 m
    for p in S["pisos"]:
        n, zc = p["n"], p["zc"]
        for dz in (0.025, 0.072):
            linea(msp, (xi0, Z(zc - dz)), (xi1, Z(zc - dz)), "CONTORNO")
        for yg in S["guias_y"]:
            rect(msp, X(yg) - 0.8, Z(zc - 0.02), X(yg) + 0.8, Z(zc), "CONTORNO")
        relleno_rect(msp, X(yb0), Z(zc), X(yb1), Z(zc + 0.03), COLOR_PISO[n])
        rect(msp, X(yb0), Z(zc), X(yb1), Z(zc + 0.03), "CONTORNO")
        for yl, s in ((yb0, -1), (yb1, 1)):
            rect(msp, X(yl) + s * 0.05, Z(zc), X(yl) + s * 0.9, Z(zc + 0.1), "CONTORNO")
        linea(msp, (X(yb0), Z(zc - 0.305)), (X(yb1), Z(zc - 0.305)), "CONTORNO")
        tn(msp, f"PISO {n}", (X(A / 2), Z(zc + 0.17)), 2.2, "MIDDLE_CENTER")
    # ancho de banda (separado del rótulo PISO 1, Rev. C)
    zc1 = S["pisos"][0]["zc"]
    for yl in (yb0, yb1):
        linea(msp, (X(yl), Z(zc1 + 0.1)), (X(yl), Z(zc1 + 0.42)), "COTAS")
    cota(msp, (X(yb0), Z(zc1 + 0.1)), (X(yb1), Z(zc1 + 0.1)), distancia=8.0, escala=k, valor="2000 (banda)")

    # ---- flujo de aire: entra caliente por el ducto 12 (Norte), sube por los pisos y sale agotado
    ca, cv = COL["aire_caliente"], COL["aire_agotado"]
    xd0, xd1 = 29.0, 53.0                                   # ducto 600 mm de ancho
    corte_roto(msp, 27, 55, 260.2)
    poli(msp, [(xd0, 260.2), (xd0, 121.0), (43.0, Z(0.405)), (X(0), Z(0.405))], "CONTORNO", color=ca)
    poli(msp, [(xd1, 260.2), (xd1, 135.3), (X(0), Z(0.88))], "CONTORNO", color=ca)
    linea(msp, (xd0, 135.3), (xd1, 135.3), "CONTORNO")
    flecha(msp, (41.0, 240.3), (41.0, 152.1), "CONTORNO", color=ca, tam=2.4)
    t(msp, "aire 135 °C", (37.4, 218.3), 2.0, "MIDDLE_CENTER", rotacion=90)
    globo(msp, "12", (34.9, 176.3), (41.0, 176.3))
    flecha(msp, (X(0.09), Z(0.65)), (X(1.4), Z(0.65)), "CONTORNO", color=ca, tam=2.2)
    for yy in (0.8, 1.3, 1.8, 2.3):
        linea(msp, (X(yy - 0.5), Z(0.52)), (X(yy - 0.315), Z(0.81)), "CONTORNO", color=ca)   # deflectores
    for yy in (0.8, 1.3):
        flecha(msp, (X(yy), Z(0.52)), (X(yy), Z(0.62)), "CONTORNO", color=ca, tam=1.4)
    for yy in (0.8, 1.3, 1.8):
        flecha(msp, (X(yy), Z(1.30)), (X(yy), Z(1.50)), "CONTORNO", color=ca, tam=1.6)
        flecha(msp, (X(yy), Z(2.15)), (X(yy), Z(2.35)), "CONTORNO", color=cv, tam=1.6)
    t(msp, "deflectores", (93.0, 107.4), 1.9, "MIDDLE_CENTER")

    # ---- pasarela y baranda sobre el techo (lado Sur)
    relleno_rect(msp, X(1.75), Z(H), X(2.52), Z(H) + 0.7, GRIS_OSCURO)
    xb = X(2.52)
    linea(msp, (xb, Z(H)), (xb, Z(H + 1.0)), "CONTORNO")
    relleno_rect(msp, xb - 0.8, Z(H) + 0.7, xb + 0.8, Z(H + 0.1), (0, 0, 0))
    for zz in (H + 0.5, H + 1.0):
        relleno_rect(msp, xb - 1.0, Z(zz) - 1.0, xb + 1.0, Z(zz) + 1.0, GRIS_OSCURO)
    cota(msp, (xb + 1.0, Z(H)), (xb + 1.0, Z(H + 1.0)), distancia=-13.3, escala=k)
    t(msp, "pasarela 800 + baranda 1000", (149.0, 277.5), 1.9, "MIDDLE_CENTER")

    # ---- accionamientos de los pisos 1 y 3 (al fondo, motrices en la cabeza Este; lado Sur)
    for zc, zr0, zr1, _zch0, zch1, mot in ((2.70, 2.08, 2.30, 2.32, 2.43, "M5"), (1.00, 0.24, 0.46, 0.48, 0.73, "M7")):
        za = zc - S["r_motriz"]                                          # eje del tambor motriz
        rect(msp, 170.5, Z(za) - 3.7, 173.3, Z(za) + 3.7, "CONTORNO")    # rodamiento UCF 212
        rz = 0.455 / 2
        rect(msp, 176.0, Z(za - rz), 177.0, Z(za + rz), "CONTORNO")     # corona Z75 de canto
        relleno_rect(msp, 176.0, Z(zch1), 177.0, Z(za - 0.03), (0, 0, 0))
        linea(msp, (176.5, Z(za - rz)), (176.5, Z(zr1) - 2.0), "CONTORNO")
        rect(msp, 171.0, Z(zr0), 183.0, Z(zr1), "CONTORNO")             # reductor
        circulo(msp, (189.6, Z((zr0 + zr1) / 2)), 3.15, "CONTORNO")     # motor
        t(msp, mot, (195.1, Z(zr0) - 4.6), 1.9, "MIDDLE_LEFT")
    for zc in (2.70, 1.85, 1.00):
        nivel(msp, 181.8, Z(zc), f"+{zc:.2f}".replace(".", ","))
    t(msp, "accionamientos pisos 1 y 3", (178.9, 150.0), 1.9, "MIDDLE_LEFT")
    t(msp, "(al fondo, x = 12,45)", (178.9, 144.6), 1.9, "MIDDLE_LEFT")

    # ---- cotas
    cota(msp, (xi0, Z(H)), (xi1, Z(H)), distancia=12.0, escala=k)                    # 2440
    niveles = [0.0, hp, S["pisos"][2]["zc"], S["pisos"][1]["zc"], S["pisos"][0]["zc"], H]
    for za, zb in zip(niveles[:-1], niveles[1:]):
        cota(msp, (X(0), Z(za)), (X(0), Z(zb)), distancia=8.3, escala=k)
    cota(msp, (X(0), Z0), (X(A), Z0), distancia=-5.8, escala=k)                      # 2600

    # ---- referencias y orientación
    globo(msp, "4.8", (60.3, 192.0), (X(0) + 1.6, 188.0))
    globo(msp, "4.1", (135.9, 196.8), (128.9, Z(zc1) + 0.4))
    tn(msp, "NORTE", (37.0, 81.3), 2.2, "MIDDLE_CENTER")
    tn(msp, "SUR", (192.8, 81.3), 2.2, "MIDDLE_CENTER")


# ====================================================================== B - BORDE DE BANDA 1:5
def detalle_borde(msp):
    titulo_vista(msp, "B - DETALLE 1: BORDE DE BANDA  -  ESC. 1:5", 216, 280.5, 3.5)
    k = factor("1:5")
    # panel 80 mm (lana de roca) cortado arriba y abajo
    relleno_rect(msp, 232.2, 230.1, 248.3, 272.0, GRIS_PANEL)
    linea(msp, (232.2, 230.1), (232.2, 272.0))
    linea(msp, (248.3, 230.1), (248.3, 272.0))
    corte_roto(msp, 231.0, 249.5, 272.0, 2.6)
    corte_roto(msp, 231.0, 249.5, 230.1, 2.6)
    # travesaño L 50x50x5 soldado a la estructura
    s = [(248.3, 234.7), (308.2, 234.7), (308.2, 235.7), (249.3, 235.7), (249.3, 244.7), (248.3, 244.7)]
    relleno(msp, s, (120, 120, 120))
    poli(msp, s, "CONTORNO", cerrada=True)
    # guías UHMW-PE 40 x 20
    for x0 in (278.1, 294.1):
        relleno_rect(msp, x0, 244.9, x0 + 8.0, 248.9, VERDE_GUIA)
        rect(msp, x0, 244.9, x0 + 8.0, 248.9, "CONTORNO")
    # malla AISI 304 + cadena lateral + capa de producto 30 mm
    relleno_rect(msp, 290.0, 248.9, 324.1, 250.5, GRIS_OSCURO)
    rect(msp, 290.0, 248.9, 324.1, 250.5, "CONTORNO")
    relleno_rect(msp, 290.6, 250.5, 293.4, 252.6, (60, 50, 45))
    rect(msp, 290.6, 250.5, 293.4, 252.6, "CONTORNO")
    relleno_rect(msp, 293.4, 250.5, 324.1, 256.5, (192, 150, 100))
    rect(msp, 293.4, 250.5, 324.1, 256.5, "CONTORNO")
    # guía lateral inox 3 mm (100 mm de alto) con su soporte
    poli(msp, [(277.2, 270.2), (288.3, 270.2), (288.3, 250.2), (277.2, 250.2)], "CONTORNO")
    rect(msp, 273.1, 262.0, 288.6, 263.2, "CONTORNO")
    rect(msp, 272.8, 256.0, 274.0, 268.1, "CONTORNO")
    cota(msp, (277.2, 250.2), (277.2, 270.2), distancia=-1.6, escala=k)
    # referencias
    referencia(msp, (240.0, 262.0), (250.2, 275.9), "panel 80 mm - lana de roca", 254.9)
    referencia(msp, (288.3, 269.2), (300.4, 275.9), "guía lateral inox 3 mm", 304.9)
    referencia(msp, (318.0, 255.0), (330.1, 270.0), "capa de producto 30 mm", 334.9)
    referencia(msp, (291.9, 251.5), (335.3, 256.0), "cadena lateral", 339.8)
    referencia(msp, (316.0, 249.6), (340.1, 243.9), "malla AISI 304 Ø2", 344.8)
    referencia(msp, (298.0, 246.7), (350.2, 234.0), "guía UHMW-PE 40 x 20", 354.9)
    referencia(msp, (272.0, 235.2), (300.4, 228.1), "travesaño L 50x50x5", 304.9)


# ====================================================================== C - PASAJE DEL EJE 1:5
def detalle_eje(msp):
    titulo_vista(msp, "C - DETALLE 2: PASAJE DEL EJE  -  ESC. 1:5", 216, 221.6, 3.5)
    # panel del secador (80 mm), cortado
    yp0, yp1 = 167.0, 211.0
    relleno_rect(msp, 254.1, yp0, 270.1, yp1, GRIS_PANEL)
    linea(msp, (254.1, yp0), (254.1, yp1))
    linea(msp, (270.1, yp0), (270.1, yp1))
    corte_roto(msp, 252.9, 271.3, yp1, 2.6)
    corte_roto(msp, 252.9, 271.3, yp0, 2.6)
    # sello de laberinto (2 anillos) alrededor del eje
    relleno_rect(msp, 254.1, 182.1, 270.1, 194.1, (255, 255, 255))
    rect(msp, 252.9, 175.6, 271.4, 200.5, "CONTORNO")
    for xa in (257.0, 261.1, 265.4, 268.8):
        linea(msp, (xa, 194.1), (xa, 195.5), "CONTORNO")
        linea(msp, (xa, 182.1), (xa, 180.7), "CONTORNO")
    # eje SAE 1045 Ø60
    rect(msp, 220.0, 182.1, 304.2, 194.1, "CONTORNO")
    linea(msp, (254.1, 182.1), (254.1, 194.1), "FINO")
    linea(msp, (270.1, 182.1), (270.1, 194.1), "FINO")
    linea(msp, (217.8, 188.1), (306.3, 188.1), "EJES")
    # ménsula PL 12 soldada a la estructura (en corte)
    m = [(277.6, 168.0), (280.2, 168.0), (280.2, 206.1), (277.6, 206.1)]
    rayado(msp, m, escala=0.12)
    poli(msp, m, "CONTORNO", cerrada=True)
    # rodamiento UCF 212 con brida
    poli(msp, [(280.2, 205.6), (288.2, 205.6), (288.2, 170.6), (280.2, 170.6)], "CONTORNO")
    relleno_rect(msp, 281.9, 194.1, 295.3, 197.2, (0, 0, 0))
    relleno_rect(msp, 281.9, 178.9, 295.3, 182.1, (0, 0, 0))
    rect(msp, 281.9, 178.9, 295.3, 197.2, "CONTORNO")
    for yb in (202.3, 173.7):
        linea(msp, (275.8, yb), (290.2, yb), "EJES")
    tn(msp, "INTERIOR", (240.0, 172.5), 1.9, "MIDDLE_CENTER")
    tn(msp, "EXTERIOR", (300.1, 172.5), 1.9, "MIDDLE_CENTER")
    referencia(msp, (262.0, 206.5), (312.4, 214.0), "panel del secador (80 mm)", 316.9)
    referencia(msp, (266.1, 197.3), (316.2, 206.0), "sello de laberinto (2 anillos)", 320.7)
    referencia(msp, (292.1, 197.2), (322.0, 197.9), "rodamiento UCF 212 (brida)", 326.9)
    referencia(msp, (302.1, 182.1), (327.0, 182.1), "eje SAE 1045 Ø60", 330.9)
    referencia(msp, (278.9, 168.8), (322.0, 168.8), "ménsula PL 12 soldada a la estructura", 326.9)


# ====================================================================== D - PUERTA 1:10
def detalle_puerta(msp):
    dy = 5.0                                   # subido 5 mm: la tabla de revisiones D ocupa hasta y = 80
    titulo_vista(msp, "D - DETALLE 3: PUERTA 700 x 600  -  ESC. 1:10", 216, 154.3 + dy, 3.5)
    k = factor("1:10")
    Y = lambda y: y + dy
    rect(msp, 223.6, Y(82.7), 300.6, Y(149.5), "CONTORNO")      # marco
    rect(msp, 226.9, Y(86.1), 296.9, Y(146.1), "CONTORNO")      # vano 700 x 600
    rect(msp, 229.1, Y(88.2), 295.1, Y(144.0), "CONTORNO")      # hoja
    for y0, y1 in ((132.1, 140.1), (91.9, 100.2)):               # bisagras
        rect(msp, 222.4, Y(y0), 226.9, Y(y1), "CONTORNO")
    for yc in (136.1, 96.1):                                     # cierres de leva
        circulo(msp, (293.9, Y(yc)), 1.5, "CONTORNO")
        linea(msp, (295.1, Y(yc) + 0.6), (297.0, Y(yc) + 1.4), "CONTORNO")
    linea(msp, (297.0, Y(137.5)), (297.6, Y(139.2)), "COTAS")
    t(msp, "cierres de leva", (298.0, Y(140.7)), 1.9, "MIDDLE_LEFT")
    rect(msp, 297.9, Y(111.9), 302.1, Y(119.9), "CONTORNO")      # microinterruptor
    tn(msp, "ZS", (300.0, Y(116.0)), 1.8, "MIDDLE_CENTER")
    t(msp, "microinterruptor", (302.9, Y(116.0)), 1.9, "MIDDLE_LEFT")
    referencia(msp, (224.7, Y(96.0)), (224.7, Y(96.0)), "bisagras", 231.8)
    t(msp, "burlete siliconado 200 °C", (262.0, Y(84.4)), 1.8, "MIDDLE_CENTER")
    cota(msp, (226.9, Y(86.1)), (226.9, Y(146.1)), distancia=11.2, escala=k)        # 600
    cota(msp, (226.9, Y(86.1)), (296.9, Y(86.1)), distancia=-9.3, escala=k)         # 700


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "Lámina nueva: corte por entrada de aire, borde de banda, pasaje de eje y puerta"),
            ("C", "09/2026", "Cota ancho de banda separada de PISO 1; rótulo bisagras fuera del marco puerta"),
            ("D", FECHA, "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24")]
    doc, msp, z = lamina(9, "SECADOR - CORTE TRANSVERSAL\nY DETALLES", "1:25 / 1:5 / 1:10", revs)
    corte_cc(msp)
    detalle_borde(msp)
    detalle_eje(msp)
    detalle_puerta(msp)
    subtitulo(msp, "NOTAS GENERALES DEL SECADOR", 25, 57.6, 2.9)
    notas(msp, [
        "1. Todo lo que toca el producto: acero inoxidable AISI 304. Estructura: acero F-24 con antióxido epoxi + esmalte poliuretánico.",
        "2. Soldaduras: E6013 en estructura (cordón 4 mm); inox con TIG ER308L. Tornillería 8.8 zincada; A2 en zonas húmedas.",
        "3. Tambores escalonados 250 mm en las transferencias; motrices en la cabeza de cada banda (pisos 1 y 3 al Este, piso 2 al Oeste).",
        "4. Rodamientos UCF 212 / UCT 210 fuera de la cámara, sobre ménsulas; sellos de laberinto en el panel.",
        "5. Entrada de aire lateral (cara Norte) con 4 deflectores; salida por la campana del techo (flujo en Z).",
        "6. Puertas con microinterruptor (ZS): abrirlas detiene cintas y dosificador. Pasarela con baranda 1,0 m y zócalo.",
    ], 25, 56.0, altura=1.95, interlineado=1.72)
    exportar_lamina(doc, 9)


if __name__ == "__main__":
    main()
