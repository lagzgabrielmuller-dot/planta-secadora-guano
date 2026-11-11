"""Genera las 24 láminas y el juego completo en un solo PDF.

    python juego.py            # todas
    python juego.py 5 17 23    # solo esas (y vuelve a armar el juego completo)
"""
import importlib
import os
import sys

import pymupdf

from lamina_secadora import CARPETA_PLANOS, TOTAL_HOJAS, juego_completo

AQUI = os.path.dirname(os.path.abspath(__file__))


def main(numeros):
    for n in numeros:
        modulo = importlib.import_module(f"P{n:02d}")
        modulo.main()
    pdf = juego_completo()
    with pymupdf.open(pdf) as d:
        tamanos = {(round(p.rect.width), round(p.rect.height)) for p in d}
        print(f"juego completo: {d.page_count} láminas, tamaño de página {tamanos} pt (A3 = 1191 x 842)")
    print("carpeta:", CARPETA_PLANOS)


if __name__ == "__main__":
    os.chdir(AQUI)
    sys.path.insert(0, AQUI)
    nums = [int(x) for x in sys.argv[1:]] or list(range(1, TOTAL_HOJAS + 1))
    main(nums)
