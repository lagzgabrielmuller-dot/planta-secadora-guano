"""Geometría de la planta para el video: geo.json (capturado del visor con capturar_geometria.js) ->
datos/planta.bin (Float32, triángulos en coordenadas del mundo) + datos/planta.json (índice).

Cada pieza del visor se separa por color, y la nave (N) y el anexo (AN) se dividen además en piso,
estructura, paredes y techo para poder armarlos por etapas en el video.

    node ../capturar_geometria.js ../../visor.html _tmp/geo.json
    python preparar_planta.py _tmp/geo.json

Ejes de three.js (los del visor): x al Este, y arriba, z al Sur; metros; origen en el vértice SO de la nave.
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "datos")

# piezas que no van en el video: el secador simplificado del visor (se usa el modelo detallado SC-4)
FUERA = {"4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8", "4.9", "4.10", "4.11", "4.12", "4.13"}
VEHICULOS = {"CA", "CB", "CC", "L", "MC"}


def triangulos(it):
    m = np.array(it["m"], dtype=np.float64).reshape(4, 4).T       # three guarda la matriz por columnas
    p = np.array(it["tri"], dtype=np.float64).reshape(-1, 3)
    p = p @ m[:3, :3].T + m[:3, 3]
    return p.astype(np.float32)


def clase_cerramiento(p):
    """Piso, estructura, pared o techo según la caja de la pieza (nave y anexo)."""
    lo, hi = p.min(0), p.max(0)
    dx, dy, dz = hi - lo
    if hi[1] <= 0.45:
        return "piso"
    if lo[1] >= 4.2 or (dy < 1.6 and lo[1] > 3.0):
        return "techo"
    if dy >= 1.5 and min(dx, dz) <= 0.45 and max(dx, dz) >= 1.2:
        return "paredes"
    if dy >= 1.5:
        return "estructura"
    return "estructura" if lo[1] > 0.45 else "piso"


def clase_terreno(it, p):
    lo, hi = p.min(0), p.max(0)
    dx, dy, dz = hi - lo
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    if max(dx, dz) > 160 or not (-27 <= cx <= 103 and -45 <= cz <= 41):
        return None                                   # campo y calles del visor: los reemplaza la imagen satelital
    if it["t"] in ("IcosahedronGeometry",) or (it["t"] == "CylinderGeometry" and dy > 1.5 and max(dx, dz) < 1):
        return "arboles"
    if hi[1] <= 0.5:
        return "solado"
    return "cerco"


def main(geo):
    g = json.load(open(geo, encoding="utf-8"))
    nombres = g.get("nombres", {})
    bloques = defaultdict(list)                      # (pieza, grupo, color, opacidad) -> [triángulos]
    for pid, items in g["partes"].items():
        if pid in FUERA:
            continue
        for it in items:
            if not it.get("tri"):
                continue
            p = triangulos(it)
            if pid in ("N", "AN"):
                grupo = clase_cerramiento(p)
            elif pid == "terreno":
                grupo = clase_terreno(it, p)
                if grupo is None:
                    continue
            elif pid in VEHICULOS:
                if it["t"] == "TubeGeometry":
                    continue                          # manguera de soplado del camión de cáscara (animación del visor)
                grupo = "vehiculo"
            else:
                grupo = "equipo"
            c = it["c"]
            if it.get("tex") is not None:          # textura del visor: su color promedio por el color del material
                c = (((c >> 16) & 255) * ((it["tex"] >> 16) & 255) // 255 << 16) | \
                    (((c >> 8) & 255) * ((it["tex"] >> 8) & 255) // 255 << 8) | ((c & 255) * (it["tex"] & 255) // 255)
            if it.get("vc"):                         # colores por vértice (vehículos, tablero): bloque propio
                col = np.array(it["vc"], dtype=np.float32).reshape(-1, 3) * np.array(
                    [((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255], dtype=np.float32)
                bloques[(pid, grupo, -1, round(it.get("op", 1), 2))].append((p, col))
            else:
                bloques[(pid, grupo, c, round(it.get("op", 1), 2))].append(p)
    os.makedirs(DATOS, exist_ok=True)
    indice, partes, colores, ofs, ofs_c = [], [], [], 0, 0
    for (pid, grupo, c, op), lista in sorted(bloques.items(), key=lambda kv: kv[0][:2]):
        vc = c == -1
        p = np.concatenate([x[0] for x in lista] if vc else lista)
        lo, hi = p.min(0), p.max(0)
        b = {"pieza": pid, "grupo": grupo, "c": 0xffffff if vc else c, "op": op, "ofs": ofs, "n": int(p.size),
             "min": [round(float(v), 3) for v in lo], "max": [round(float(v), 3) for v in hi]}
        if vc:
            col = np.clip(np.concatenate([x[1] for x in lista]) * 255 + 0.5, 0, 255).astype(np.uint8)
            b["vc_ofs"] = ofs_c
            colores.append(col.ravel())
            ofs_c += col.size
        indice.append(b)
        partes.append(p.ravel())
        ofs += p.size
    datos = np.concatenate(partes).astype(np.float32)
    datos.tofile(os.path.join(DATOS, "planta.bin"))
    (np.concatenate(colores) if colores else np.zeros(0, np.uint8)).tofile(os.path.join(DATOS, "planta_col.bin"))
    json.dump({"bloques": indice, "nombres": nombres}, open(os.path.join(DATOS, "planta.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    tot = defaultdict(int)
    for b in indice:
        tot[b["grupo"]] += b["n"] // 9
    print(f"planta.bin {datos.nbytes / 1e6:.1f} MB · {len(indice)} bloques · triángulos por grupo {dict(tot)}")


if __name__ == "__main__":
    main(sys.argv[1])
