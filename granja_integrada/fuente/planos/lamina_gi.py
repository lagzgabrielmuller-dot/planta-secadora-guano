"""Base de las láminas GI de la granja integrada.

Usa las mismas funciones de lámina A3 del proyecto anterior (fuente/planos/lamina_secadora.py, solo lectura):
recuadro, rótulo de la escuela, tabla de revisiones, capas IRAM y exportación DXF + PDF vectorial + PNG. Acá solo
se cambia el nombre del proyecto, la serie (GI-xx) y la carpeta de salida (granja_integrada/planos).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]                                          # granja_integrada/
sys.path.insert(0, str(RAIZ.parent / "fuente" / "planos"))      # proyecto anterior (solo lectura)

import lamina_secadora as LS  # noqa: E402
from lamina_secadora import (COL, arco, circulo, escala_grafica, flecha, flecha_poli, globo, imagen,  # noqa: E402,F401
                             linea, nivel, norte, notas, poli, rayado, rect, relleno, relleno_circulo, relleno_rect,
                             subtitulo, suelo, t, tabla, titulo_vista, tn)
from lamina_a3 import cota, factor, unir_pdfs  # noqa: E402,F401

LS.PROYECTO = "GRANJA INTEGRADA · SECADO DE GUANO Y 4 GALPONES"
LS.FECHA = "11/2026"
CARPETA = RAIZ / "planos"
TOTAL = 20
REVISIONES = [("A", "11/2026", "Emisión original (granja integrada)")]

D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
K = json.loads((RAIZ / "datos" / "calculos.json").read_text(encoding="utf-8"))
E = json.loads((RAIZ / "datos" / "electrica.json").read_text(encoding="utf-8"))

# colores propios de la granja (RGB)
C = dict(COL)
C.update({"galpon": (196, 214, 230), "galpon_borde": (45, 74, 99), "deposito": (240, 226, 170), "planta": (214, 209, 200),
          "limpia": (222, 236, 214), "sucia": (238, 226, 210), "camino": (214, 214, 214), "transporte": (178, 58, 29),
          "inclinada": (217, 130, 43), "torre": (110, 110, 110), "tp": (160, 82, 45), "arbol": (120, 160, 100),
          "electrica": (200, 30, 120), "fibra": (40, 140, 200), "agua_c": (31, 150, 200), "ampl": (90, 110, 140)})


def hoja(n, titulo, escala):
    """Nueva lámina GI-n. Devuelve (doc, msp, zonas)."""
    return LS.lamina(n, titulo, escala, REVISIONES, serie={"prefijo": "GI-", "total": TOTAL})


def exportar(doc, n):
    return LS.exportar_lamina(doc, n, carpeta_planos=str(CARPETA), prefijo="GI-")


class Vista:
    """Transformación de coordenadas reales (m) a papel (mm): origen de papel (px, py) ↔ real (rx, ry), escala 1:den.
    eje: 'xy' (planta), 'xz' (vista desde el Sur), 'yz' (vista desde el Oeste), '-xz', '-yz' (sentido opuesto)."""

    def __init__(self, px, py, rx, ry, den, eje="xy"):
        self.px, self.py, self.rx, self.ry, self.k, self.eje = px, py, rx, ry, 1000.0 / den, eje

    def __call__(self, x, y=None):
        if y is None:
            x, y = x
        return (self.px + (x - self.rx) * self.k, self.py + (y - self.ry) * self.k)

    def p3(self, p):
        x, y, z = p
        a, b = {"xy": (x, y), "xz": (x, z), "yz": (y, z), "-xz": (-x, z), "-yz": (-y, z), "yx": (y, -x)}[self.eje]
        return self(a, b)

    def L(self, metros):
        return metros * self.k

    def rect(self, msp, x0, y0, x1, y1, capa="CONTORNO", **kw):
        a, b = self(x0, y0), self(x1, y1)
        return rect(msp, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), capa, **kw)

    def relleno_rect(self, msp, x0, y0, x1, y1, color):
        a, b = self(x0, y0), self(x1, y1)
        return relleno_rect(msp, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), color)

    def poli(self, msp, pts, capa="CONTORNO", **kw):
        return poli(msp, [self(p[0], p[1]) for p in pts], capa, **kw)

    def circulo(self, msp, c, r, capa="CONTORNO", **kw):
        return circulo(msp, self(*c), self.L(r), capa, **kw)


def fmt(v, dec=1):
    """Número con coma decimal y punto de miles (formato argentino)."""
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def cota_h(msp, a, b, y, texto, capa="COTAS", h=2.0):
    """Cota horizontal simple entre a y b (papel) a la altura y, con texto centrado."""
    linea(msp, (a, y), (b, y), capa)
    for x in (a, b):
        linea(msp, (x - 0.8, y - 0.8), (x + 0.8, y + 0.8), capa)
    t(msp, texto, ((a + b) / 2, y + 0.8), h, "BOTTOM_CENTER")


def cota_v(msp, x, a, b, texto, capa="COTAS", h=2.0):
    linea(msp, (x, a), (x, b), capa)
    for y in (a, b):
        linea(msp, (x - 0.8, y - 0.8), (x + 0.8, y + 0.8), capa)
    t(msp, texto, (x - 0.8, (a + b) / 2), h, "BOTTOM_CENTER", rotacion=90)


def caja_texto(msp, x0, y0, x1, y1, titulo, renglones, h=2.1, rgb=None):
    """Recuadro con título y renglones de texto (bloques de proceso, tableros, notas)."""
    if rgb:
        relleno_rect(msp, x0, y0, x1, y1, rgb)
    rect(msp, x0, y0, x1, y1, "CONTORNO")
    tn(msp, titulo, ((x0 + x1) / 2, y1 - 2.4), h + 0.3, "MIDDLE_CENTER")
    y = y1 - 5.2
    for r in renglones:
        t(msp, r, ((x0 + x1) / 2, y), h, "MIDDLE_CENTER")
        y -= h * 1.5
    return (x0, y0, x1, y1)


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])
