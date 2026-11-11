"""Proyecciones ortogonales del modelo del secador SC-4 (aristas visibles y ocultas, algoritmo HLR de
OpenCASCADE) para dibujar los planos SC en DXF. Misma técnica que vistas_dxf() de la skill
modelado-3d-cad del kit, pero devuelve polilíneas 2D en mm del modelo y las guarda en caché
(fuente/secadora/_cache) porque proyectar el conjunto completo tarda.

    from proyecciones import proyectar
    v = proyectar("exterior", ["frente", "planta", "lateral_o"])
    v["frente"]["visibles"]   # [[(x, y), ...], ...]   x = a lo largo del secador, y = altura
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
CACHE = os.path.join(AQUI, "_cache")

# (dirección hacia el observador, eje x de la vista). Método ISO E: frente = cara Sur (accionamientos),
# planta debajo del frente, lateral izquierda (vista desde el Oeste) a la derecha del frente.
VISTAS = {
    "frente": ((0, -1, 0), (1, 0, 0)),
    "planta": ((0, 0, 1), (1, 0, 0)),
    "lateral_o": ((-1, 0, 0), (0, -1, 0)),
    "lateral_e": ((1, 0, 0), (0, 1, 0)),
    "posterior": ((0, 1, 0), (-1, 0, 0)),
}

# conjuntos de piezas (expresiones regulares sobre el código de la pieza)
SELECCION = {
    # lo que se ve desde afuera (sin bandas, tambores ni piezas internas: el HLR es mucho más rápido)
    "exterior": r"^(4\.8|4\.9|4\.11a|4\.17|4\.13|4\.12|4\.19|4\.5|M\d|4\.15c|4\.16|4\.4|4\.14|4\.2\.1|4\.3\.1)",
    "estructura": r"^(4\.11|4\.17|4\.20|4\.16-)",
    "interior": r"^(4\.1-|4\.2|4\.3|4\.4|4\.6|4\.7|4\.10|4\.11|4\.14|4\.18|4\.19|4\.20|4\.16-|4\.17)",
}


def _huella():
    with open(os.path.join(AQUI, "modelo_secador.py"), "rb") as f:
        return hashlib.sha1(f.read() + open(__file__, "rb").read()).hexdigest()[:12]


def _aristas_a_polilineas(compuestos, paso_mm=15.0):
    import cadquery as cq
    from OCP.BRepLib import BRepLib
    polis = []
    for c in compuestos:
        if c is None or c.IsNull():
            continue
        for e in cq.Shape.cast(c).Edges():
            BRepLib.BuildCurves3d_s(e.wrapped, 1e-6)
            tipo = e.geomType()
            if tipo == "LINE":
                a, b = e.startPoint(), e.endPoint()
                polis.append([(round(a.x, 1), round(a.y, 1)), (round(b.x, 1), round(b.y, 1))])
                continue
            largo = e.Length()
            if largo < 0.5:
                continue
            if tipo == "CIRCLE":
                n = max(6, int(math.degrees(largo / max(e.radius(), 1e-6)) / 8))
            else:
                n = max(4, int(largo / paso_mm))
            pts = [e.positionAt(i / n) for i in range(n + 1)]
            polis.append([(round(p.x, 1), round(p.y, 1)) for p in pts])
    return polis


def _hlr(forma, hacia, eje_x):
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    algo = HLRBRep_Algo()
    algo.Add(forma.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*hacia), gp_Dir(*eje_x))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    vis = _aristas_a_polilineas([h.VCompound(), h.OutLineVCompound()])
    ocu = _aristas_a_polilineas([h.HCompound(), h.OutLineHCompound()])
    return vis, ocu


def _caja(polis):
    xs = [p[0] for pl in polis for p in pl]
    ys = [p[1] for pl in polis for p in pl]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)


def proyectar(seleccion, vistas, ocultas=False):
    """Devuelve {vista: {"visibles": [...], "ocultas": [...], "caja": (x0, y0, x1, y1)}} en mm del modelo."""
    os.makedirs(CACHE, exist_ok=True)
    clave = f"{seleccion}_{'-'.join(vistas)}_{int(ocultas)}_{_huella()}"
    ruta = os.path.join(CACHE, clave + ".json")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    import cadquery as cq
    import modelo_secador as M
    patron = re.compile(SELECCION.get(seleccion, seleccion))
    formas = [p["forma"] for p in M.construir() if patron.search(p["cod"])]
    comp = cq.Compound.makeCompound(formas)
    res = {}
    for v in vistas:
        vis, ocu = _hlr(comp, *VISTAS[v])
        res[v] = {"visibles": vis, "ocultas": ocu if ocultas else [], "caja": _caja(vis + (ocu if ocultas else []))}
        print(f"  proyección {seleccion}/{v}: {len(vis)} visibles, {len(ocu)} ocultas")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(res, f)
    return res


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = proyectar(sys.argv[1] if len(sys.argv) > 1 else "exterior", ["frente", "planta", "lateral_o"])
    print({k: v["caja"] for k, v in r.items()}, f"{time.time() - t0:.0f} s")
