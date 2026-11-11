"""Juego de planos aparte del secador de cinta SC-4 (láminas SC-01 a SC-06, A3, numeración propia).

    python planos_sc.py            # las 6 láminas + Planos_Secador_SC4.pdf
    python planos_sc.py 2 4        # solo SC-02 y SC-04 (y rearma el PDF)

Salida en secadora/planos/ (dxf/, pdf/, png). El PDF del juego del secador agrega al final, como
referencia, las láminas del juego general que son del secador: P02, P03, P09 y P22.

Fuentes de datos (nada se copia a mano):
  secadora/modelo_3d/piezas.json        lista de piezas, masas, centros y vectores de despiece (CadQuery)
  proyecciones.py                       vistas ortogonales del modelo (HLR) para SC-01 y SC-05
  secadora/renders/                     capturas del visor (visor/capturas.js) para SC-01, SC-02 y SC-06
  fuente/calculos/resultados.json       fatiga (SC-03, SC-04) y anclajes (SC-05)
  pasos_montaje.json                    los 13 pasos del manual de armado (SC-06)
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "fuente", "planos"))
sys.path.insert(0, AQUI)

from lamina_secadora import (COL, FECHA, arco, circulo, cota, exportar_lamina, factor, flecha, globo,  # noqa: E402
                             imagen, lamina, linea, nivel, notas, poli, rayado, rect, relleno, relleno_rect,
                             subtitulo, t, tabla, titulo_vista, tn, unir_pdfs)
from proyecciones import proyectar  # noqa: E402

CARPETA = os.path.join(RAIZ, "secadora", "planos")
RENDERS = os.path.join(RAIZ, "secadora", "renders")
SERIE = {"prefijo": "SC-", "total": 6}
REVS = [("A", FECHA, "Emisión original: juego aparte del secador SC-4"),
        ("B", "11/2026", "Estudio térmico (Rev. F): guías PTFE en pisos 2 y 3, faldones de sellado 4.21")]
PIEZAS = json.load(open(os.path.join(RAIZ, "secadora", "modelo_3d", "piezas.json"), encoding="utf-8"))["piezas"]
RES = json.load(open(os.path.join(RAIZ, "fuente", "calculos", "resultados.json"), encoding="utf-8"))
FAT = RES["fatiga"]
PASOS = json.load(open(os.path.join(AQUI, "pasos_montaje.json"), encoding="utf-8"))

GRIS = (215, 218, 222)
GRIS_OSC = (120, 125, 130)
VERDE = (214, 236, 214)
ROJO_SUAVE = (250, 214, 210)
AMARILLO = (255, 240, 190)


def coma(v, dec=1):
    """Número con coma decimal y punto de miles (es-AR)."""
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


SUP = str.maketrans("0123456789-−", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁻")


def pot10(txt):
    """'1.44e+03' -> '1,44·10³' (el ^ no se puede usar en textos DXF)."""
    m = re.fullmatch(r"([\d.]+)e\+?(-?\d+)", txt.strip())
    if not m:
        return txt
    return f"{coma(float(m.group(1)), 2)}·10{str(int(m.group(2))).translate(SUP)}"


def nueva(numero, titulo, escala):
    return lamina(numero, titulo, escala, REVS, serie=SERIE)


def guardar(doc, numero):
    return exportar_lamina(doc, numero, carpeta_planos=CARPETA, prefijo="SC-")


def img(doc, msp, archivo, x, y, ancho, alto=None):
    return imagen(doc, msp, os.path.join(RENDERS, archivo), x, y, ancho, alto, carpeta_planos=CARPETA)


def dibujar(msp, polis, k, dx, dy, capa="FINO"):
    """Polilíneas en mm del modelo -> papel: (x, y) * k + (dx, dy)."""
    for pl in polis:
        pts = [(x * k + dx, y * k + dy) for x, y in pl]
        if len(pts) == 2:
            msp.add_line(pts[0], pts[1], dxfattribs={"layer": capa})
        else:
            msp.add_lwpolyline(pts, dxfattribs={"layer": capa})


def pieza(cod):
    return next(p for p in PIEZAS if p["cod"] == cod)


def agrupar():
    """Lista de piezas agrupada por código base (las de los 3 pisos juntas)."""
    grupos = {}
    for p in PIEZAS:
        base = re.sub(r"-\d$", "", p["cod"])
        base = "M5–M7" if re.fullmatch(r"M\d", base) else base
        nombre = re.sub(r"\s*–\s*piso \d$", "", p["nombre"])
        nombre = re.sub(r"Motor M\d", "Motores", nombre)
        g = grupos.setdefault(base, {"cod": base, "nombre": nombre, "cant": 0, "masa": 0.0,
                                     "material": p["material"], "ids": [], "nota": p["nota"]})
        g["cant"] += p["cantidad"]
        g["masa"] += p["masa_kg"]
        g["ids"].append(p["id"])
    orden = lambda c: [int(x) if x.isdigit() else ord(x[0]) for x in re.findall(r"\d+|[a-zA-Z]", c)] \
        if not c.startswith("M") else [4, 5, 0]
    return sorted(grupos.values(), key=lambda g: orden(g["cod"]))


# ================================================================ SC-01 conjunto general
def sc01():
    doc, msp, z = nueva(1, "SECADOR DE CINTA SC-4\nCONJUNTO GENERAL", "1:75")
    k = factor("1:75")
    v = proyectar("exterior", ["frente", "planta", "lateral_o"])
    cf, cp, cl = v["frente"]["caja"], v["planta"]["caja"], v["lateral_o"]["caja"]
    # frente (cara Sur) arriba a la izquierda, planta debajo, lateral izquierda (desde el Oeste) a la derecha
    x0, yf = 34.0, 196.0
    dxf, dyf = x0 - cf[0] * k, yf - cf[1] * k
    dibujar(msp, v["frente"]["visibles"], k, dxf, dyf)
    yp_top = 160.0
    dxp, dyp = x0 - cp[0] * k, yp_top - cp[3] * k
    dibujar(msp, v["planta"]["visibles"], k, dxp, dyp)
    xl = x0 + (cf[2] - cf[0]) * k + 30
    dxl, dyl = xl - cl[0] * k, dyf
    dibujar(msp, v["lateral_o"]["visibles"], k, dxl, dyl)
    F = lambda x, zz: (x * k + dxf, zz * k + dyf)
    P = lambda x, y: (x * k + dxp, y * k + dyp)
    L = lambda u, zz: (u * k + dxl, zz * k + dyl)          # u = -y del modelo
    # piso y títulos
    linea(msp, F(-1500, 0), F(13400, 0), "CONTORNO")
    linea(msp, L(-3000, 0), L(700, 0), "CONTORNO")
    titulo_vista(msp, "VISTA FRONTAL (CARA SUR, ACCIONAMIENTOS)", x0, 275, 3.0)
    titulo_vista(msp, "VISTA SUPERIOR", x0, yp_top + 13, 3.0)
    titulo_vista(msp, "LATERAL IZQ. (OESTE)", xl - 2, 275, 3.0)
    # ejes de columnas (letras debajo de la planta)
    for i, xc in enumerate((60, 3250, 6500, 9750, 12940)):
        linea(msp, P(xc, -1050), P(xc, 3100), "EJES")
        circulo(msp, P(xc, -1300), 2.4, "COTAS")
        tn(msp, "ABCDE"[i], P(xc, -1300), 2.4, "MIDDLE_CENTER")
    # cotas
    cota(msp, F(0, 0), F(13000, 0), -13, k)
    for a, b in ((60, 3250), (3250, 6500), (6500, 9750), (9750, 12940)):
        cota(msp, F(a, 0), F(b, 0), -7, k)
    cota(msp, P(13000, 0), P(13000, 2600), -12, k)
    cota(msp, L(-2600, 0), L(0, 0), -7, k)
    cota(msp, L(-2600, 0), L(-2600, 3400), 6, k)
    cota(msp, L(-2600, 0), L(-2600, 4500), 12, k)
    cota(msp, L(-2600, 0), L(-2600, 400), 2.5, k, valor="400")
    # niveles de las bandas (a la derecha de la vista lateral)
    for zz, txt in ((2700, "+2,70 banda piso 1"), (1850, "+1,85 banda piso 2"), (1000, "+1,00 banda piso 3")):
        linea(msp, L(-2600, zz), L(650, zz), "AUXILIAR")
        nivel(msp, L(700, zz)[0], L(0, zz)[1], txt)
    # globos de los componentes principales (sobre la vista frontal y la planta)
    refs = [("4.13", "4.13", F, (5730, 3750), (6300, 5050)),
            ("4.12", "4.12", F, (3000, 3700), (3000, 5050)),
            ("4.19c", "4.19c", F, (900, 3550), (1500, 5050)),
            ("4.8a", "4.8a", F, (7300, 2300), (8100, 5050)),
            ("4.9", "4.9", F, (4875, 2700), (4500, 5050)),
            ("4.15c-1", "4.15c", F, (12450, 2700), (13750, 3500)),
            ("M5", "M5", F, (12376, 2216), (13750, 2500)),
            ("4.5-3", "4.5", F, (12420, 384), (13750, 1200)),
            ("4.16b-3", "4.16b", F, (12450, 150), (13750, 250)),
            ("4.11a", "4.11a", F, (9750, 200), (10900, -1700)),
            ("4.17", "4.17", F, (6500, 6), (7500, -1700)),
            ("4.19b", "4.19b", P, (11000, 2675), (11000, 3450)),
            ("4.14-1", "4.14", P, (375, 2670), (900, 3450)),
            ("4.4-1", "4.4", P, (12450, 2670), (12450, 3450)),
            ("4.19a", "4.19a", P, (12750, 1300), (14350, 1300))]
    for _, etq, fn, a, b in refs:
        globo(msp, etq, fn(*b), apunta_a=fn(*a), radio=3.6, relleno_rgb=(255, 255, 255))
    # render y datos a la derecha
    xr = 302.0
    img(doc, msp, "SC_general.png", xr, 133, 103, 103 / 1.6)
    t(msp, "Vista 3D del modelo (visor Visor_Secador_SC4.html)", (xr, 131.5), 1.7, "TOP_LEFT")
    ms = sum(p["masa_kg"] for p in PIEZAS)
    datos = [["Dato", "Valor"],
             ["Capacidad", "8 t/día de guano húmedo (60 % → 15 %)"],
             ["Tipo", "Secador de cinta continuo, 3 pisos"],
             ["Cámara (largo × ancho × alto)", "13,0 × 2,6 × 3,4 m"],
             ["Bandas", "3 × malla AISI 304, 2,0 m de ancho"],
             ["Velocidad de banda", "≈ 0,37 m/min (VFD, ≈ 20 Hz)"],
             ["Accionamientos", "3 × 0,75 kW 1:300 + cadena ASA 60 1:5"],
             ["Tambores", "motriz Ø316 con goma / reenvío Ø250"],
             ["Ejes", "SAE 1045 Ø60/Ø50 (Rev. E de fatiga)"],
             ["Cerramiento", "panel sándwich 80 mm lana de roca"],
             ["Aire caliente", "entrada 1,2 × 0,4 m cara Norte, ≤ 120 °C"],
             ["Masa del equipo (modelo 3D)", f"{coma(ms, 0)} kg (sin producto)"],
             ["Fijación al piso", "10 placas, 40 anclajes químicos M16 (SC-05)"],
             ["Ubicación en planta", "x = 11,50 m, y = 8,00 m (plano 13)"]]
    tabla(msp, 292, 127, [44, 69], datos, h_fila=3.3, altura=1.8, alin=["L", "L"])
    notas(msp, ["1. Origen: vértice Sudoeste del secador sobre la platea; x a lo largo de la cámara (Este),",
                "   y hacia el Norte. Medidas del modelo 3D Secador_SC4.step (CadQuery).",
                "2. Vistas proyectadas del modelo con eliminación de líneas ocultas (HLR).",
                "3. Lista completa de piezas y despiece: SC-02. Ejes: SC-03. Fatiga: SC-04.",
                "   Bastidor y anclajes: SC-05. Montaje paso a paso: SC-06.",
                "4. Corte longitudinal y corte transversal del secador: planos 02 y 09 del juego general."],
          34, 62, altura=2.0, titulo="NOTAS")
    return guardar(doc, 1)


# ================================================================ SC-02 despiece
def sc02():
    doc, msp, z = nueva(2, "SECADOR DE CINTA SC-4\nDESPIECE Y LISTA DE PIEZAS", "S/E")
    titulo_vista(msp, "VISTA EXPLOTADA (DESPIECE) DEL MODELO 3D", 27, 278, 3.2)
    X0, Y0, W = 27.0, 128.0, 222.0
    H = W / 1.6
    img(doc, msp, "SC_despiece.png", X0, Y0, W, H)
    grupos = agrupar()
    for i, g in enumerate(grupos, 1):
        g["pos"] = i
    # globos sobre la imagen: posición proyectada del centro de cada pieza despiezada
    ruta = os.path.join(RENDERS, "SC_despiece_globos.json")
    if os.path.exists(ruta):
        gj = json.load(open(ruta, encoding="utf-8"))
        pix = {p["id"]: p["px"] for p in gj["piezas"]}
        aw, ah = gj["ancho"], gj["alto"]
        papel = lambda px: (X0 + px[0] / aw * W, Y0 + (1 - px[1] / ah) * H)
        ocupados = []
        cx, cy = X0 + W / 2, Y0 + H / 2
        for g in grupos:
            # una referencia por grupo: la pieza del grupo más cercana al centro de la imagen
            pts = [papel(pix[i]) for i in g["ids"] if i in pix]
            pts = [p for p in pts if X0 + 3 < p[0] < X0 + W - 3 and Y0 + 3 < p[1] < Y0 + H - 3]
            if not pts:
                continue
            a = min(pts, key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
            ang = math.atan2(a[1] - cy, a[0] - cx)
            for r_ in (9, 13, 17, 21, 25, 30):
                ok = False
                for dang in (0, 0.35, -0.35, 0.7, -0.7, 1.1, -1.1):
                    b = (a[0] + r_ * math.cos(ang + dang), a[1] + r_ * math.sin(ang + dang))
                    b = (min(max(b[0], X0 + 4), X0 + W - 4), min(max(b[1], Y0 + 4), Y0 + H - 4))
                    if all(math.hypot(b[0] - o[0], b[1] - o[1]) > 7.6 for o in ocupados):
                        ok = True
                        break
                if ok:
                    break
            ocupados.append(b)
            globo(msp, str(g["pos"]), b, apunta_a=a, radio=3.4, relleno_rgb=(255, 255, 255))
    # lista de piezas
    filas = [["Pos.", "Cód.", "Denominación", "Cant.", "Material", "kg"]]
    for g in grupos:
        nom = g["nombre"]
        nom = nom if len(nom) <= 52 else nom[:50] + "…"
        filas.append([str(g["pos"]), g["cod"], nom, str(g["cant"]), g["material"][:24], coma(g["masa"], 0)])
    filas.append(["", "", "MASA TOTAL DEL SECADOR (sin producto)", "", "", coma(sum(g["masa"] for g in grupos), 0)])
    subtitulo(msp, "LISTA DE PIEZAS (agrupada; las de los 3 pisos juntas)", 252, 279)
    tabla(msp, 252, 277, [8, 11, 74, 9, 36, 13], filas, h_fila=5.15, altura=1.75,
          alin=["C", "L", "L", "C", "L", "R"], negrita_ultima=True)
    # desarme
    notas(msp, [
        "Desarme (orden inverso al montaje de SC-06), con el equipo detenido y bloqueado:",
        "1. Cortar y bloquear con candado el seccionador del TG y los VFD (LOTO); esperar 15 min a que la cámara baje de 40 °C.",
        "2. Vaciar las bandas en marcha lenta; retirar techo (4.8e), campana (4.12) y pasarela (4.13) con grúa.",
        "3. Retirar los cárteres (4.15c), aflojar los colisos de la consola (4.16b) y sacar la cadena con el extractor.",
        "4. Desmontar motorreductores (4.5 + M) y consolas. Aflojar los tensores UCT (4.14) hasta el final de carrera.",
        "5. Abrir el empalme de cada banda (4.1) y enrollarla desde la cola. Retirar rodillos (4.6) y guías (4.7).",
        "6. Sacar los ejes (4.2.1 / 4.3.1) por el lado Sur con el tambor apoyado en caballetes; no golpear los asientos.",
        "7. Paneles laterales y testeros (4.8a-d) y, por último, estructura (4.11, 4.20) y placas base (4.17).",
        "Los anclajes químicos (4.17a) no se reutilizan: cortar a ras y hacer anclajes nuevos desplazados ≥ 2 Ø.",
    ], 27, 118, altura=1.95, interlineado=1.5, titulo="DESARME / DESPIECE EN OBRA")
    pares = [["Unión", "Tornillo", "Par N·m"],
             ["Placa base a platea (4.17a)", "M16 5.8 químico", "80"],
             ["Rodamientos UCF 212 / ménsula", "M14 8.8", "135"],
             ["Unidades tensoras UCT 210", "M16 8.8", "210"],
             ["Consola motorreductor", "M16 8.8", "210"],
             ["Reductor a consola", "M12 8.8", "85"],
             ["Cárter de la cadena", "M8 5.6", "12"],
             ["Prisioneros insertos UC", "M10 (punta)", "29"]]
    tabla(msp, 27, 72, [52, 32, 16], pares, h_fila=4.0, altura=1.9, alin=["L", "L", "R"])
    t(msp, "Pares de apriete en seco, μ ≈ 0,14 (VDI 2230); los del anclaje según el fabricante de la resina.",
      (27, 38), 1.7, "TOP_LEFT")
    notas(msp, ["Pos. = número de globo. Masas del modelo 3D (CadQuery) con los pesos de",
                "catálogo de bandas, tambores, motorreductores, paneles y pasarela."],
          133, 72, altura=1.8, interlineado=1.45)
    return guardar(doc, 2)


# ================================================================ SC-03 ejes (fabricación)
def _eje(msp, x0, y0, k, tramos, titulo):
    """Eje horizontal por tramos [(largo, diámetro), ...] desde x0 (izquierda) con el eje en y0."""
    x = x0
    bordes = []
    for l, d in tramos:
        r = d / 2 * k
        rect(msp, x, y0 - r, x + l * k, y0 + r, "CONTORNO")
        bordes.append((x, x + l * k, d))
        x += l * k
    linea(msp, (x0 - 4, y0), (x + 4, y0), "EJES")
    titulo_vista(msp, titulo, x0, y0 + 22, 3.0)
    return bordes


def sc03():
    doc, msp, z = nueva(3, "SECADOR SC-4 - EJES MOTRIZ Y DE\nREENVÍO (FABRICACIÓN, REV. E)", "1:10 / 1:2")
    k = factor("1:10")
    # ---- eje motriz 4.2.1: Ø60 de -1440 a +1455 (2.895), Ø50 de 1455 a 1560 (105); u desde el norte
    x0, y0 = 40.0, 236.0
    _eje(msp, x0, y0, k, [(2895, 60), (105, 50)], "A - EJE MOTRIZ 4.2.1 (3 piezas)  -  ESC. 1:10")
    U = lambda u: x0 + u * k                         # u = mm desde el extremo Norte
    for uc, txt, h in ((70, "UCF 212 (A)", 15), (396, "cubo N", 15), (2484, "cubo S", 15), (2810, "UCF 212 (B)", 15),
                       (2945, "corona Z75", 19.5)):
        linea(msp, (U(uc), y0 - 6), (U(uc), y0 + h - 1), "EJES")
        t(msp, txt, (U(uc), y0 + h), 1.8, "BOTTOM_CENTER")
    # zonas rectificadas (asientos de cubo) y chavetero
    for uc in (396, 2484):
        relleno_rect(msp, U(uc - 40), y0 - 3, U(uc + 40), y0 + 3, AMARILLO)
        rect(msp, U(uc - 40), y0 - 3, U(uc + 40), y0 + 3, "FINO")
    rect(msp, U(2913), y0 - 0.6, U(2976), y0 + 2.5, "FINO")
    cota(msp, (U(0), y0 - 3), (U(3000), y0 - 3), -21, k)
    cota(msp, (U(0), y0 - 3), (U(2895), y0 - 3), -14, k)
    for a, b in ((0, 70), (70, 396), (396, 2484), (2484, 2810)):
        cota(msp, (U(a), y0 + 3), (U(b), y0 + 3), 4.5 if a else 7.5, k)
    t(msp, "Ø60 h8 (asientos de cubo: rectificado Ra 0,8)", (U(1440), y0 - 6.0), 1.9, "TOP_CENTER")
    t(msp, "Ø60 h7 en UCF", (U(70), y0 - 6.0), 1.9, "TOP_LEFT")
    t(msp, "Ø50 k6", (U(2950), y0 - 6.0), 1.9, "TOP_CENTER")
    # ---- detalle B (1:2): escalón Ø60/Ø50 con r = 2 y chavetero 14 × 9 × 63
    k2 = factor("1:2")
    bx, by = 40.0, 166.0
    titulo_vista(msp, "B - EXTREMO SUR: ESCALÓN Y CHAVETERO  -  ESC. 1:2", bx, by + 30, 3.0)
    B = lambda u, v: (bx + (u - 2840) * k2, by + v * k2)
    poli(msp, [B(2840, 30), B(2893, 30)], "CONTORNO")
    arco(msp, B(2893, 27), 2 * k2, 0, 90)
    poli(msp, [B(2895, 27), B(2895, 25), B(2998, 25), B(3000, 23), B(3000, -23), B(2998, -25), B(2895, -25),
               B(2895, -27)], "CONTORNO")
    arco(msp, B(2893, -27), 2 * k2, 270, 360)
    poli(msp, [B(2893, -30), B(2840, -30)], "CONTORNO")
    linea(msp, B(2835, 0), B(3008, 0), "EJES")
    rect(msp, B(2913, 25 - 5.5)[0], B(0, 19.5)[1], B(2976, 0)[0], B(0, 25)[1], "CONTORNO")
    rayado(msp, [B(2913, 19.5), B(2976, 19.5), B(2976, 25), B(2913, 25)], escala=0.15)
    cota(msp, B(2895, 25), B(3000, 25), 9, k2)
    cota(msp, B(2913, 25), B(2976, 25), 4.5, k2)
    cota(msp, B(3000, -25), B(3000, 25), 7, k2, valor="Ø50 k6")
    cota(msp, B(2850, -30), B(2850, 30), -7, k2, valor="Ø60 h7")
    t(msp, "r = 2 pulido (Rev. E)", (B(2893, 30)[0] - 2, B(0, 30)[1] + 6), 2.0, "BOTTOM_RIGHT")
    flecha(msp, (B(2893, 30)[0] - 1.5, B(0, 30)[1] + 5.5), B(2894, 28.6), "COTAS")
    t(msp, "chavetero 14 P9 × 5,5 × 63 (DIN 6885 A)", (B(2944, 0)[0], B(0, -25)[1] - 4), 1.9, "TOP_CENTER")
    # corte C-C del chavetero
    cx, cy = 196.0, 166.0
    titulo_vista(msp, "C-C  ESC. 1:2", cx - 12, cy + 30, 3.0)
    circulo(msp, (cx, cy), 25 * k2, "CONTORNO")
    rect(msp, cx - 7 * k2, cy + (25 - 5.5) * k2, cx + 7 * k2, cy + 25.6 * k2, "CONTORNO")
    linea(msp, (cx - 16, cy), (cx + 16, cy), "EJES")
    linea(msp, (cx, cy - 16), (cx, cy + 16), "EJES")
    cota(msp, (cx - 7 * k2, cy + 25 * k2), (cx + 7 * k2, cy + 25 * k2), 5, k2, valor="14 P9")
    cota(msp, (cx + 7 * k2, cy - 25 * k2), (cx + 7 * k2, cy + 19.5 * k2), 13, k2, valor="44,5")
    # ---- eje de reenvío 4.3.1 (Rev. E): Ø50 300 + Ø60 2.500 + Ø50 300
    rx, ry = 40.0, 120.0
    _eje(msp, rx, ry, k, [(300, 50), (2500, 60), (300, 50)], "D - EJE DE REENVÍO 4.3.1 (3 piezas, REV. E)  -  ESC. 1:10")
    R_ = lambda u: rx + u * k
    for uc, txt in ((180, "UCT 210"), (506, "cubo"), (2594, "cubo"), (2920, "UCT 210")):
        linea(msp, (R_(uc), ry - 6), (R_(uc), ry + 6), "EJES")
        t(msp, txt, (R_(uc), ry + 8.5), 1.8, "BOTTOM_CENTER")
    cota(msp, (R_(0), ry - 3), (R_(3100), ry - 3), -17, k)
    for a, b in ((0, 300), (300, 2800), (2800, 3100)):
        cota(msp, (R_(a), ry - 3), (R_(b), ry - 3), -10, k)
    t(msp, "Ø50 h7", (R_(150), ry + 4), 1.9, "BOTTOM_CENTER")
    t(msp, "Ø60 h8 (entre cubos)", (R_(1550), ry + 4), 1.9, "BOTTOM_CENTER")
    t(msp, "Ø50 h7", (R_(2950), ry + 4), 1.9, "BOTTOM_CENTER")
    t(msp, "escalones r = 2", (R_(300) + 1, ry + 12), 1.8, "BOTTOM_LEFT")
    # ---- tabla de fatiga por sección y notas de fabricación
    em = FAT["eje_motriz"]
    filas = [["Secc.", "Ubicación", "Kf", "Se MPa", "σa MPa", "n Goodman"]]
    for s in em["secciones"]:
        filas.append([s["cod"], s["seccion"][:40], coma(s["Kf"], 2), coma(s["Se"], 0), coma(s["vm_a"], 1),
                      coma(s["n_goodman"], 2)])
    for c in FAT["eje_reenvio"]["casos"]:
        filas.append(["R", "reenvío: " + c["caso"][:31], coma(c["Kf"], 2), coma(c["Se"], 0), coma(c["sigma_a"], 1),
                      coma(c["n"], 2)])
    subtitulo(msp, "VERIFICACIÓN A FATIGA (SHIGLEY-BUDYNAS, DE-GOODMAN, n ≥ 1,5)", 232, 196)
    tabla(msp, 232, 194, [10, 76, 12, 15, 15, 17], filas, h_fila=4.2, altura=1.9,
          alin=["C", "L", "R", "R", "R", "R"], sombras={5: ROJO_SUAVE, 6: VERDE})
    notas(msp, [
        f"Material: SAE 1045 laminado en caliente (Sut {em['Sut']} MPa, Sy {em['Sy']} MPa).",
        "Tolerancias generales ISO 2768-mK. Rugosidad general Ra 3,2; asientos de cubo Ra 0,8.",
        "Chaflanes 2 × 45° en los extremos. Radios de acuerdo r = 2 mm pulidos, sin marcas.",
        "Rectitud ≤ 0,1 mm/m (enderezar en prensa antes de rectificar).",
        "END: partículas magnéticas (ISO 9934-1) en escalones y chavetero antes del montaje.",
        f"Par de atasco sin límite {coma(em['atasco']['T_atasco'], 0)} N·m (n = {coma(em['atasco']['n'], 1)}): el VFD limita",
        f"el par a {coma(em['atasco']['T_limite_VFD'], 0)} N·m en el eje (150 %) → n = {coma(em['atasco']['n_limite'], 1)} (ver SC-04).",
        "Protección: aceite antióxido y papel VCI hasta el montaje.",
    ], 232, 154, altura=1.95, interlineado=1.5, titulo="NOTAS DE FABRICACIÓN")
    # materia prima y secuencia de mecanizado
    filas_m = [["Pieza", "Materia prima (por eje)", "Cant."],
               ["Eje motriz 4.2.1", "barra SAE 1045 HR Ø65 × 3.020", "3"],
               ["Eje de reenvío 4.3.1", "barra SAE 1045 HR Ø65 × 3.120", "3"],
               ["Chaveta corona", "14 × 9 × 63 DIN 6885 A, C45", "3"],
               ["Repuesto (recomendado)", "1 eje motriz + 1 de reenvío terminados", "2"]]
    subtitulo(msp, "MATERIA PRIMA", 40, 86)
    tabla(msp, 40, 84, [38, 66, 12], filas_m, h_fila=4.0, altura=1.9, alin=["L", "L", "C"])
    notas(msp, ["1. Refrentar y hacer centros. 2. Desbaste en torno dejando 1 mm.",
                "3. Enderezar (≤ 0,1 mm/m). 4. Torneado de terminación y radios r = 2.",
                "5. Fresado del chavetero. 6. Rectificado de los asientos de cubo (Ra 0,8).",
                "7. Control dimensional y de rectitud entre puntas. 8. END por partículas.",
                "9. Protección y marcado (n.° de pieza y colada)."],
          40, 57, altura=1.9, interlineado=1.5, titulo="SECUENCIA DE MECANIZADO")
    return guardar(doc, 3)


# ================================================================ SC-04 fatiga
def _ejes_graf(msp, x0, y0, w, h, xt, yt):
    poli(msp, [(x0, y0 + h), (x0, y0), (x0 + w, y0)], "CONTORNO")
    t(msp, xt, (x0 + w, y0 - 6.5), 2.0, "TOP_RIGHT")
    t(msp, yt, (x0 - 1, y0 + h + 2), 2.0, "BOTTOM_LEFT")


def sc04():
    doc, msp, z = nueva(4, "SECADOR SC-4 - VERIFICACIÓN A\nFATIGA (SHIGLEY-BUDYNAS)", "S/E")
    em = FAT["eje_motriz"]
    sut, sy = em["Sut"], em["Sy"]
    # ---- A: diagrama de Goodman modificado (σa - σm), eje motriz
    gx, gy, gw, gh = 40.0, 172.0, 120.0, 90.0
    titulo_vista(msp, "A - DIAGRAMA DE GOODMAN MODIFICADO - EJE MOTRIZ", 28, 278, 3.0)
    sm_max, sa_max = 600.0, 340.0
    X = lambda sm: gx + sm / sm_max * gw
    Y = lambda sa: gy + sa / sa_max * gh
    _ejes_graf(msp, gx, gy, gw, gh, "σm' (MPa)", "σa' (MPa)")
    for v in range(100, 601, 100):
        linea(msp, (X(v), gy), (X(v), gy - 1.2), "FINO")
        t(msp, str(v), (X(v), gy - 2), 1.7, "TOP_CENTER")
        linea(msp, (X(v), gy), (X(v), Y(sa_max)), "AUXILIAR")
    for v in range(50, 341, 50):
        linea(msp, (gx, Y(v)), (gx - 1.2, Y(v)), "FINO")
        t(msp, str(v), (gx - 2, Y(v)), 1.7, "MIDDLE_RIGHT")
        linea(msp, (gx, Y(v)), (X(sm_max), Y(v)), "AUXILIAR")
    s1 = em["secciones"][0]
    se = s1["Se"]
    linea(msp, (X(0), Y(se)), (X(sut), Y(0)), "CONTORNO", color=(31, 119, 180))
    linea(msp, (X(0), Y(se / 1.5)), (X(sut / 1.5), Y(0)), "CONTORNO", color=(31, 119, 180))
    linea(msp, (X(0), Y(sy)), (X(sy), Y(0)), "CONTORNO", color=(200, 30, 30))
    t(msp, f"Goodman Se = {coma(se, 0)} (S1)", (X(40), Y(se) + 2), 1.8, "BOTTOM_LEFT")
    t(msp, "n = 1,5", (X(sut / 1.5) - 3, Y(12)), 1.8, "BOTTOM_RIGHT")
    t(msp, f"fluencia de Langer Sy = {sy}", (X(0) + 2, Y(sy) + 1.5), 1.8, "BOTTOM_LEFT")
    for s in em["secciones"]:
        p = (X(s["vm_m"]), Y(s["vm_a"]))
        relleno(msp, [(p[0] - 1.2, p[1] - 1.2), (p[0] + 1.2, p[1] - 1.2), (p[0] + 1.2, p[1] + 1.2),
                      (p[0] - 1.2, p[1] + 1.2)], (200, 30, 30))
        t(msp, s["cod"], (p[0], p[1] + 2), 1.8, "BOTTOM_CENTER")
    t(msp, "puntos (σm', σa') de von Mises: " + " · ".join(f"{s['cod']} n = {coma(s['n_goodman'], 2)}"
                                                           for s in em["secciones"]),
      (X(110), Y(250)), 1.8, "MIDDLE_LEFT")
    for c in FAT["eje_reenvio"]["casos"]:
        p = (X(0), Y(c["sigma_a"]))
        circulo(msp, (p[0] + 1.6, p[1]), 1.2, "CONTORNO")
        t(msp, f"reenvío Ø{c['d']} n = {coma(c['n'], 2)}", (p[0] + 3.5, p[1]), 1.8, "MIDDLE_LEFT")
    # ---- B: curva de Wöhler (S-N) log-log del SAE 1045 y ensayo de probetas
    wx, wy, ww, wh = 225.0, 172.0, 150.0, 90.0
    titulo_vista(msp, "B - CURVA S-N (WÖHLER) SAE 1045 Y PLAN DE ENSAYO", 213, 278, 3.0)
    wo = FAT["wohler"]
    lx = lambda n: wx + (math.log10(n) - 3) / 5 * ww             # 10³ a 10⁸ ciclos
    ly = lambda s: wy + (math.log10(s) - 2) / (math.log10(700) - 2) * wh   # 100 a 700 MPa
    _ejes_graf(msp, wx, wy, ww, wh, "N (ciclos)", "S (MPa)")
    for e in range(3, 9):
        linea(msp, (lx(10 ** e), wy), (lx(10 ** e), wy - 1.2), "FINO")
        linea(msp, (lx(10 ** e), wy), (lx(10 ** e), ly(700)), "AUXILIAR")
        t(msp, "10" + str(e).translate(SUP), (lx(10 ** e), wy - 2), 1.9, "TOP_CENTER")
    for s in (100, 150, 200, 300, 400, 500, 700):
        linea(msp, (wx, ly(s)), (wx - 1.2, ly(s)), "FINO")
        linea(msp, (wx, ly(s)), (lx(1e8), ly(s)), "AUXILIAR")
        t(msp, str(s), (wx - 2, ly(s)), 1.7, "MIDDLE_RIGHT")
    a, b = wo["a"], wo["b"]
    pts = [(lx(n), ly(a * n ** b)) for n in [10 ** (3 + i * 0.1) for i in range(31)]]
    pts.append((lx(1e8), ly(wo["Se_prima"])))
    poli(msp, pts, "CONTORNO", color=(31, 119, 180))
    t(msp, f"probeta pulida: log S = log {coma(a, 1)} {coma(b, 4)}·log N;  Se' = 0,5·Sut = {coma(wo['Se_prima'], 0)}",
      (lx(1.2e3), ly(a * 1.2e3 ** b) + 3), 1.8, "BOTTOM_LEFT")
    # componente (S1): Se de Marin
    f_ = wo["f"]
    a_c = (f_ * sut) ** 2 / se
    b_c = -math.log10(f_ * sut / se) / 3
    ptc = [(lx(n), ly(a_c * n ** b_c)) for n in [10 ** (3 + i * 0.1) for i in range(31)]] + [(lx(1e8), ly(se))]
    poli(msp, ptc, "OCULTAS", color=(200, 30, 30))
    t(msp, f"eje motriz S1 (Marin): Se = {coma(se, 0)} MPa", (lx(1e6) + 2, ly(se) - 2), 1.8, "TOP_LEFT")
    # vida requerida
    nv = em["ciclos_vida"]
    linea(msp, (lx(nv), wy), (lx(nv), ly(700)), "EJES")
    t(msp, f"vida del eje: {coma(nv / 1e6, 2)}·10⁶ ciclos (20 años)", (lx(nv) + 1, ly(640)), 1.7, "MIDDLE_LEFT")
    for niv in wo["niveles"]:
        try:
            n = float(niv["N"])
        except ValueError:
            n = 1e7
            circulo(msp, (lx(n), ly(niv["S"])), 1.0, "CONTORNO")
            continue
        relleno(msp, [(lx(n) - 1, ly(niv["S"]) - 1), (lx(n) + 1, ly(niv["S"]) - 1), (lx(n) + 1, ly(niv["S"]) + 1),
                      (lx(n) - 1, ly(niv["S"]) + 1)], (40, 40, 40))
    t(msp, f"■ niveles del ensayo ({wo['probetas']} probetas, flexión rotativa)  ○ sin rotura a 10⁷",
      (wx + 2, wy + 3), 1.7, "BOTTOM_LEFT")
    # ---- C: tabla resumen de todos los componentes
    at = em["atasco"]
    ch, ca, rod, me, an = FAT["chaveta"], FAT["cadena"], FAT["rodamientos"], FAT["mensula"], FAT["anclajes"]
    reen = FAT["eje_reenvio"]["casos"]
    filas = [["Componente", "Criterio", "n", "Resultado"],
             ["Eje motriz - S1 asiento rectificado", "DE-Goodman", coma(em["n_min"], 2), "verifica"],
             ["Eje motriz - S1 si queda torneado", "DE-Goodman", coma(em["S1_torneado"]["n_goodman"], 2), "no (< 1,5)"],
             ["Eje motriz - atasco sin limitar", "fluencia en torsión", coma(at["n"], 1), "no: límite VFD"],
             [f"Eje motriz - atasco, VFD {at['T_limite_VFD']} N·m", "fluencia en torsión", coma(at["n_limite"], 1), "verifica"],
             ["Eje reenvío Ø50 (diseño anterior)", "DE-Goodman", coma(reen[0]["n"], 2), "no → Rev. E"],
             ["Eje reenvío Ø60 / muñones Ø50", "DE-Goodman", coma(reen[1]["n"], 2), "verifica"],
             ["Chaveta 14 × 9 × 63", "fatiga / aplastam.", f"{coma(ch['n_fatiga'], 1)} / {coma(ch['n_aplast'], 1)}", "verifica"],
             ["Cadena ASA 60 (Tsubaki RS60)", "carga adm. a fatiga", coma(ca["n_fatiga"], 2), "verifica"],
             ["UCF 212 / UCT 210", "L10 y s0 estático", f"s0 ≥ {coma(min(r['s0'] for r in rod['filas']), 1)}", "verifica"],
             ["Ménsula PL 12 (soldadura)", "Goodman en corte", coma(me["n"], 1), "verifica"],
             ["Anclajes M16 (corte por banda)", "uso de V_Rd", f"{coma(an['secador']['uso_V_pct'], 1)} %", "verifica"],
             ["Bulones ventilador (G 6,3)", "Goodman bulón 8.8", coma(an["ventilador"]["n_f"], 0), "verifica"]]
    sombra = {i: (ROJO_SUAVE if filas[i][3].startswith("no") else VERDE) for i in range(1, len(filas))}
    subtitulo(msp, "C - RESUMEN DE COEFICIENTES DE SEGURIDAD (n admisible = 1,5)", 28, 150)
    tabla(msp, 28, 148, [62, 34, 18, 26], filas, h_fila=4.2, altura=1.9, alin=["L", "L", "R", "L"], sombras=sombra)
    # ---- D: datos y método
    mar = em["secciones"][0]["marin"]
    notas(msp, [
        f"Servicio: {FAT['servicio']['horas_dia']:g} h/día × {FAT['servicio']['dias_anio']} días × {FAT['servicio']['anios']} años; confiabilidad {FAT['confiabilidad']} %.",
        f"Eje motriz: T = {coma(em['T'], 0)} N·m, n = {coma(em['rpm'], 3)} rpm, fluctuación de par ±{int(em['fluct'] * 100)} %.",
        "Flexión rotativa: σa = M·c/I; torsión casi constante: τm = 16 T/πd³ (DE: von Mises).",
        f"Se' = 0,5·Sut = {coma(em['Se_prima'], 0)} MPa; Se = ka·kb·kc·kd·ke·kf·Se' (Marin), S1:",
        f"ka {coma(mar['ka'], 3)} (rectificado) · kb {coma(mar['kb'], 3)} · kd {coma(mar['kd'], 2)} (100 °C) · ke {coma(mar['ke'], 3)} (99 %) · kf {coma(mar['kf'], 2)} (corrosión).",
        "Kf = 1 + q (Kt − 1), q de Neuber; Goodman: 1/n = σa'/Se + σm'/Sut.",
        "Bibliografía: Budynas-Nisbett, Diseño en ingeniería mecánica de Shigley, 8.ª ed., cap. 6, 7 y 8;",
        "apunte de cátedra INET (ensayos destructivos: fatiga por flexión rotativa, curva de Wöhler).",
    ], 175, 148, altura=1.95, interlineado=1.5, titulo="D - MÉTODO Y DATOS")
    filas_e = [["Nivel", "S MPa", "S/Sut", "N esperado"]]
    for i, niv in enumerate(wo["niveles"][:12], 1):
        filas_e.append([str(i), str(niv["S"]), coma(niv["frac"], 2), pot10(niv["N"])])
    subtitulo(msp, "E - PLAN DE ENSAYO DE WÖHLER", 175, 113)
    tabla(msp, 175, 111, [11, 13, 13, 26], filas_e[:7], h_fila=3.6, altura=1.7, alin=["C", "R", "R", "L"])
    tabla(msp, 175 + 66, 111, [11, 13, 13, 30], [filas_e[0]] + filas_e[7:], h_fila=3.6, altura=1.7,
          alin=["C", "R", "R", "L"])
    t(msp, "Probetas Ø7,5 pulidas de la misma barra SAE 1045 de los ejes; flexión rotativa (R = −1).",
      (175, 82.5), 1.7, "TOP_LEFT")
    return guardar(doc, 4)


# ================================================================ SC-05 bastidor y fijación al piso
def sc05():
    doc, msp, z = nueva(5, "SECADOR SC-4 - BASTIDOR, REPLANTEO\nY FIJACIÓN AL PISO", "1:75 / 1:5")
    k = factor("1:75")
    v = proyectar("estructura", ["frente", "planta"])
    cf = v["frente"]["caja"]
    x0, yf = 36.0, 214.0
    dxf, dyf = x0 - cf[0] * k, yf - cf[1] * k
    dibujar(msp, v["frente"]["visibles"], k, dxf, dyf)
    F = lambda x, zz: (x * k + dxf, zz * k + dyf)
    linea(msp, F(-600, 0), F(13600, 0), "CONTORNO")
    titulo_vista(msp, "A - ESTRUCTURA, VISTA FRONTAL (SUR)  -  ESC. 1:75", x0, F(0, 3500)[1] + 4, 3.0)
    for zz, txt in ((2630, "+2,63 piso 1"), (1780, "+1,78 piso 2"), (930, "+0,93 piso 3"), (3400, "+3,40")):
        nivel(msp, F(13000, 0)[0] + 2, F(0, zz)[1], txt)
    cota(msp, F(0, 0), F(13000, 0), -8, k)
    # plantilla de replanteo (planta 1:75)
    yp = 150.0
    P = lambda x, y: (x0 + x * k, yp + y * k)
    titulo_vista(msp, "B - PLANTILLA DE REPLANTEO SOBRE LA PLATEA  -  ESC. 1:75", x0, yp + 2600 * k + 15, 3.0)
    dibujar(msp, v["planta"]["visibles"], k, x0, yp)
    xs = (60, 3250, 6500, 9750, 12940)
    for i, xc in enumerate(xs):
        linea(msp, P(xc, -900), P(xc, 3300), "EJES")
        circulo(msp, (P(xc, 0)[0], P(0, -1300)[1]), 2.5, "COTAS")
        tn(msp, "ABCDE"[i], (P(xc, 0)[0], P(0, -1300)[1]), 2.4, "MIDDLE_CENTER")
    for j, yc in enumerate((30, 2570)):
        linea(msp, P(-700, yc), P(13700, yc), "EJES")
        circulo(msp, (P(-1100, 0)[0], P(0, yc)[1]), 2.5, "COTAS")
        tn(msp, "12"[j], (P(-1100, 0)[0], P(0, yc)[1]), 2.4, "MIDDLE_CENTER")
    linea(msp, P(60, 30), P(12940, 2570), "AUXILIAR", color=(200, 30, 30))
    linea(msp, P(60, 2570), P(12940, 30), "AUXILIAR", color=(200, 30, 30))
    diag = math.hypot(12880, 2540)
    t(msp, f"diagonales A1-E2 = A2-E1 = {coma(diag / 1000, 3)} m (± 3 mm)", P(4500, 1500), 1.9, "BOTTOM_LEFT")
    for a, b in zip(xs, xs[1:]):
        cota(msp, P(a, 2570), P(b, 2570), 6, k)
    cota(msp, P(12940, 30), P(12940, 2570), -9, k)
    # detalle C: placa base y anclaje químico (1:5)
    k5 = factor("1:5")
    cx, cy = 264.0, 212.0
    titulo_vista(msp, "C - PLACA BASE Y ANCLAJE QUÍMICO  -  ESC. 1:5", 228, 275, 3.0)
    D = lambda u, w: (cx + u * k5, cy + w * k5)
    # platea H-21 (e = 200) con rayado de hormigón
    relleno_rect(msp, D(-190, -230)[0], D(0, -230)[1], D(190, 0)[0], D(0, 0)[1], COL["hormigon"])
    rayado(msp, [D(-190, -230), D(190, -230), D(190, -20), D(-190, -20)], escala=0.03, patron="AR-CONC", angulo=0)
    linea(msp, D(-190, 0), D(190, 0), "CONTORNO")
    t(msp, "platea H-21 e = 20 cm, malla Q188", D(-185, -224), 1.8, "BOTTOM_LEFT")
    # grout 20 mm y placa 12 mm
    relleno_rect(msp, D(-110, 0)[0], D(0, 0)[1], D(110, 20)[0], D(0, 20)[1], (190, 190, 185))
    rect(msp, D(-110, 0)[0], D(0, 0)[1], D(110, 20)[0], D(0, 20)[1], "FINO")
    relleno_rect(msp, D(-100, 20)[0], D(0, 20)[1], D(100, 32)[0], D(0, 32)[1], (150, 155, 160))
    rect(msp, D(-100, 20)[0], D(0, 20)[1], D(100, 32)[0], D(0, 32)[1], "CONTORNO")
    # columna UPN 120 (alma) soldada, cortada con línea de rotura
    poli(msp, [D(-60, 220), D(-60, 32), D(60, 32), D(60, 220)], "CONTORNO")
    linea(msp, D(-53, 32), D(-53, 220), "FINO")
    poli(msp, [D(-66, 220), D(-20, 220), D(-12, 232), D(-4, 208), D(4, 220), D(66, 220)], "FINO")
    for s in (-1, 1):
        poli(msp, [D(s * 60, 32), D(s * 66, 32), D(s * 60, 38)], "CONTORNO", cerrada=True)
    t(msp, "UPN 120 - filete 6 mm todo alrededor (E7018)", D(70, 150), 1.8, "MIDDLE_LEFT")
    # varillas M16 (dos de las cuatro en el corte) con resina y tuercas
    for u in (-70, 70):
        relleno_rect(msp, D(u - 9, -135)[0], D(0, -135)[1], D(u + 9, 0)[0], D(0, 0)[1], (225, 205, 120))
        rect(msp, D(u - 8, -135 + 5)[0], D(0, -130)[1], D(u + 8, 64)[0], D(0, 64)[1], "CONTORNO")
        rect(msp, D(u - 15, 32)[0], D(0, 32)[1], D(u + 15, 35)[0], D(0, 35)[1], "CONTORNO")
        rect(msp, D(u - 12, 35)[0], D(0, 35)[1], D(u + 12, 49)[0], D(0, 49)[1], "CONTORNO")
    cota(msp, D(-70, -130), D(-70, 0), 15, k5, valor="h_ef 125")
    cota(msp, D(-79, -135), D(-61, -135), -5, k5, valor="Ø18")
    cota(msp, D(-70, 64), D(70, 64), 8, k5)
    cota(msp, D(-100, 20), D(100, 20), -14, k5)
    cota(msp, D(-110, 0), D(-110, 20), -6, k5, valor="20")
    cota(msp, D(100, 20), D(100, 32), 6, k5, valor="12")
    for txt, w, apunta in (("resina epoxi (inyectada desde el fondo)", -110, D(79, -100)),
                           ("grout sin contracción e = 20 mm", 10, D(105, 10)),
                           ("tuerca M16 + arandela, 80 N·m", 45, D(82, 42))):
        t(msp, txt, (D(200, 0)[0] + 1, D(0, w)[1]), 1.8, "MIDDLE_LEFT")
        flecha(msp, (D(200, 0)[0], D(0, w)[1]), apunta, "COTAS")
    # planta de la placa
    px0, py0 = 384.0, 236.0
    Q = lambda u, w: (px0 + u * k5, py0 + w * k5)
    titulo_vista(msp, "PLANTA DE LA PLACA", 362, 268, 2.4)
    rect(msp, *Q(-100, -100), *Q(100, 100), "CONTORNO")
    for du in (-70, 70):
        for dw in (-70, 70):
            circulo(msp, Q(du, dw), 9 * k5, "CONTORNO")
            linea(msp, Q(du - 14, dw), Q(du + 14, dw), "EJES")
            linea(msp, Q(du, dw - 14), Q(du, dw + 14), "EJES")
    cota(msp, Q(-100, -100), Q(100, -100), -5, k5)
    cota(msp, Q(-70, 100), Q(70, 100), 5, k5)
    t(msp, "PL 200×200×12 F-24, 4 × Ø18", Q(-100, -100 - 70), 1.8, "TOP_LEFT")
    # verificación de los anclajes
    an = FAT["anclajes"]["secador"]
    ms = FAT["anclajes"]["masa"]
    filas = [["Verificación (por placa)", "Valor"],
             ["Masa del equipo / con producto", f"{coma(ms['total_kg'], 0)} / {coma(an['m_kg'], 0)} kg"],
             ["Control con el modelo 3D", f"{coma(ms.get('modelo_cad_kg', 0), 0)} kg ({coma(ms.get('dif_cad_pct', 0), 1)} %)"],
             ["Compresión por placa", f"{coma(an['V_placa_kN'], 1)} kN → σ = {coma(an['sigma_apoyo_MPa'], 2)} MPa"],
             ["Esfuerzo horizontal total (tiro de bandas)", f"{coma(an['H_total_N'], 0)} N"],
             ["Resistencia de cálculo por varilla", f"N_Rd {coma(an['N_Rd'], 0)} kN · V_Rd {coma(an['V_Rd'], 0)} kN"],
             ["Uso al corte", f"{coma(an['uso_V_pct'], 1)} % (verifica)"],
             ["Par de instalación / pretensado", f"{coma(an['T_inst'], 0)} N·m / {coma(an['F_pre_kN'], 0)} kN"]]
    tabla(msp, 230, 158, [92, 80], filas, h_fila=4.2, altura=1.9, alin=["L", "L"])
    notas(msp, [
        "Replanteo: marcar los ejes A-E y 1-2 con tiza de línea y nivel láser; controlar diagonales.",
        "Perforar Ø18 × 135 con taladro percutor (sin vibrar la mecha); limpiar: 2 soplados + 2 cepillados",
        "+ 2 soplados. Inyectar la resina desde el fondo (2/3 del agujero) y colocar la varilla girando.",
        "Curado antes de cargar: según el fabricante (≈ 24 h a 20 °C; el doble con < 10 °C).",
        "Distancia al borde de la platea ≥ 150 mm; separación entre anclajes 140 mm (≥ 2 h_ef con cono).",
        "Nivelar las placas con cuñas a ± 1 mm, llenar con grout de 20 mm y apretar después del fraguado.",
        "Columnas a plomo ± 2 mm en 3,4 m. Ensayo de arrancamiento de 1 de cada 10 anclajes (SC-04/inf.).",
    ], 230, 117, altura=1.85, interlineado=1.5, titulo="PROCEDIMIENTO DE FIJACIÓN")
    # materiales de la fijación y ensayo de los anclajes
    filas_m = [["Material de la fijación", "Cantidad"],
               ["Varilla roscada M16 × 190 clase 5.8 zincada + tuerca + arandela", "40 juegos"],
               ["Resina epoxi para anclajes (cartucho 585 ml)", "3 cartuchos"],
               ["Placa base PL 200 × 200 × 12 F-24, 4 agujeros Ø18", "10"],
               ["Mortero de relleno sin contracción (grout)", "1 bolsa 25 kg"],
               ["Cuñas de nivelación de acero 50 × 30 × 3/6", "40"],
               ["Mecha SDS Ø18 × 200 y cepillo Ø18", "1 + 1"]]
    subtitulo(msp, "D - MATERIALES DE LA FIJACIÓN", 36, 120)
    tabla(msp, 36, 118, [120, 30], filas_m, h_fila=4.0, altura=1.9, alin=["L", "L"])
    notas(msp, ["Ensayo de verificación (1 de cada 10 anclajes, sin dañar la platea): carga de tracción",
                f"de prueba 15 kN ≈ 0,6·N_Rd ({coma(an['N_Rd'], 0)} kN) durante 2 min con gato hueco y comparador;",
                "aceptación: desplazamiento < 0,5 mm y sin fisuras en el hormigón. Si falla uno, ensayar todos."],
          36, 84, altura=1.85, interlineado=1.5, titulo="E - ENSAYO DE ARRANCAMIENTO")
    return guardar(doc, 5)


# ================================================================ SC-06 montaje paso a paso
def _cortar(texto, ancho_chars):
    palabras, renglones, actual = texto.split(), [], ""
    for p in palabras:
        if len(actual) + len(p) + 1 > ancho_chars:
            renglones.append(actual)
            actual = p
        else:
            actual = (actual + " " + p).strip()
    if actual:
        renglones.append(actual)
    return renglones


def _recorte(ruta, aspecto):
    """Recorta el cielo de arriba de la captura para llevarla a la proporción ancho/alto pedida."""
    from PIL import Image
    destino = os.path.join(CARPETA, "dxf", "img", "SC06_" + os.path.basename(ruta))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with Image.open(ruta) as im:
        w, h = im.size
        h2 = int(round(w / aspecto))
        im.crop((0, h - h2 - int((h - h2) * 0.25), w, h - int((h - h2) * 0.25))).convert("RGB").save(destino)
    return destino


def sc06():
    doc, msp, z = nueva(6, "SECADOR SC-4 - MONTAJE\nPASO A PASO (MANUAL DE ARMADO)", "S/E")
    W, IH, CH = 73.0, 39.0, 61.5
    xs = [27 + i * (W + 2.6) for i in range(5)]
    ys = [282 - CH * (j + 1) for j in range(4)]
    celdas = [(x, ys[0]) for x in xs] + [(x, ys[1]) for x in xs] + [(x, ys[2]) for x in xs]
    for i, paso in enumerate(PASOS):
        x, y = celdas[i]
        ruta = _recorte(os.path.join(RENDERS, "montaje", f"paso_{i + 1:02d}.png"), W / IH)
        imagen(doc, msp, ruta, x, y + CH - IH - 0.5, W, IH, carpeta_planos=CARPETA)
        tit = paso["titulo"]
        tn(msp, tit, (x, y + CH - IH - 3.0), min(2.0, W / (0.7 * len(tit))), "MIDDLE_LEFT")
        renglones = _cortar(paso["texto"], 78)
        for r, ren in enumerate(renglones[:8]):
            t(msp, ren, (x, y + CH - IH - 5.4 - r * 2.15), 1.42, "TOP_LEFT")
    # celdas 14 y 15: controles y herramientas
    x, y = celdas[13]
    filas = [["Control final", "Tolerancia"],
             ["Diagonales de la planta", "± 3 mm"],
             ["Plomo de columnas", "± 2 mm / 3,4 m"],
             ["Nivel de travesaños de un piso", "± 1 mm"],
             ["Escuadra de los ejes de tambor", "≤ 1 mm/m"],
             ["Desalineación de ruedas", "< 1 mm"],
             ["Flecha de la cadena", "≈ 2 % de c"],
             ["Tensión de banda T2", "≈ 2.000 N"],
             ["Capa de guano (compuerta)", "30 mm"],
             ["Par anclajes M16", "80 N·m"],
             ["Prueba de carga pasarela", "1,5 × 2 kN/m²"],
             ["Marcha en vacío (cada banda)", "4 h"],
             ["Vibraciones (ISO 20816-3)", "zona A/B"]]
    tabla(msp, x, y + CH - 1, [W * 0.66, W * 0.34 + W + 2.6], filas, h_fila=4.1, altura=1.75, alin=["L", "L"])
    notas(msp, [
        "SEGURIDAD EN EL MONTAJE (Ley 19.587, Dec. 351/79 y 911/96):",
        "· Casco, calzado de seguridad, guantes y protección ocular en todo el montaje.",
        "· Trabajo en altura > 2 m con arnés y línea de vida hasta montar la pasarela y su baranda.",
        "· Izajes con grúa o autoelevador habilitado; eslingas revisadas; nadie debajo de la carga.",
        "· Soldadura con permiso de trabajo en caliente, matafuego ABC a mano y biombos.",
        "· Antes de energizar: cárteres colocados, puertas con microinterruptor y paradas de emergencia probadas.",
        "· Bloqueo y etiquetado (LOTO) de TG/VFD para cualquier intervención posterior.",
        "El manual completo con fotos grandes y listas de control está en secadora/Manual_de_armado_SC4.pdf.",
    ], 27, ys[3] + CH - 4, altura=1.9, interlineado=1.55)
    return guardar(doc, 6)


# ================================================================ juego del secador
def juego(numeros):
    fn = {1: sc01, 2: sc02, 3: sc03, 4: sc04, 5: sc05, 6: sc06}
    for n in numeros:
        print("SC-%02d" % n, fn[n]())
    pdfs = [os.path.join(CARPETA, "pdf", f"SC-{n:02d}.pdf") for n in range(1, 7)]
    general = os.path.join(RAIZ, "planos", "pdf")
    pdfs += [os.path.join(general, f"P{n:02d}.pdf") for n in (2, 3, 9, 22)]
    faltan = [p for p in pdfs if not os.path.exists(p)]
    if faltan:
        print("faltan:", faltan)
        return
    salida = unir_pdfs(pdfs, os.path.join(CARPETA, "pdf", "Planos_Secador_SC4.pdf"))
    print("juego del secador:", salida)


if __name__ == "__main__":
    os.chdir(AQUI)
    juego([int(x) for x in sys.argv[1:]] or list(range(1, 7)))
