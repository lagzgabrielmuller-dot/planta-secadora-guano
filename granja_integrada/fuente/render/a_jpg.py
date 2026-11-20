"""Pasa los renders de Blender (PNG en renders/_png) a JPG livianos en renders/.

    python a_jpg.py            # todos
    python a_jpg.py R06        # solo los que empiezan con R06
"""
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]          # granja_integrada/
ORIGEN, DESTINO = RAIZ / "renders" / "_png", RAIZ / "renders"


def main(prefijos):
    for png in sorted(ORIGEN.glob("*.png")):
        if prefijos and not any(png.stem.startswith(p) for p in prefijos):
            continue
        jpg = DESTINO / (png.stem + ".jpg")
        Image.open(png).convert("RGB").save(jpg, quality=90, optimize=True, progressive=True)
        print(png.name, "->", jpg.name, f"{jpg.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main(sys.argv[1:])
