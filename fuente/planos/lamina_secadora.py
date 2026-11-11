"""Lámina A3 del proyecto Secadora de guano (rótulo de la escuela) sobre lamina_a3.py.

Reproduce el formato de las láminas del proyecto: recuadro con márgenes de 20 mm a la
izquierda y 10 mm en el resto, marcas de centrado, tabla de revisiones y rótulo de la
E.P.N.M. y S. N° 35 con escala, formato, plano N°, revisión, firmas, hoja x/24 e integrantes.
Exporta DXF (AutoCAD), PDF A3 vectorial y el PNG que muestra el visor (planos/Pxx.png).

    from lamina_secadora import *
    doc, msp, z = lamina(23, "ESQUEMA UNIFILAR TG2\\n(CONSUMOS NUEVOS REV. D)", "S/E",
                         [("D", "09/2026", "Emisión original"), ("E", FECHA, "Se agregan EX1-EX2")])
    titulo_vista(msp, "A - ESQUEMA", 30, 278)
    tabla(msp, 230, 250, [20, 80, 20], [["Tag", "Equipo", "kW"], ["M16", "Hidrolavadora", "4,00"]])
    exportar_lamina(doc, 23)

Coordenadas en mm de papel: la hoja va de (0, 0) a (420, 297). z["dibujo"] es el interior
del recuadro y z["reservado"] el rótulo con las revisiones (no dibujar encima).
"""
from __future__ import annotations

import math
import os
import shutil
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lamina_a3  # noqa: E402
from lamina_a3 import cota, cota_diametro, factor, unir_pdfs  # noqa: E402,F401

# ---------------------------------------------------------------- datos del proyecto
INSTITUCION = 'E.P.N.M. y S. N° 35 Técnica "Gral. Don José de San Martín" - Crespo, Entre Ríos'
CURSO = "PROYECTO FINAL - 7° AÑO TÉCNICO ELECTROMECÁNICO - 2026"
PROYECTO = "SECADORA DE GUANO DE GALLINA 8 t/día"
INTEGRANTES = "Integrantes: G. Müller · P. Hofstetter · B. Goette · F. Stegmann · M. Bernhardt · B. Belluzzo"
DIBUJO = "Grupo PF"
FECHA = "10/2026"
TOTAL_HOJAS = 24

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CARPETA_PLANOS = os.path.join(RAIZ, "planos")

ANCHO, ALTO = 420.0, 297.0
MARCO = (20.0, 10.0, 410.0, 287.0)
ROT_X0 = 230.0                      # rótulo: 180 mm de ancho, abajo a la derecha

# capas: (color ACI, espesor en centésimas de mm, tipo de línea). ACI 7 sale negro sobre blanco.
CAPAS = {
    "HOJA": (8, 13, "CONTINUOUS"),
    "RECUADRO": (7, 70, "CONTINUOUS"),
    "ROTULO": (7, 35, "CONTINUOUS"),
    "CONTORNO": (7, 50, "CONTINUOUS"),
    "FINO": (7, 25, "CONTINUOUS"),
    "OCULTAS": (8, 25, "DASHED"),
    "EJES": (1, 18, "CENTER"),
    "COTAS": (7, 25, "CONTINUOUS"),
    "RAYADO": (8, 18, "CONTINUOUS"),
    "RELLENO": (9, 13, "CONTINUOUS"),
    "TEXTO": (7, 25, "CONTINUOUS"),
    "AUXILIAR": (9, 13, "CONTINUOUS"),
}

# colores de uso frecuente en las láminas del proyecto (RGB)
COL = {
    "guano": (139, 90, 43), "aire_caliente": (214, 40, 40), "aire_frio": (31, 119, 180),
    "aire_agotado": (46, 139, 87), "humos": (110, 110, 110), "agua": (31, 150, 200),
    "biogas": (212, 167, 0), "recirc": (230, 120, 30), "incendio": (200, 16, 46),
    "salida": (11, 138, 67), "encabezado": (226, 232, 238), "zona_recepcion": (240, 230, 214),
    "zona_acopio": (236, 225, 200), "zona_gris": (225, 228, 230), "verde": (225, 238, 220),
    "amarillo_seg": (243, 194, 41), "hormigon": (215, 215, 210), "pavimento": (205, 210, 215),
    "ladrillo": (205, 160, 120), "inox": (215, 220, 225), "rojo": (200, 30, 30), "azul": (40, 90, 170),
}


# ---------------------------------------------------------------- lámina

_FUENTES_PIL = {}


def fuente_pil(negrita=True):
    """Arial de PIL para medir textos (a 1000 px). Sin Arial en el sistema (Linux) usa Liberation Sans, que
    tiene las mismas medidas (paquete fonts-liberation)."""
    if negrita not in _FUENTES_PIL:
        from PIL import ImageFont
        nombres = ["arialbd.ttf", "LiberationSans-Bold.ttf"] if negrita else ["arial.ttf", "LiberationSans-Regular.ttf"]
        for n in nombres + [os.path.expanduser("~/.fonts/" + nombres[0])]:
            try:
                _FUENTES_PIL[negrita] = ImageFont.truetype(n, 1000)
                break
            except OSError:
                continue
        else:
            raise OSError("No se encontró Arial ni Liberation Sans: instalar fonts-liberation (ver fuente/README.md)")
    return _FUENTES_PIL[negrita]


def lamina(numero, titulo, escala, revisiones, formato="A3", serie=None):
    """Crea la lámina N° numero (int) con el rótulo del proyecto.

    titulo: título del rótulo (admite '\\n' para dos renglones).
    revisiones: [(letra, fecha, descripción), ...] de la más vieja a la más nueva; la última
    es la revisión vigente.
    serie: para un juego aparte con numeración propia, p. ej. {"prefijo": "SC-", "total": 6}
    (plano N° SC-01, hoja 01/06). Sin serie: plano N° 01 y hoja x/24 del juego general.
    """
    doc = ezdxf.new("R2018", setup=True, units=4)
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 0.5
    doc.header["$PSLTSCALE"] = 0
    doc.styles.get("Standard").dxf.font = "arial.ttf"
    if "NEGRITA" not in doc.styles:
        doc.styles.add("NEGRITA", font="arialbd.ttf")
    for nombre, (color, lw, lt) in CAPAS.items():
        doc.layers.add(nombre, color=color, lineweight=lw,
                       linetype=lt if lt in doc.linetypes else "CONTINUOUS")
    lamina_a3._estilo_cotas(doc)
    doc.dimstyles.get("IRAM").dxf.dimtxsty = "Standard"
    msp = doc.modelspace()

    msp.add_lwpolyline([(0, 0), (ANCHO, 0), (ANCHO, ALTO), (0, ALTO)], close=True, dxfattribs={"layer": "HOJA"})
    x0, y0, x1, y1 = MARCO
    rect(msp, x0, y0, x1, y1, "RECUADRO")
    # marcas de centrado (IRAM 4504)
    for a, b in (((ANCHO / 2, ALTO - 5), (ANCHO / 2, y1)), ((ANCHO / 2, 5), (ANCHO / 2, y0)),
                 ((5, ALTO / 2), (x0, ALTO / 2)), ((ANCHO - 5, ALTO / 2), (x1, ALTO / 2))):
        msp.add_line(a, b, dxfattribs={"layer": "RECUADRO"})

    letra = revisiones[-1][0] if revisiones else "A"
    fecha = revisiones[-1][1] if revisiones else FECHA   # fecha de la revisión vigente
    tope = _rotulo(msp, numero, titulo, escala, letra, formato, fecha, serie)
    tope = _revisiones(msp, revisiones, tope)
    zonas = {
        "hoja": (0, 0, ANCHO, ALTO),
        "marco": MARCO,
        "dibujo": (x0 + 5, y0 + 5, x1 - 5, y1 - 5),
        "reservado": (ROT_X0, y0, x1, tope),
    }
    doc.set_modelspace_vport(height=ALTO * 1.05, center=(ANCHO / 2, ALTO / 2))
    return doc, msp, zonas


def _rotulo(msp, numero, titulo, escala, letra, formato, fecha=FECHA, serie=None):
    x0, y0, x1 = ROT_X0, MARCO[1], MARCO[2]
    L = lambda a, b: msp.add_line(a, b, dxfattribs={"layer": "ROTULO"})
    # renglones: integrantes 10-17 | firmas 17-24 | título 24-51 | escuela 51-62
    for y in (17, 24, 51, 62):
        L((x0, y), (x1, y))
    L((x0, y0), (x0, 62))
    t(msp, INTEGRANTES, (x0 + 2, 13.5), 2.5, "MIDDLE_LEFT", capa="ROTULO")
    # firmas
    cols = [x0, 246, 288, 305, 360, 369, 384, 392, x1]
    for c in cols[1:-1]:
        L((c, 17), (c, 24))
    for (a, b), val, h in ((cols[0:2], "Dibujó", 2.2), (cols[1:3], DIBUJO, 2.5), (cols[2:4], "Revisó", 2.2),
                           (cols[4:6], "Fecha", 1.9), (cols[5:7], fecha, 2.2), (cols[6:8], "Hoja", 1.9),
                           (cols[7:9], f"{numero:02d}/{serie['total'] if serie else TOTAL_HOJAS:02d}", 2.4)):
        if "/" in val and val[0].isdigit():
            t(msp, val, ((a + b) / 2, 20.5), h, "MIDDLE_CENTER", capa="ROTULO")
        else:
            t(msp, val, (a + 1.2, 20.5), h, "MIDDLE_LEFT", capa="ROTULO")
    # bloque de título
    L((360, 24), (360, 51))
    L((384, 24), (384, 51))
    L((360, 37.5), (x1, 37.5))
    t(msp, PROYECTO, (x0 + 2, 47.5), 3.0, "MIDDLE_LEFT", capa="ROTULO", estilo="NEGRITA")
    renglones = titulo.split("\n")
    h = 4.2 if len(renglones) == 1 else 3.8
    ancho_max = max(len(r) for r in renglones)
    h = min(h, 126 / (0.8 * ancho_max))     # mayúscula en negrita ≈ 0,8 × altura de ancho
    yc = 37.0 if len(renglones) == 1 else 39.0
    for i, r in enumerate(renglones):
        t(msp, r, (x0 + 2, yc - i * (h * 1.45)), h, "MIDDLE_LEFT", capa="ROTULO", estilo="NEGRITA")
    t(msp, "Método ISO E (IRAM 4501)", (x0 + 2, 27.5), 2.0, "MIDDLE_LEFT", capa="ROTULO")
    _simbolo_iso_e(msp, 305, 27.6)
    t(msp, "Cotas en mm (salvo indicación)", (317, 27.5), 2.0, "MIDDLE_LEFT", capa="ROTULO")
    t(msp, "Escala", (361.5, 49.3), 1.8, "TOP_LEFT", capa="ROTULO")
    t(msp, escala, (372, 42.5), min(3.6, 22 / (0.62 * max(len(escala), 1))), "MIDDLE_CENTER", capa="ROTULO", estilo="NEGRITA")
    t(msp, "Formato", (361.5, 35.8), 1.8, "TOP_LEFT", capa="ROTULO")
    t(msp, formato, (372, 29.5), 3.6, "MIDDLE_CENTER", capa="ROTULO", estilo="NEGRITA")
    t(msp, "Plano N°", (385.5, 49.3), 1.8, "TOP_LEFT", capa="ROTULO")
    if serie:
        t(msp, f"{serie['prefijo']}{numero:02d}", (397, 42.3), 4.3, "MIDDLE_CENTER", capa="ROTULO", estilo="NEGRITA")
    else:
        t(msp, f"{numero:02d}", (397, 42.3), 6.0, "MIDDLE_CENTER", capa="ROTULO", estilo="NEGRITA")
    t(msp, "Revisión", (385.5, 35.8), 1.8, "TOP_LEFT", capa="ROTULO")
    t(msp, letra, (397, 29.3), 5.0, "MIDDLE_CENTER", capa="ROTULO", estilo="NEGRITA")
    # escuela
    t(msp, INSTITUCION, (x0 + 2, 58.6), 2.9, "MIDDLE_LEFT", capa="ROTULO", estilo="NEGRITA")
    t(msp, CURSO, (x0 + 2, 54.2), 2.4, "MIDDLE_LEFT", capa="ROTULO")
    return 62.0


def _simbolo_iso_e(msp, x, y):
    """Símbolo del método de proyección ISO E: tronco de cono visto de frente y de costado."""
    a = {"layer": "ROTULO"}
    msp.add_lwpolyline([(x - 6, y - 2.2), (x, y - 1.2), (x, y + 1.2), (x - 6, y + 2.2)], close=True, dxfattribs=a)
    msp.add_circle((x + 4.5, y), 2.2, dxfattribs=a)
    msp.add_circle((x + 4.5, y), 1.2, dxfattribs=a)
    msp.add_line((x - 7.5, y), (x + 7.5, y), dxfattribs={"layer": "EJES"})


def _revisiones(msp, revisiones, y):
    x0, x1 = ROT_X0, MARCO[2]
    h = 3.6
    cols = [x0, x0 + 12, x0 + 29, x1 - 20, x1]
    filas = [("Rev.", "Fecha", "Descripción", "Dibujó")] + [tuple(r) + (DIBUJO.split()[0],) for r in revisiones]
    filas += [("", "", "", "")] * max(0, 3 - len(revisiones))
    for i, fila in enumerate(reversed(filas)):
        yy = y + i * h
        rect(msp, x0, yy, x1, yy + h, "ROTULO")
        for c in cols[1:-1]:
            msp.add_line((c, yy), (c, yy + h), dxfattribs={"layer": "ROTULO"})
        enc = i == len(filas) - 1
        for j, val in enumerate(fila):
            if not val:
                continue
            ca, cb = cols[j], cols[j + 1]
            hh = 2.0 if enc else min(2.2, (cb - ca - 2.5) / (0.7 * max(len(val), 1)))
            hh = max(hh, 1.2)
            alin = "MIDDLE_CENTER" if j in (0, 1) else "MIDDLE_LEFT"
            pos = ((ca + cb) / 2, yy + h / 2) if j in (0, 1) else (ca + 1.2, yy + h / 2)
            t(msp, val, pos, hh, alin, capa="ROTULO", estilo="NEGRITA" if enc else None)
    return y + len(filas) * h


# ---------------------------------------------------------------- dibujo

def t(msp, contenido, pos, altura=2.5, alineacion="MIDDLE_LEFT", capa="TEXTO", estilo=None,
      rotacion=0.0, color=None, fondo=False, ancho=None):
    """Texto (TEXT; MTEXT si tiene varios renglones, ancho fijo o fondo). estilo='NEGRITA' para negrita.
    color: (r, g, b) opcional."""
    contenido = str(contenido)
    attrs = {"layer": capa}
    if estilo:
        attrs["style"] = estilo
    if fondo or ancho or "\n" in contenido:
        attrs["char_height"] = altura
        mt = msp.add_mtext(contenido.replace("\n", "\\P"), dxfattribs=attrs)
        mt.set_location(pos, rotation=rotacion, attachment_point=lamina_a3._ADJUNTO_MTEXT[alineacion])
        if ancho:
            mt.dxf.width = ancho
        if fondo:
            mt.set_bg_color("canvas", scale=1.25)
        if color:
            mt.rgb = color
        return mt
    e = msp.add_text(contenido, height=altura, rotation=rotacion, dxfattribs=attrs)
    e.set_placement(pos, align=TextEntityAlignment[alineacion])
    if color:
        e.rgb = color
    return e


def tn(msp, contenido, pos, altura=2.5, alineacion="MIDDLE_LEFT", **kw):
    """Texto en negrita."""
    return t(msp, contenido, pos, altura, alineacion, estilo="NEGRITA", **kw)


def titulo_vista(msp, contenido, x, y, altura=3.5):
    """Título de vista o de bloque, en negrita y subrayado doble (como en las láminas del proyecto)."""
    tn(msp, contenido, (x, y), altura, "BOTTOM_LEFT")
    largo = 0.78 * altura * len(contenido)
    msp.add_line((x, y - 1.0), (x + largo, y - 1.0), dxfattribs={"layer": "CONTORNO"})
    msp.add_line((x, y - 1.8), (x + largo, y - 1.8), dxfattribs={"layer": "FINO"})
    return largo


def subtitulo(msp, contenido, x, y, altura=3.0):
    """Título de tabla o de nota, en negrita sin subrayar."""
    return tn(msp, contenido, (x, y), altura, "BOTTOM_LEFT")


def linea(msp, a, b, capa="CONTORNO", color=None, lw=None):
    e = msp.add_line(a, b, dxfattribs={"layer": capa})
    if color:
        e.rgb = color
    if lw:
        e.dxf.lineweight = lw
    return e


def poli(msp, pts, capa="CONTORNO", cerrada=False, color=None, lw=None, tipo=None):
    e = msp.add_lwpolyline(pts, close=cerrada, dxfattribs={"layer": capa})
    if color:
        e.rgb = color
    if lw:
        e.dxf.lineweight = lw
    if tipo:
        e.dxf.linetype = tipo
    return e


def rect(msp, x0, y0, x1, y1, capa="CONTORNO", color=None, lw=None, tipo=None):
    return poli(msp, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], capa, True, color, lw, tipo)


def circulo(msp, c, r, capa="CONTORNO", color=None, lw=None):
    e = msp.add_circle(c, r, dxfattribs={"layer": capa})
    if color:
        e.rgb = color
    if lw:
        e.dxf.lineweight = lw
    return e


def arco(msp, c, r, a0, a1, capa="CONTORNO", color=None):
    e = msp.add_arc(c, r, a0, a1, dxfattribs={"layer": capa})
    if color:
        e.rgb = color
    return e


def relleno(msp, pts, color, capa="RELLENO"):
    """Superficie llena (hatch sólido) con color RGB. Dibujarla ANTES que los contornos."""
    h = msp.add_hatch(dxfattribs={"layer": capa})
    h.rgb = color
    h.paths.add_polyline_path(pts, is_closed=True)
    return h


def relleno_rect(msp, x0, y0, x1, y1, color, capa="RELLENO"):
    return relleno(msp, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, capa)


def relleno_circulo(msp, c, r, color, capa="RELLENO"):
    h = msp.add_hatch(dxfattribs={"layer": capa})
    h.rgb = color
    h.paths.add_edge_path().add_arc(c, r, 0, 360)
    return h


def rayado(msp, pts, escala=1.0, angulo=45.0, capa="RAYADO", patron="ANSI31", color=None):
    """Rayado de corte (IRAM 4507): por defecto líneas finas a 45°."""
    h = msp.add_hatch(dxfattribs={"layer": capa})
    h.set_pattern_fill(patron, scale=escala, angle=angulo - 45.0 if patron == "ANSI31" else angulo)
    h.paths.add_polyline_path(pts, is_closed=True)
    if color:
        h.rgb = color
    return h


def flecha(msp, p0, p1, capa="CONTORNO", color=None, tam=2.2, lw=None):
    """Línea con punta de flecha llena en p1 (flujos, salidas, sentidos de marcha)."""
    linea(msp, p0, p1, capa, color, lw)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    a = (p1[0] - ux * tam - uy * tam * 0.38, p1[1] - uy * tam + ux * tam * 0.38)
    b = (p1[0] - ux * tam + uy * tam * 0.38, p1[1] - uy * tam - ux * tam * 0.38)
    h = msp.add_hatch(dxfattribs={"layer": capa})
    h.paths.add_polyline_path([p1, a, b], is_closed=True)
    if color:
        h.rgb = color
    return h


def flecha_poli(msp, pts, capa="CONTORNO", color=None, tam=2.2, lw=None):
    """Recorrido en varios tramos con flecha al final."""
    if len(pts) > 2:
        poli(msp, pts[:-1], capa, color=color, lw=lw)
    flecha(msp, pts[-2], pts[-1], capa, color, tam, lw)


def globo(msp, etiqueta, centro, apunta_a=None, radio=3.2, capa="COTAS", relleno_rgb=None):
    """Globo de referencia (línea desde el borde del círculo hasta un punto lleno)."""
    if relleno_rgb:
        relleno_circulo(msp, centro, radio, relleno_rgb)
    msp.add_circle(centro, radio, dxfattribs={"layer": capa})
    largo = len(str(etiqueta))
    h = radio * (0.95 if largo <= 2 else 0.8 if largo <= 3 else 0.62)
    tn(msp, etiqueta, centro, h, "MIDDLE_CENTER", capa=capa)
    if apunta_a:
        dx, dy = apunta_a[0] - centro[0], apunta_a[1] - centro[1]
        d = math.hypot(dx, dy)
        if d > radio:
            borde = (centro[0] + dx / d * radio, centro[1] + dy / d * radio)
            msp.add_line(borde, apunta_a, dxfattribs={"layer": capa})
            p = msp.add_hatch(dxfattribs={"layer": capa})
            p.paths.add_edge_path().add_arc(apunta_a, 0.55, 0, 360)


def tabla(msp, x, y, anchos, filas, h_fila=4.0, altura=2.2, encabezado=True, alin=None,
          negrita_ultima=False, sombras=None, ajustar=True):
    """Tabla con la primera fila de encabezado sombreada. (x, y) = esquina superior izquierda.

    anchos: ancho de cada columna (mm). alin: lista 'L', 'C' o 'R' por columna.
    sombras: {índice de fila: (r, g, b)} para resaltar filas (0 = encabezado).
    Devuelve la y del borde inferior.
    """
    alin = alin or ["L"] * len(anchos)
    xs = [x]
    for w in anchos:
        xs.append(xs[-1] + w)
    sombras = dict(sombras or {})
    if encabezado:
        sombras.setdefault(0, COL["encabezado"])
    for i, rgb in sombras.items():
        yy = y - (i + 1) * h_fila
        relleno_rect(msp, x, yy, xs[-1], yy + h_fila, rgb)
    for i, fila in enumerate(filas):
        yy = y - (i + 1) * h_fila
        rect(msp, x, yy, xs[-1], yy + h_fila, "FINO")
        neg = (encabezado and i == 0) or (negrita_ultima and i == len(filas) - 1)
        for j, val in enumerate(fila):
            if val is None or val == "":
                continue
            val = str(val)
            ca, cb = xs[j], xs[j + 1]
            hh = altura
            if ajustar:
                hh = max(1.4, min(altura, (cb - ca - 1.8) / (0.64 * max(len(val), 1))))
            a = alin[j]
            if a == "C":
                pos, al = ((ca + cb) / 2, yy + h_fila / 2), "MIDDLE_CENTER"
            elif a == "R":
                pos, al = (cb - 1.0, yy + h_fila / 2), "MIDDLE_RIGHT"
            else:
                pos, al = (ca + 1.0, yy + h_fila / 2), "MIDDLE_LEFT"
            t(msp, val, pos, hh, al, estilo="NEGRITA" if neg else None)
    for c in xs[1:-1]:
        msp.add_line((c, y), (c, y - len(filas) * h_fila), dxfattribs={"layer": "FINO"})
    rect(msp, x, y - len(filas) * h_fila, xs[-1], y, "CONTORNO")
    return y - len(filas) * h_fila


def notas(msp, renglones, x, y, altura=2.2, interlineado=1.55, titulo=None):
    """Bloque de notas numeradas o sueltas. Devuelve la y del último renglón."""
    if titulo:
        subtitulo(msp, titulo, x, y)
        y -= altura * 2.2
    for r in renglones:
        t(msp, r, (x, y), altura, "TOP_LEFT")
        y -= altura * interlineado
    return y


def escala_grafica(msp, x, y, escala, total_m, paso_m, alto=1.6):
    """Escala gráfica en metros: barras alternadas blanco/negro con rótulos."""
    k = factor(escala) * 1000.0
    n = int(round(total_m / paso_m))
    for i in range(n):
        x0, x1 = x + i * paso_m * k, x + (i + 1) * paso_m * k
        if i % 2 == 0:
            relleno_rect(msp, x0, y, x1, y + alto, (0, 0, 0))
        rect(msp, x0, y, x1, y + alto, "FINO")
    for i in range(n + 1):
        v = i * paso_m
        t(msp, f"{v:g}", (x + v * k, y + alto + 1.2), 2.0, "BOTTOM_CENTER")
    t(msp, "m", (x + total_m * k + 3, y + alto + 1.2), 2.0, "BOTTOM_LEFT")
    t(msp, f"Escala gráfica {escala}", (x, y - 1.5), 2.0, "TOP_LEFT")


def norte(msp, x, y, r=6.0):
    """Flecha de Norte dentro de un círculo, con la N arriba."""
    circulo(msp, (x, y), r, "CONTORNO")
    a, b, c = (x, y + r * 0.85), (x - r * 0.38, y - r * 0.6), (x + r * 0.38, y - r * 0.6)
    h = msp.add_hatch(dxfattribs={"layer": "CONTORNO"})
    h.paths.add_polyline_path([a, (x, y - r * 0.25), c], is_closed=True)
    poli(msp, [a, b, (x, y - r * 0.25), c], "CONTORNO", cerrada=True)
    tn(msp, "N", (x, y + r + 1.2), 4.0, "BOTTOM_CENTER")


def nivel(msp, x, y, texto, lado=1):
    """Indicador de nivel (triángulo invertido sobre una línea) con la cota, p. ej. '+4,35'."""
    s = 1.6
    poli(msp, [(x - s, y + s * 1.2), (x + s, y + s * 1.2), (x, y)], "COTAS", cerrada=True)
    linea(msp, (x - s * 2, y), (x + s * 6 * lado, y), "COTAS")
    t(msp, texto, (x + s * 1.3, y + s * 1.4), 2.2, "BOTTOM_LEFT")


def suelo(msp, x0, x1, y, alto=1.6):
    """Línea de terreno con rayado de suelo (cortes y vistas)."""
    linea(msp, (x0, y), (x1, y), "CONTORNO")
    rayado(msp, [(x0, y - alto), (x1, y - alto), (x1, y), (x0, y)], escala=0.35, patron="EARTH", angulo=0)


def imagen(doc, msp, ruta, x, y, ancho, alto=None, carpeta_planos=None):
    """Imagen raster (render del modelo 3D, logo). Se copia a planos/img para que el DXF la encuentre.
    (x, y) = esquina inferior izquierda; alto opcional (por defecto respeta la proporción)."""
    from PIL import Image
    carpeta = os.path.join(carpeta_planos or CARPETA_PLANOS, "dxf", "img")
    os.makedirs(carpeta, exist_ok=True)
    destino = os.path.join(carpeta, os.path.basename(ruta))
    if os.path.abspath(ruta) != os.path.abspath(destino):
        shutil.copyfile(ruta, destino)
    with Image.open(destino) as im:
        w, h = im.size
    alto = alto or ancho * h / w
    idef = doc.add_image_def(filename="img/" + os.path.basename(ruta), size_in_pixel=(w, h))
    msp.add_image(idef, insert=(x, y), size_in_units=(ancho, alto), dxfattribs={"layer": "AUXILIAR"})
    rect(msp, x, y, x + ancho, y + alto, "FINO")
    return (x, y, x + ancho, y + alto)


# ---------------------------------------------------------------- exportación

def exportar_lamina(doc, numero, dpi=200, carpeta_planos=None, prefijo="P"):
    """Guarda planos/dxf/Pxx.dxf, planos/pdf/Pxx.pdf (A3 vectorial) y planos/Pxx.png (visor).
    Para un juego aparte: carpeta_planos (p. ej. secadora/planos) y prefijo (p. ej. "SC-")."""
    CARPETA_PLANOS = carpeta_planos or globals()["CARPETA_PLANOS"]
    nombre = f"{prefijo}{numero:02d}"
    tmp = os.path.join(CARPETA_PLANOS, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    base = os.path.join(tmp, nombre)
    cwd = os.getcwd()
    os.makedirs(os.path.join(CARPETA_PLANOS, "dxf"), exist_ok=True)
    os.chdir(os.path.join(CARPETA_PLANOS, "dxf"))  # las imágenes del DXF se buscan en img/ desde acá
    try:
        lamina_a3.exportar(doc, base, color=True, dpi=dpi)
    finally:
        os.chdir(cwd)
    comprimir_imagenes_pdf(base + ".pdf")
    for ext, sub in ((".dxf", "dxf"), (".pdf", "pdf"), (".png", "")):
        dst_dir = os.path.join(CARPETA_PLANOS, sub) if sub else CARPETA_PLANOS
        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(base + ext, os.path.join(dst_dir, nombre + ext))
    return os.path.join(CARPETA_PLANOS, "pdf", nombre + ".pdf")


def comprimir_imagenes_pdf(ruta, max_px=1800, calidad=85, umbral=400_000):
    """El backend PDF de ezdxf guarda las imágenes sin comprimir (un render de 2000 px pesa ≈ 6 MB).
    Pasa a JPEG (y achica a max_px de ancho) las imágenes de más de 'umbral' bytes; no toca el dibujo
    vectorial ni las imágenes chicas (logos)."""
    import pymupdf
    doc = pymupdf.open(ruta)
    cambio = False
    hechos = set()                            # una imagen usada en varias páginas se reemplaza una sola vez
    for pagina in doc:
        for info in pagina.get_images(full=True):
            xref = info[0]
            if xref in hechos:
                continue
            hechos.add(xref)
            crudo = len(doc.xref_stream_raw(xref) or b"")
            if crudo < umbral:
                continue
            pix = pymupdf.Pixmap(doc, xref)
            if pix.alpha or pix.n > 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            if pix.width > max_px:
                from PIL import Image
                im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                im = im.resize((max_px, round(pix.height * max_px / pix.width)), Image.LANCZOS)
                import io
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=calidad, optimize=True)
                datos = buf.getvalue()
            else:
                datos = pix.tobytes("jpeg", jpg_quality=calidad)
            if len(datos) < 0.8 * crudo:          # solo si achica (las imágenes indexadas ya vienen chicas)
                pagina.replace_image(xref, stream=datos)
                cambio = True
    if cambio:
        tmp = ruta + ".tmp"
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        os.replace(tmp, ruta)
    else:
        doc.close()


def juego_completo():
    """Une los PDF de las 24 láminas en planos/pdf/Planos_Secadora_RevD.pdf, en orden."""
    pdfs = [os.path.join(CARPETA_PLANOS, "pdf", f"P{n:02d}.pdf") for n in range(1, TOTAL_HOJAS + 1)]
    faltan = [p for p in pdfs if not os.path.exists(p)]
    if faltan:
        raise FileNotFoundError("Faltan láminas: " + ", ".join(os.path.basename(p) for p in faltan))
    return unir_pdfs(pdfs, os.path.join(CARPETA_PLANOS, "pdf", "Planos_Secadora_RevD.pdf"))
