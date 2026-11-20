"""Cortes y plantas sacados del modelo 3D: se corta cada pieza con un plano y se dibujan las líneas en la lámina.

Así los cortes de los planos son los del modelo (mismas medidas y ubicaciones), sin redibujar a mano.

    from cortes import corte, dibujar
    segs = corte("y", 52.65, region=(-72, -60, None, None, -1, 7))         # plano y = 52,65 m
    dibujar(msp, segs, vista)                                              # vista: Vista con eje 'xz'
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import trimesh

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[0] / "modelo"))

_ESCENA = None
_MALLA = {}
_CAJA = {}

# color por grupo en los cortes (RGB); el resto va en gris oscuro
COLOR_GRUPO = [("Instalación eléctrica", (200, 30, 120)), ("Transporte de guano", (178, 58, 29)),
               ("Torres", (70, 70, 70)), ("Recepción", (160, 82, 45)), ("Secador", (40, 90, 170)),
               ("Galpones - jaulas", (110, 130, 150)), ("Galpones - accionamientos", (178, 58, 29)),
               ("Flujo", None), ("Predio - terreno", None), ("Predio - forestación", None)]


def escena():
    global _ESCENA
    if _ESCENA is None:
        import cad
        import electrica
        import galpon
        import planta
        import sitio
        import transporte
        e = cad.Escena("granja")
        sitio.construir(e)
        galpon.construir(e)
        planta.construir(e)
        transporte.construir(e)
        electrica.construir(e)
        _ESCENA = e
    return _ESCENA


def _malla(key):
    if key not in _MALLA:
        import cad
        sh = cad.forma(key)
        bb = sh.BoundingBox()
        diag = math.sqrt(bb.xlen ** 2 + bb.ylen ** 2 + bb.zlen ** 2)
        vs, fs = sh.tessellate(min(4.0, max(0.2, diag / 300)), 0.3)
        if not fs:
            _MALLA[key] = None
        else:
            _MALLA[key] = trimesh.Trimesh(vertices=np.array([(p.x, p.y, p.z) for p in vs]), faces=np.array(fs), process=False)
        _CAJA[key] = np.array([[bb.xmin, bb.ymin, bb.zmin], [bb.xmax, bb.ymax, bb.zmax]])
    return _MALLA[key]


def _esquinas(key, M):
    lo, hi = _CAJA[key]
    P = np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    return (M @ P.T).T[:, :3] / 1000.0


def corte(eje, valor, region=(None, None, None, None, None, None), filtro=None, mallas=True):
    """Segmentos (m) de la intersección del modelo con el plano eje = valor.

    eje: 'x', 'y' o 'z'. region: (x0, x1, y0, y1, z0, z1) en m (None = sin límite).
    Devuelve una lista de (array k×2×3, grupo, material)."""
    e = escena()
    i_eje = "xyz".index(eje)
    n = np.zeros(3)
    n[i_eje] = 1.0
    lim = [(region[2 * k], region[2 * k + 1]) for k in range(3)]
    out = []
    for inst in e.inst:
        g = inst["grupo"]
        if filtro and not filtro(inst):
            continue
        if any(g.startswith(p) for p, c in COLOR_GRUPO if c is None):
            continue
        m = _malla(inst["key"])
        if m is None:
            continue
        M = inst["M"]
        W = _esquinas(inst["key"], M)
        lo, hi = W.min(0), W.max(0)
        if not (lo[i_eje] <= valor <= hi[i_eje]):
            continue
        if any((a is not None and hi[k] < a) or (b is not None and lo[k] > b) for k, (a, b) in enumerate(lim)):
            continue
        R, tr = M[:3, :3], M[:3, 3]
        n_l = R.T @ n
        o_l = R.T @ (n * valor * 1000.0 - tr)
        try:
            lineas = trimesh.intersections.mesh_plane(m, n_l, o_l)
        except Exception:
            continue
        if len(lineas):
            w = (np.einsum("ij,klj->kli", R, lineas) + tr) / 1000.0
            out.append((w, g, inst["mat"]))
    if mallas:
        for g, m in e.mallas:
            if any(g.startswith(p) for p, c in COLOR_GRUPO if c is None):
                continue
            lo, hi = m.bounds
            if not (lo[i_eje] <= valor <= hi[i_eje]):
                continue
            try:
                lineas = trimesh.intersections.mesh_plane(m, n, n * valor)
            except Exception:
                continue
            if len(lineas):
                sel = np.ones(len(lineas), bool)
                for k, (a, b) in enumerate(lim):
                    if a is not None:
                        sel &= lineas[:, :, k].max(1) >= a
                    if b is not None:
                        sel &= lineas[:, :, k].min(1) <= b
                if sel.any():
                    out.append((lineas[sel], g, "revF"))
    return out


def color_de(grupo):
    for p, c in COLOR_GRUPO:
        if grupo.startswith(p):
            return c
    return (35, 35, 35)


def dibujar(msp, segs, vista, capa="CONTORNO", color=None, lw=None, recorte=None, min_mm=0.15):
    """Dibuja los segmentos con la Vista (su eje dice cómo proyectar). recorte: (u0, u1, v0, v1) en mm de papel."""
    n = 0
    for w, g, mat in segs:
        rgb = color or color_de(g)
        for a, b in w:
            pa, pb = vista.p3(a), vista.p3(b)
            if math.dist(pa, pb) < min_mm:
                continue
            if recorte:
                c = _recortar(pa, pb, recorte)
                if c is None:
                    continue
                pa, pb = c
            e = msp.add_line(pa, pb, dxfattribs={"layer": capa})
            if rgb:
                e.rgb = rgb
            if lw:
                e.dxf.lineweight = lw
            n += 1
    return n


def _dentro(pa, pb, r):
    u0, u1, v0, v1 = r
    return all(u0 <= p[0] <= u1 and v0 <= p[1] <= v1 for p in (pa, pb))


def _recortar(pa, pb, r):
    """Recorte de Liang-Barsky del segmento pa-pb al rectángulo r = (u0, u1, v0, v1)."""
    u0, u1, v0, v1 = r
    x0, y0 = pa
    dx, dy = pb[0] - x0, pb[1] - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - u0), (dx, u1 - x0), (-dy, y0 - v0), (dy, v1 - y0)):
        if p == 0:
            if q < 0:
                return None
            continue
        tt = q / p
        if p < 0:
            if tt > t1:
                return None
            t0 = max(t0, tt)
        else:
            if tt < t0:
                return None
            t1 = min(t1, tt)
    return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)
