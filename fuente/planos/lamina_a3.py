"""Lámina normalizada para planos técnicos (A3 apaisada por defecto) con ezdxf.

Arma la hoja con recuadro, rótulo y tabla de revisiones, crea las capas
normalizadas y exporta DXF (AutoCAD), PDF vectorial al tamaño real de la hoja
y PNG de control.

    from lamina_a3 import nueva_lamina, cota, cota_diametro, texto, globo, factor, exportar, unir_pdfs
    doc, msp, zonas = nueva_lamina("Layout general", "P01", "1:100", proyecto="Planta de secado")
    k = factor("1:100")            # mm reales -> mm de papel
    ...                            # dibujar en msp con coordenadas en mm de papel
    exportar(doc, "salida/P01")    # P01.dxf, P01.pdf, P01.png

Demo:  python lamina_a3.py demo carpeta_salida
Requiere: pip install ezdxf pymupdf
"""
from __future__ import annotations

import datetime
import math
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

FORMATOS = {"A4": (210, 297), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594), "A0": (1189, 841)}

# capa: (color ACI, espesor en centésimas de mm, tipo de línea)
CAPAS = {
    "HOJA": (8, 13, "CONTINUOUS"),
    "RECUADRO": (7, 70, "CONTINUOUS"),
    "ROTULO": (7, 35, "CONTINUOUS"),
    "CONTORNO": (7, 50, "CONTINUOUS"),
    "OCULTAS": (8, 25, "DASHED"),
    "EJES": (1, 18, "CENTER"),
    "COTAS": (3, 25, "CONTINUOUS"),
    "RAYADO": (8, 18, "CONTINUOUS"),
    "TEXTO": (7, 25, "CONTINUOUS"),
    "AUXILIAR": (9, 13, "CONTINUOUS"),
}

_ADJUNTO_MTEXT = {
    "TOP_LEFT": 1, "TOP_CENTER": 2, "TOP_RIGHT": 3,
    "MIDDLE_LEFT": 4, "MIDDLE_CENTER": 5, "MIDDLE_RIGHT": 6,
    "BOTTOM_LEFT": 7, "BOTTOM_CENTER": 8, "BOTTOM_RIGHT": 9,
}


def factor(escala: str) -> float:
    """'1:50' -> 0.02 ; '2:1' -> 2.0. Multiplica medidas reales (mm) para pasarlas a mm de papel."""
    a, b = (float(x.replace(",", ".")) for x in escala.split(":"))
    return a / b


def nueva_lamina(titulo, numero, escala, proyecto="", autor="", reviso="", fecha=None,
                 revision=None, revisiones=None, formato="A3", margen_izq=25.0, margen=10.0,
                 institucion=""):
    """Crea el documento con hoja, recuadro, rótulo y (si se pasan) revisiones.

    revisiones: lista de tuplas (letra, fecha, descripción), de la más vieja a la más nueva.
    Devuelve (doc, msp, zonas); zonas tiene rectángulos (x0, y0, x1, y1) en mm de papel:
    'hoja', 'marco', 'dibujo' (interior del marco con 5 mm de aire), 'rotulo', 'revisiones'
    y 'reservado' (rótulo + revisiones, abajo a la derecha: no dibujar encima).
    """
    ancho, alto = FORMATOS[formato]
    fecha = fecha or datetime.date.today().strftime("%d/%m/%Y")
    revisiones = list(revisiones or [])
    if revision is None:
        revision = revisiones[-1][0] if revisiones else "A"

    doc = ezdxf.new("R2018", setup=True, units=4)  # 4 = milímetros
    doc.header["$MEASUREMENT"] = 1
    doc.styles.get("Standard").dxf.font = "arial.ttf"
    for nombre, (color, lw, lt) in CAPAS.items():
        doc.layers.add(nombre, color=color, lineweight=lw,
                       linetype=lt if lt in doc.linetypes else "CONTINUOUS")
    _estilo_cotas(doc)
    msp = doc.modelspace()

    # contorno de la hoja: fija la extensión exacta del PDF
    msp.add_lwpolyline([(0, 0), (ancho, 0), (ancho, alto), (0, alto)], close=True,
                       dxfattribs={"layer": "HOJA"})
    x0, y0, x1, y1 = margen_izq, margen, ancho - margen, alto - margen
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                       dxfattribs={"layer": "RECUADRO"})
    rot = _rotulo(msp, x1, y0, min(180.0, x1 - x0), titulo, numero, escala, proyecto,
                  autor, reviso, fecha, revision, institucion)
    rev = _tabla_revisiones(msp, rot, revisiones)
    tope = rev[3] if rev else rot[3]
    zonas = {
        "hoja": (0, 0, ancho, alto),
        "marco": (x0, y0, x1, y1),
        "dibujo": (x0 + 5, y0 + 5, x1 - 5, y1 - 5),
        "rotulo": rot,
        "revisiones": rev,
        "reservado": (rot[0], y0, x1, tope),
    }
    doc.set_modelspace_vport(height=alto * 1.05, center=(ancho / 2, alto / 2))
    return doc, msp, zonas


def texto(msp, contenido, pos, altura=3.5, alineacion="MIDDLE_CENTER", capa="TEXTO",
          rotacion=0.0, fondo=False, ancho=None):
    """Texto simple, o MTEXT si tiene varias líneas, ancho fijo o fondo blanco (fondo=True)."""
    contenido = str(contenido)
    if fondo or ancho or "\n" in contenido:
        mt = msp.add_mtext(contenido.replace("\n", "\\P"),
                           dxfattribs={"layer": capa, "char_height": altura})
        mt.set_location(pos, rotation=rotacion, attachment_point=_ADJUNTO_MTEXT[alineacion])
        if ancho:
            mt.dxf.width = ancho
        if fondo:
            mt.set_bg_color("canvas", scale=1.3)
        return mt
    t = msp.add_text(contenido, height=altura, rotation=rotacion, dxfattribs={"layer": capa})
    t.set_placement(pos, align=TextEntityAlignment[alineacion])
    return t


def cota(msp, p1, p2, distancia=8.0, escala=1.0, valor=None, capa="COTAS"):
    """Cota alineada entre p1 y p2 (mm de papel), con la línea a 'distancia' mm (signo = lado).

    escala: factor del dibujo (k = factor('1:N')) para que se lea la medida real.
    valor: texto fijo opcional (por ejemplo 'Ø 50 h7'); por defecto, la medida.
    """
    dim = msp.add_aligned_dim(p1=p1, p2=p2, distance=distancia, dimstyle="IRAM",
                              text=valor or "<>", override={"dimlfac": 1.0 / escala},
                              dxfattribs={"layer": capa})
    dim.render()
    return dim


def cota_diametro(msp, centro, radio, angulo=45.0, escala=1.0, capa="COTAS"):
    """Cota de diámetro de un círculo dibujado con radio 'radio' (mm de papel)."""
    dim = msp.add_diameter_dim(center=centro, radius=radio, angle=angulo, dimstyle="IRAM",
                               override={"dimlfac": 1.0 / escala}, dxfattribs={"layer": capa})
    dim.render()
    return dim


def globo(msp, etiqueta, centro, apunta_a=None, radio=4.0, capa="COTAS"):
    """Globo de referencia; la línea arranca en el borde del círculo y termina en un punto lleno."""
    msp.add_circle(centro, radio, dxfattribs={"layer": capa})
    texto(msp, etiqueta, centro, altura=radio * 0.9, capa=capa)
    if apunta_a:
        dx, dy = apunta_a[0] - centro[0], apunta_a[1] - centro[1]
        d = math.hypot(dx, dy)
        if d > radio:
            borde = (centro[0] + dx / d * radio, centro[1] + dy / d * radio)
            msp.add_line(borde, apunta_a, dxfattribs={"layer": capa})
            punto = msp.add_hatch(dxfattribs={"layer": capa})
            punto.paths.add_edge_path().add_arc(apunta_a, 0.7, 0, 360)


def exportar(doc, base, color=False, dpi=150, png=True):
    """Guarda base.dxf, base.pdf (vectorial, tamaño real de la hoja) y base.png.

    color=False imprime todo en negro (plano normalizado); True respeta los colores de capa.
    """
    from ezdxf import bbox

    carpeta = os.path.dirname(os.path.abspath(base))
    os.makedirs(carpeta, exist_ok=True)
    auditor = doc.audit()
    doc.saveas(base + ".dxf")
    caja = bbox.extents(doc.modelspace().query('*[layer=="HOJA"]'))
    ancho, alto = caja.size.x, caja.size.y
    with open(base + ".pdf", "wb") as f:
        f.write(_pdf_vectorial(doc, ancho, alto, color))
    if png:
        import pymupdf
        with pymupdf.open(base + ".pdf") as d:
            d[0].get_pixmap(dpi=dpi).save(base + ".png")
    print(f"{os.path.basename(base)}: DXF + PDF {ancho:.0f} x {alto:.0f} mm"
          f"{' + PNG' if png else ''} | errores DXF: {len(auditor.errors)}")
    return base


def unir_pdfs(pdfs, salida):
    """Une las láminas en un solo PDF, en el orden dado."""
    import pymupdf
    juego = pymupdf.open()
    for p in pdfs:
        with pymupdf.open(p) as d:
            juego.insert_pdf(d)
    juego.save(salida)
    print(f"{os.path.basename(salida)}: {juego.page_count} láminas")
    juego.close()
    return salida


# ---------------------------------------------------------------- internos

def _estilo_cotas(doc):
    if "IRAM" in doc.dimstyles:
        return
    doc.dimstyles.new("IRAM", dxfattribs={
        "dimtxt": 2.5, "dimasz": 2.5, "dimexo": 1.0, "dimexe": 1.5, "dimgap": 0.8,
        "dimtad": 1, "dimtih": 0, "dimtoh": 0, "dimdec": 1, "dimzin": 8, "dimdsep": ord(","),
    })


def _altura(contenido, ancho_disp, h_max, h_min=1.8):
    """Altura de texto que entra en ancho_disp (estimación para letra tipo Arial)."""
    n = max(len(str(contenido)), 1)
    return max(h_min, min(h_max, ancho_disp / (0.62 * n)))


def _t(msp, contenido, pos, h, alin, capa="ROTULO"):
    texto(msp, contenido, pos, altura=h, alineacion=alin, capa=capa)


def _rotulo(msp, x1, y0, ancho, titulo, numero, escala, proyecto, autor, reviso, fecha,
            revision, institucion):
    alto = 40.0
    x0 = x1 - ancho
    linea = lambda a, b: msp.add_line(a, b, dxfattribs={"layer": "ROTULO"})
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y0 + alto), (x0, y0 + alto)], close=True,
                       dxfattribs={"layer": "ROTULO"})
    linea((x0, y0 + 15), (x1, y0 + 15))
    linea((x0, y0 + 30), (x1, y0 + 30))
    xn = x1 - 50  # columna del número de plano
    linea((xn, y0 + 15), (xn, y0 + 30))

    campos = [("ESCALA", escala, 2), ("FECHA", fecha, 2), ("DIBUJÓ", autor, 3),
              ("REVISÓ", reviso, 3), ("REV.", revision, 2)]
    x = x0
    for etiqueta, valor, partes in campos:
        w = ancho * partes / 12
        if x > x0:
            linea((x, y0), (x, y0 + 15))
        _t(msp, etiqueta, (x + 1.5, y0 + 13.5), 1.8, "TOP_LEFT")
        if valor:
            _t(msp, valor, (x + w / 2, y0 + 6), _altura(valor, w - 3, 3.0), "MIDDLE_CENTER")
        x += w

    _t(msp, "PLANO N°", (xn + 1.5, y0 + 28.5), 1.8, "TOP_LEFT")
    _t(msp, numero, ((xn + x1) / 2, y0 + 21), _altura(numero, 44, 6.0), "MIDDLE_CENTER")
    _t(msp, titulo, ((x0 + xn) / 2, y0 + 22.5), _altura(titulo, xn - x0 - 4, 5.0), "MIDDLE_CENTER")
    cabecera = f"{institucion} · {proyecto}" if institucion and proyecto else (institucion or proyecto)
    _t(msp, "PROYECTO", (x0 + 1.5, y0 + 38.5), 1.8, "TOP_LEFT")
    if cabecera:
        _t(msp, cabecera, (x0 + 18, y0 + 35), _altura(cabecera, ancho - 20, 3.0), "MIDDLE_LEFT")
    return (x0, y0, x1, y0 + alto)


def _tabla_revisiones(msp, rot, revisiones):
    if not revisiones:
        return None
    x0, _, x1, y = rot
    h = 6.0
    filas = [("REV.", "FECHA", "DESCRIPCIÓN")] + [tuple(str(c) for c in f) for f in revisiones]
    columnas = [x0, x0 + 15, x0 + 40, x1]
    y_ini = y
    for i, fila in enumerate(filas):
        msp.add_lwpolyline([(x0, y), (x1, y), (x1, y + h), (x0, y + h)], close=True,
                           dxfattribs={"layer": "ROTULO"})
        for c in columnas[1:-1]:
            msp.add_line((c, y), (c, y + h), dxfattribs={"layer": "ROTULO"})
        hmax = 1.8 if i == 0 else 2.5
        for j, valor in enumerate(fila[:3]):
            ca, cb = columnas[j], columnas[j + 1]
            if j < 2:
                _t(msp, valor, ((ca + cb) / 2, y + h / 2), _altura(valor, cb - ca - 2, hmax), "MIDDLE_CENTER")
            else:
                _t(msp, valor, (ca + 1.5, y + h / 2), _altura(valor, cb - ca - 3, hmax), "MIDDLE_LEFT")
        y += h
    return (x0, y_ini, x1, y)


def _pdf_vectorial(doc, ancho, alto, color):
    from ezdxf.addons.drawing import Frontend, RenderContext, config, layout
    from ezdxf.addons.drawing import pymupdf as backend_pymupdf

    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.COLOR if color else config.ColorPolicy.BLACK,
        lineweight_policy=config.LineweightPolicy.ABSOLUTE,
        lineweight_scaling=1.0,
    )
    backend = backend_pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(doc.modelspace(), finalize=True)
    pagina = layout.Page(ancho, alto, layout.Units.mm, margins=layout.Margins.all(0))
    return backend.get_pdf_bytes(pagina, settings=layout.Settings(fit_page=False, scale=1.0))


# ---------------------------------------------------------------- demo

def _demo(carpeta):
    """Placa con agujeros a escala 1:2: vistas, ocultas, ejes, cotas, globo y revisiones."""
    doc, msp, z = nueva_lamina("Placa de anclaje del motor", "P01", "1:2",
                               proyecto="Ejemplo de lámina normalizada", autor="Apellido N.",
                               reviso="Docente", revisiones=[("A", "21/10/2026", "Emisión original"),
                                                             ("B", "22/10/2026", "Se agregan agujeros Ø18")])
    k = factor("1:2")
    L, A, E, D = 300, 200, 16, 18            # mm reales
    ox, oy = 70, 150                          # frente (alzado), mm de papel
    w, h, e = L * k, A * k, E * k
    msp.add_lwpolyline([(ox, oy), (ox + w, oy), (ox + w, oy + e), (ox, oy + e)], close=True,
                       dxfattribs={"layer": "CONTORNO"})
    py = oy - 25 - h                          # planta debajo del frente (método ISO E)
    msp.add_lwpolyline([(ox, py), (ox + w, py), (ox + w, py + h), (ox, py + h)], close=True,
                       dxfattribs={"layer": "CONTORNO"})
    for cx in (40, L - 40):
        for cy in (40, A - 40):
            msp.add_circle((ox + cx * k, py + cy * k), D / 2 * k, dxfattribs={"layer": "CONTORNO"})
            msp.add_line((ox + cx * k - 8, py + cy * k), (ox + cx * k + 8, py + cy * k), dxfattribs={"layer": "EJES"})
            msp.add_line((ox + cx * k, py + cy * k - 8), (ox + cx * k, py + cy * k + 8), dxfattribs={"layer": "EJES"})
        for xx in (cx - D / 2, cx + D / 2):   # agujeros ocultos en el frente
            msp.add_line((ox + xx * k, oy), (ox + xx * k, oy + e), dxfattribs={"layer": "OCULTAS"})
    cota(msp, (ox, oy + e), (ox + w, oy + e), distancia=10, escala=k)
    cota(msp, (ox + w, oy), (ox + w, oy + e), distancia=-10, escala=k)
    cota(msp, (ox, py), (ox + w, py), distancia=-10, escala=k)
    cota(msp, (ox, py), (ox, py + h), distancia=10, escala=k)
    cota_diametro(msp, (ox + (L - 40) * k, py + (A - 40) * k), D / 2 * k, angulo=45, escala=k)
    globo(msp, 1, (ox + w + 40, py + h + 15), apunta_a=(ox + w - 2, py + h - 2))
    texto(msp, "Material: chapa F-24 de 16 mm\nAgujeros pasantes Ø18 para bulones M16",
          (z["dibujo"][0] + 2, z["dibujo"][3] - 2), altura=3, alineacion="TOP_LEFT", ancho=120)
    base = os.path.join(carpeta, "P01_demo")
    exportar(doc, base)
    return base


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        _demo(sys.argv[2] if len(sys.argv) > 2 else "salida")
    else:
        print(__doc__)
