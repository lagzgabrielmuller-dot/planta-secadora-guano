"""P14 - Ubicación en Crespo (croquis sin escala) e implantación del lote a 1:1000.

El croquis es esquemático (posiciones relativas orientativas), igual que en la lámina original.
La implantación del lote usa las medidas del modelo: predio 120 × 76 m (Rev. C 72 × 76 m,
G.predio de layout_planta.json, más los 48 m del Sector Este de la Rev. D), nave y anexo del JSON,
depósito de expedición E7 (x 60-80, y 0-12) y cerco de la zona de biogás (x 60-96, y 16-38)
de __revDBuild en visor.html. Origen del lote: vértice SO del predio (x = -22, y = -36 de la nave).
"""
import json
import math
import os

from lamina_secadora import (FECHA, circulo, cota, exportar_lamina, factor, flecha, lamina, linea,
                             norte, notas, poli, rayado, rect, relleno, relleno_circulo, relleno_rect,
                             subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]

GRIS_RUTA = (190, 190, 190)
FONDO_CROQUIS = (243, 242, 237)
PIC = (224, 231, 240)
BIOGAS = (230, 240, 222)
DIGESTOR = (212, 226, 222)
CRESPO = (240, 226, 198)
GRILLA = (215, 200, 170)
AMPLIACION = (238, 240, 245)
ROJO = (200, 16, 46)
VERDE_LOTE = (233, 241, 225)
FONDO_LOTE = (244, 245, 240)
AMARILLO = (255, 242, 196)
DEPOSITO = (228, 198, 182)
NAVE = (220, 220, 220)
CALLE = (185, 185, 185)


# ---------------------------------------------------------------- croquis (sin escala)
# Las formas del croquis se tomaron del PNG original; P() pasa sus coordenadas (px a 200 dpi,
# relativas al marco del croquis) a mm de papel.
CX0, CY1 = 25.0, 271.1


def P(px, py):
    return (CX0 + (px - 8) / 7.871, CY1 - (py - 14) / 7.869)


def PP(pts):
    return [P(*p) for p in pts]


def _intervalos_dentro(poligono, a, b):
    """Tramos del segmento a-b que quedan dentro del polígono (regla par-impar)."""
    ts = []
    n = len(poligono)
    for i in range(n):
        p, q = poligono[i], poligono[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ex, ey = q[0] - p[0], q[1] - p[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        s = ((p[0] - a[0]) * ey - (p[1] - a[1]) * ex) / den
        u = ((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / den
        if 0 <= s <= 1 and 0 <= u < 1:
            ts.append(s)
    if _dentro(poligono, a):
        ts.append(0.0)
    if _dentro(poligono, b):
        ts.append(1.0)
    ts.sort()
    return [(ts[i], ts[i + 1]) for i in range(0, len(ts) - 1, 2)]


def _dentro(poligono, p):
    c = False
    n = len(poligono)
    for i in range(n):
        (x1, y1), (x2, y2) = poligono[i], poligono[(i + 1) % n]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def trazos(e, ltscale=6.0):
    """Las líneas de trazos de la plantilla están en pulgadas: se agranda el patrón."""
    e.dxf.ltscale = ltscale
    return e


def suavizar(pts, n=8):
    """Curva cerrada Catmull-Rom por los puntos dados (contorno de la planta urbana)."""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for k in range(n):
            s = k / n
            s2, s3 = s * s, s * s * s
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * s + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * s2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * s3) for j in (0, 1)))
    return out


def ruta(msp, a, b, ancho):
    """Ruta: banda gris con extremos redondeados y eje blanco a trazos."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    nx, ny = -uy * ancho / 2, ux * ancho / 2
    relleno(msp, [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], GRIS_RUTA)
    relleno_circulo(msp, a, ancho / 2, GRIS_RUTA)
    relleno_circulo(msp, b, ancho / 2, GRIS_RUTA)
    s, paso, trazo = 0.0, 4.2, 2.4
    while s + trazo <= d:
        linea(msp, (a[0] + ux * s, a[1] + uy * s), (a[0] + ux * (s + trazo), a[1] + uy * (s + trazo)),
              "FINO", color=(255, 255, 255), lw=25)
        s += paso


def croquis(msp):
    titulo_vista(msp, "CROQUIS DE UBICACIÓN EN CRESPO, ENTRE RÍOS - SIN ESCALA", 26, 277.5, 3.4)
    x0, y0 = P(8, 1005)
    x1, y1 = P(1585, 14)
    relleno_rect(msp, x0, y0, x1, y1, FONDO_CROQUIS)

    # planta urbana de Crespo (contorno libre con grilla de manzanas)
    blob = suavizar(PP([(55, 440), (130, 393), (240, 372), (350, 385), (440, 422), (505, 488), (538, 575),
                        (542, 665), (515, 760), (470, 842), (420, 912), (330, 946), (262, 953), (170, 936),
                        (92, 882), (32, 792), (9, 645), (16, 538)]))
    relleno(msp, blob, CRESPO)
    for gx in (88, 147, 206, 265, 324, 383, 442):
        a, b = P(gx, 470), P(gx, 912)
        for s0, s1 in _intervalos_dentro(blob, a, b):
            linea(msp, (a[0], a[1] + (b[1] - a[1]) * s0), (a[0], a[1] + (b[1] - a[1]) * s1), "FINO", color=GRILLA, lw=18)
    for gy in (502, 562, 621, 680, 739, 798, 857):
        a, b = P(30, gy), P(482, gy)
        for s0, s1 in _intervalos_dentro(blob, a, b):
            linea(msp, (a[0] + (b[0] - a[0]) * s0, a[1]), (a[0] + (b[0] - a[0]) * s1, a[1]), "FINO", color=GRILLA, lw=18)
    poli(msp, blob, "CONTORNO", cerrada=True, lw=35)
    tn(msp, "CRESPO", P(261, 697), 4.2, "MIDDLE_CENTER")
    t(msp, "planta urbana", P(261, 741), 2.2, "MIDDLE_CENTER")

    # ampliación prevista del PIC
    amp = PP([(780, 582), (1080, 768), (1048, 928), (750, 755)])
    relleno(msp, amp, AMPLIACION)
    trazos(poli(msp, amp, "CONTORNO", cerrada=True, lw=30, tipo="DASHED"))
    t(msp, "ampliación prevista", P(930, 781), 1.8, "MIDDLE_CENTER")
    t(msp, "del PIC (predio de ≈ 70 ha)", P(930, 807), 1.8, "MIDDLE_CENTER")

    # Parque Industrial y planta de biogás vecina
    pic = PP([(638, 156), (953, 236), (922, 555), (607, 362)])
    bio = PP([(953, 236), (1253, 313), (1222, 755), (922, 555)])
    relleno(msp, pic, PIC)
    relleno(msp, bio, BIOGAS)
    for c in ((1016, 345), (1079, 361), (1142, 377), (1000, 424), (1063, 440), (1126, 456)):
        relleno_circulo(msp, P(*c), 2.2, DIGESTOR)
        circulo(msp, P(*c), 2.2, "CONTORNO", lw=25)
    poli(msp, pic, "CONTORNO", cerrada=True)
    poli(msp, bio, "CONTORNO", cerrada=True)
    tn(msp, "PARQUE INDUSTRIAL", P(772, 308), 2.3, "MIDDLE_CENTER")
    tn(msp, "CRESPO (PIC)", P(772, 339), 2.3, "MIDDLE_CENTER")
    t(msp, "54 ha ReNPI", P(772, 373), 1.9, "MIDDLE_CENTER")
    t(msp, "(distrito industrial 85 ha)", P(772, 399), 1.9, "MIDDLE_CENTER")
    tn(msp, "Planta de biogás", P(1095, 528), 2.2, "MIDDLE_CENTER")
    t(msp, "«Ñande Zukunft I»", P(1095, 557), 1.9, "MIDDLE_CENTER")
    t(msp, "32,76 ha · 24 biodigestores", P(1100, 583), 1.8, "MIDDLE_CENTER")

    # Ruta Nacional N° 12 y acceso secundario
    ruta(msp, P(85, 75), P(1495, 960), 3.6)
    a, b = P(435, 502), P(685, 463)
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    s = 0.0
    while s < d:
        e = min(s + 2.2, d)
        linea(msp, (a[0] + (b[0] - a[0]) * s / d, a[1] + (b[1] - a[1]) * s / d),
              (a[0] + (b[0] - a[0]) * e / d, a[1] + (b[1] - a[1]) * e / d), "CONTORNO", color=(120, 120, 120), lw=70)
        s += 3.4
    tn(msp, "RUTA NACIONAL N° 12", P(1218, 828), 2.4, "MIDDLE_CENTER", rotacion=-32.1, color=(70, 70, 70))
    tn(msp, "a PARANÁ ≈ 40 km", P(57, 42), 2.1, "MIDDLE_LEFT")
    tn(msp, "a NOGOYÁ", P(1567, 988), 2.3, "MIDDLE_RIGHT")
    for r in ((332, 84, 410, 102), (143, 131, 221, 150)):
        a, b = P(r[0], r[3]), P(r[2], r[1])
        relleno_rect(msp, a[0], a[1], b[0], b[1], (255, 255, 255))
        rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=25)
    t(msp, "granjas avícolas", P(250, 66), 1.8, "MIDDLE_LEFT")
    t(msp, "acceso principal por la", P(261, 199), 1.9, "MIDDLE_LEFT")
    tn(msp, "RN 12, km 40,6", P(261, 225), 1.9, "MIDDLE_LEFT")
    flecha(msp, P(513, 328), P(603, 349), "CONTORNO", tam=2.0, lw=30)
    t(msp, "acceso secundario: calle Democracia", P(178, 569), 1.8, "MIDDLE_LEFT")
    t(msp, "(continuación de calle Santiago Besler)", P(178, 594), 1.8, "MIDDLE_LEFT")

    # calle J. M. de Rosas y lote propuesto
    poli(msp, [P(1265, 283), P(1233, 785)], "CONTORNO", color=(205, 205, 205), lw=120)
    ang = math.degrees(math.atan2(P(1265, 283)[1] - P(1233, 785)[1], P(1265, 283)[0] - P(1233, 785)[0]))
    t(msp, "calle J. M. de Rosas", P(1262, 660), 1.8, "MIDDLE_CENTER", rotacion=ang)
    lote = PP([(1283, 329), (1442, 367), (1428, 543), (1268, 505)])
    relleno(msp, lote, (255, 255, 255))
    rayado(msp, lote, escala=0.35, color=ROJO)
    poli(msp, lote, "CONTORNO", cerrada=True, color=ROJO, lw=70)
    flecha(msp, P(1394, 205), P(1358, 326), "CONTORNO", color=ROJO, tam=2.4, lw=35)
    tn(msp, "LOTE PROPUESTO", P(1290, 126), 2.6, "MIDDLE_CENTER", color=ROJO)
    t(msp, "secadora de guano 120 × 76 m (0,91 ha)", P(1208, 156), 1.8, "MIDDLE_CENTER", color=ROJO)

    norte(msp, *P(1505, 112), r=5.0)
    rect(msp, x0, y0, x1, y1, "CONTORNO", lw=50)
    t(msp, "Croquis esquemático: las posiciones relativas son orientativas. Verificar parcela, orientación y retiros "
           "con la Municipalidad\nde Crespo (Dirección del Parque Industrial) y con el plano catastral antes del proyecto ejecutivo.",
      (x0, y0 - 2.6), 1.9, "TOP_LEFT", estilo="CURSIVA")


# ---------------------------------------------------------------- implantación del lote 1:1000
def implantacion(msp):
    k = factor("1:1000") * 1000.0          # mm de papel por metro
    km = factor("1:1000")                  # para las cotas (mm reales)
    OX, OY = 40.0, 33.0                    # vértice SO del predio en el papel
    px0 = G["predio"]["x0"]                # -22 (coordenadas de la nave)
    py0 = G["predio"]["y0"]                # -36
    ANCHO_M, ALTO_M = 120.0, float(G["predio"]["y1"] - G["predio"]["y0"])   # 120 × 76 m

    def Q(x, y):                           # coordenadas del modelo (m) -> papel
        return (OX + (x - px0) * k, OY + (y - py0) * k)

    def caja(x0, y0, x1, y1, color, lw=50):
        a, b = Q(x0, y0), Q(x1, y1)
        relleno_rect(msp, a[0], a[1], b[0], b[1], color)
        rect(msp, a[0], a[1], b[0], b[1], "CONTORNO", lw=lw)
        return a, b

    titulo_vista(msp, "IMPLANTACIÓN DEL LOTE - ESC. 1:1000", 26, 122.0, 3.4)
    relleno_rect(msp, OX - 8, OY, OX + ANCHO_M * k + 2, OY + ALTO_M * k + 4, FONDO_LOTE)
    relleno_rect(msp, OX - 8, OY - 10, OX + ANCHO_M * k + 2, OY - 3, CALLE)
    tn(msp, "CALLE DE ACCESO", (OX + 57, OY - 6.5), 1.9, "MIDDLE_CENTER")
    relleno_rect(msp, OX, OY, OX + ANCHO_M * k, OY + ALTO_M * k, VERDE_LOTE)

    # área edificable con los retiros adoptados (igual que el texto): frente (Sur) 10 m,
    # laterales (Oeste y Este) y fondo (Norte) 5 m
    ra = [(OX + 5 * k, OY + 10 * k), (OX + (ANCHO_M - 5) * k, OY + 10 * k),
          (OX + (ANCHO_M - 5) * k, OY + (ALTO_M - 5) * k), (OX + 5 * k, OY + (ALTO_M - 5) * k)]
    trazos(poli(msp, ra, "CONTORNO", cerrada=True, color=ROJO, lw=30, tipo="DASHED"), 4.0)
    t(msp, "área edificable (retiros a verificar)", (OX + 62 * k, OY + 66.6 * k), 1.8, "MIDDLE_CENTER", color=ROJO)

    # nave, anexo, depósito de expedición E7 y zona de biogás
    n = G["nave"]
    an = G["anexo"]
    a, b = caja(n["x0"], n["y0"], n["x0"] + n["L"], n["y0"] + n["A"], NAVE)
    t(msp, "nave 33 × 18 m", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 1.8, "MIDDLE_CENTER")
    a, b = caja(an["x0"], an["y0"], an["x1"], an["y1"], DEPOSITO)
    t(msp, "anexo", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 1.8, "MIDDLE_CENTER")
    a, b = caja(60, 0, 80, 12, DEPOSITO)
    t(msp, "depósito E7", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 1.8, "MIDDLE_CENTER")
    a, b = caja(60, 16, 96, 38, AMARILLO)
    t(msp, "zona de biogás (cerco ATEX)", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 1.8, "MIDDLE_CENTER")

    rect(msp, OX, OY, OX + ANCHO_M * k, OY + ALTO_M * k, "CONTORNO", lw=70)
    # cotas
    cota(msp, (OX, OY + ALTO_M * k), (OX + ANCHO_M * k, OY + ALTO_M * k), distancia=3.0, escala=km, valor="120 m")
    cota(msp, (OX + ANCHO_M * k, OY), (OX + ANCHO_M * k, OY + ALTO_M * k), distancia=-4.0, escala=km, valor="76 m")
    cota(msp, (OX, OY + (ALTO_M - 5) * k), (OX, OY + ALTO_M * k), distancia=3.5, escala=km, valor="5")
    cota(msp, (OX, OY + 10 * k), (OX + 10 * k, OY + 10 * k), distancia=-7.0, escala=km, valor="10")
    cota(msp, (OX + 115 * k, OY), (OX + 115 * k, OY + 10 * k), distancia=-3.0, escala=km, valor="10")

    tn(msp, "Retiros adoptados hasta confirmar", (170, 117.7), 2.0, "MIDDLE_LEFT")
    t(msp, "con el reglamento del PIC:\nfrente 10 m · laterales y fondo 5 m\n(el predio de 120 × 76 m ya los respeta:\n"
           "los equipos más cercanos al cerco\nestán a más de 5 m).", (170, 114.0), 1.85, "TOP_LEFT")


# ---------------------------------------------------------------- textos y tablas de la derecha
def datos(msp):
    X = 232.0
    subtitulo(msp, "DATOS DEL EMPLAZAMIENTO", X, 268.6, 2.6)
    filas = [["Dato", "Valor"],
             ["Localidad", "Crespo, depto. Paraná, Entre Ríos"],
             ["Coordenadas (ciudad)", "32° 02' S · 60° 19' O"],
             ["Acceso", "Ruta Nacional N° 12, km 40,6 (PIC)"],
             ["Acceso secundario", "calle Democracia / Santiago Besler"],
             ["Parque Industrial", "54 ha ReNPI (2014) · distrito 85 ha · ampliación ≈ 70 ha"],
             ["Vecino", "planta de biogás «Ñande Zukunft I»"],
             ["", "Bioenergía Virch S.A. · 32,76 ha · 24 biodig."],
             ["Energía eléctrica", "Coop. La Agrícola Regional (LAR);"],
             ["", "subestación nueva en servicio 16/05/2026"],
             ["Lote requerido", "120 × 76 m = 9.120 m² (0,91 ha)"],
             ["Potencia a contratar", "100 kW (ver plano 23)"]]
    tabla(msp, X, 267.0, [42, 131], filas, h_fila=3.34, altura=1.9)

    subtitulo(msp, "POR QUÉ AL LADO DE LA PLANTA DE BIOGÁS", X, 222.0, 2.6)
    notas(msp, [
        "• El guano que la secadora no alcanza a procesar (fines de semana y feriados,",
        "≈ 920 t/año) tiene destino cercano si falta capacidad en los digestores propios.",
        "• Ambas plantas comparten el acceso de camiones de guano desde las granjas sin",
        "entrar a la planta urbana, y el mismo corredor de servicios de la LAR.",
        "• El biofertilizante líquido y la fracción sólida del digestato se comercializan",
        "junto con el guano seco embolsado (viveros y horticultores).",
        "• El uso industrial del sector ya fue tratado por el Concejo Deliberante",
        "(autorización del 23/09/2026 por excepción a la Ord. 106/2025)."], X, 218.5, 1.8, 1.55)

    subtitulo(msp, "CRITERIOS DE IMPLANTACIÓN", X, 191.3, 2.6)
    notas(msp, [
        "• Recepción, biofiltro y biodigestores del lado opuesto a la planta urbana respecto",
        "de los vientos predominantes (verificar rosa de vientos del SMN, estación Paraná).",
        "• Distancia a viviendas vecinas ≥ 50 m y a linderos ≥ 20 m para los sectores con",
        "guano (criterio de la ordenanza municipal de granjas avícolas).",
        "• Portón de emergencia independiente para bomberos (Dec. 351/79, art. 160 inc. 4).",
        "• Circulación de camiones sólo por la RN 12 y calles del PIC, nunca por el centro."], X, 187.8, 1.8, 1.55)

    subtitulo(msp, "HABILITACIONES Y NORMATIVA", X, 167.8, 2.6)
    filas = [["Ámbito", "Trámite / norma"],
             ["Municipio", "Uso de suelo y radicación en el PIC (Ord. 106/2025, zonificación)"],
             ["", "Planos de obra aprobados (Ord. 49/91) y habilitación comercial"],
             ["Provincia", "Estudio de Impacto Ambiental y Certificado de Aptitud Ambiental"],
             ["", "(Ley 6.260 y Dec. 5.837/91; Dec. 4.977/09 categorización)"],
             ["Provincia", "Bomberos de la Policía de Entre Ríos: plan de protección contra incendios"],
             ["Nación", "Ley 19.587 y Dec. 351/79 (H y S); Ley 24.557 (ART); Res. SRT 905/15"],
             ["Nación", "Ley 25.675 (ambiente); Ley 24.051 (residuos peligrosos de mantenimiento)"],
             ["Nación", "SENASA: inscripción del fertilizante y rotulado de bolsas"],
             ["Energía", "Distribuidora (LAR): potencia y conexión de la cogeneración en paralelo"]]
    tabla(msp, X, 164.0, [22, 151], filas, h_fila=3.34, altura=1.9)

    subtitulo(msp, "FUENTES CONSULTADAS (09/2026)", X, 124.0, 2.3)
    for i, r in enumerate([
        "Municipalidad de Crespo y sitio del Parque Industrial Crespo (PIC); diarios Paralelo32,",
        "Examedia y 9 Digital (proyecto de biogás aprobado el 23/09/2026); directorio de parques",
        "industriales (RN 12 km 40,6). Datos a confirmar en el municipio antes de presentar."]):
        t(msp, r, (X, 120.8 - i * 2.5), 1.8, "TOP_LEFT", estilo="CURSIVA")


def main():
    revs = [("D", "09/2026", "Emisión original: emplazamiento junto al Parque Industrial de Crespo y a la planta "
                             "de biogás Ñande Zukunft I"),
            ("E", FECHA, "Superficie del PIC y su ampliación aclaradas; retiro Oeste = 5 m (lateral)")]
    doc, msp, z = lamina(14, "UBICACIÓN - PARQUE INDUSTRIAL DE CRESPO", "S/E · 1:1000", revs)
    # el título y la escala de esta lámina son largos para el bloque del rótulo: se achican
    for e in msp.query('TEXT[layer=="ROTULO"]'):
        if e.dxf.text == "UBICACIÓN - PARQUE INDUSTRIAL DE CRESPO":
            e.dxf.height = 3.6
        elif e.dxf.text == "S/E · 1:1000":
            e.dxf.height = 2.4
    if "CURSIVA" not in doc.styles:
        doc.styles.add("CURSIVA", font="ariali.ttf")
    croquis(msp)
    implantacion(msp)
    datos(msp)
    exportar_lamina(doc, 14)


if __name__ == "__main__":
    main()
