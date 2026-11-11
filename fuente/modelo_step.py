"""Modelo STEP de la secadora (Rev. D) a partir de la geometría del visor 3D.

La geometría se captura del propio visor (visor.html) con fuente/capturar_geometria.js, que
guarda por cada pieza sus primitivas (caja, cilindro, cono, esfera, toro, plano) con su
matriz de ubicación, y las mallas que no son primitivas. Acá se rearma cada primitiva como
sólido exacto de OpenCASCADE y las mallas como sólidos facetados cosidos, y se exporta un
ensamble STEP con una sub-pieza por ítem de la lista de partes (nombre y color).

    python modelo_step.py geo.json ../modelo_3d/Secadora_guano_RevD

Unidades: mm. Ejes: X al Este, Y al Norte, Z arriba; origen en el vértice Sudoeste de la nave
(igual que los planos 01, 08, 11 y 13).
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict

import cadquery as cq
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import (BRepBuilderAPI_GTransform, BRepBuilderAPI_MakePolygon,
                                BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid,
                                BRepBuilderAPI_Sewing, BRepBuilderAPI_Transform)
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone,
                             BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere,
                             BRepPrimAPI_MakeTorus)
from OCP.gp import gp_Ax2, gp_Dir, gp_GTrsf, gp_Mat, gp_Pnt, gp_Trsf, gp_XYZ
from OCP.Interface import Interface_Static
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Compound

# piezas que no son parte de la instalación (vehículos, personas, terreno)
EXCLUIR = {"terreno", "AU1", "AU2", "AU3", "CA", "CB", "CC", "L", "MC"}
EXCLUIR_PREFIJOS = ("OP",)

MM = 1000.0                      # el visor trabaja en metros
TOL = 1e-4                       # tolerancia relativa para reconocer primitivas
ESPESOR_PLANO = 0.002            # carteles y placas: chapa de 2 mm
SEG_MIN_CIL = 8                  # con menos lados el cilindro es un prisma a propósito


def matriz(m):
    """Matriz 4x4 de three.js (por columnas, Y arriba, m) -> filas, Z arriba, mm."""
    M = [[m[0], m[4], m[8], m[12]], [m[1], m[5], m[9], m[13]], [m[2], m[6], m[10], m[14]]]
    # (x, y, z)_three -> (x, -z, y) en mm
    C = [[MM, 0, 0], [0, 0, -MM], [0, MM, 0]]
    return [[sum(C[i][k] * M[k][j] for k in range(3)) for j in range(4)] for i in range(3)]


def aplicar(forma, A):
    """Ubica una forma construida en coordenadas locales (m) con la matriz A (3x4, mm)."""
    L = [[A[i][j] for j in range(3)] for i in range(3)]
    cols = [math.sqrt(sum(L[i][j] ** 2 for i in range(3))) for j in range(3)]
    det = (L[0][0] * (L[1][1] * L[2][2] - L[1][2] * L[2][1]) - L[0][1] * (L[1][0] * L[2][2] - L[1][2] * L[2][0])
           + L[0][2] * (L[1][0] * L[2][1] - L[1][1] * L[2][0]))
    s = cols[0]
    if s > 0 and abs(cols[1] - s) < 1e-6 * s and abs(cols[2] - s) < 1e-6 * s and det > 0:
        # rotación + escala uniforme: transformación rígida (conserva cilindros exactos)
        esc = gp_Trsf()
        esc.SetScale(gp_Pnt(0, 0, 0), s)
        forma = BRepBuilderAPI_Transform(forma, esc, True).Shape()
        t = gp_Trsf()
        t.SetValues(L[0][0] / s, L[0][1] / s, L[0][2] / s, A[0][3],
                    L[1][0] / s, L[1][1] / s, L[1][2] / s, A[1][3],
                    L[2][0] / s, L[2][1] / s, L[2][2] / s, A[2][3])
        return BRepBuilderAPI_Transform(forma, t, True).Shape()
    g = gp_GTrsf(gp_Mat(*[L[i][j] for i in range(3) for j in range(3)]), gp_XYZ(A[0][3], A[1][3], A[2][3]))
    return BRepBuilderAPI_GTransform(forma, g, True).Shape()


def _puntos(tri):
    return [tri[i:i + 3] for i in range(0, len(tri), 3)]


def facetado(tri):
    """Malla de triángulos (coordenadas locales) -> sólido o cáscara cosida, caras coplanares unidas."""
    cos = BRepBuilderAPI_Sewing(1e-6)
    n = 0
    p = _puntos(tri)
    for i in range(0, len(p) - 2, 3):
        a, b, c = p[i], p[i + 1], p[i + 2]
        ab = [b[k] - a[k] for k in range(3)]
        ac = [c[k] - a[k] for k in range(3)]
        cr = (ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0])
        if math.sqrt(sum(v * v for v in cr)) < 1e-12:
            continue
        pol = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
        cara = BRepBuilderAPI_MakeFace(pol.Wire(), True)
        if cara.IsDone():
            cos.Add(cara.Face())
            n += 1
    if not n:
        return None
    cos.Perform()
    forma = cos.SewedShape()
    exp = TopExp_Explorer(forma, TopAbs_SHELL)
    if exp.More():
        shell = TopoDS.Shell_s(exp.Current())
        exp.Next()
        if not exp.More() and shell.Closed():
            sol = BRepBuilderAPI_MakeSolid(shell)
            if sol.IsDone():
                forma = sol.Solid()
    try:
        u = ShapeUpgrade_UnifySameDomain(forma, True, True, False)
        u.Build()
        forma = u.Shape()
    except Exception:
        pass
    return forma


def _dims(bb):
    return [bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]]


def _cerca(a, b):
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b)) + 1e-6


def caja(it):
    p, bb = it["p"], it["bb"]
    d = _dims(bb)
    if sorted(round(x, 5) for x in d) != sorted(round(p[k], 5) for k in ("width", "height", "depth")):
        return None  # la geometría fue rotada en ángulo: va facetada
    return BRepPrimAPI_MakeBox(gp_Pnt(bb[0], bb[1], bb[2]), max(d[0], 1e-6), max(d[1], 1e-6), max(d[2], 1e-6)).Shape()


def _eje(bb, alto, diam):
    d = _dims(bb)
    ejes = [k for k in range(3) if _cerca(d[k], alto)]
    resto = lambda k: [d[j] for j in range(3) if j != k]
    for k in ejes:
        if all(r <= diam + 1e-6 for r in resto(k)):
            return k
    return None


def cilindro(it):
    p, bb, tri = it["p"], it["bb"], it["tri"]
    if p.get("openEnded") or abs(p.get("thetaLength", 2 * math.pi) - 2 * math.pi) > 1e-6:
        return None
    if p.get("radialSegments", 32) < SEG_MIN_CIL:
        return None
    if it["t"] == "ConeGeometry":
        r0, r1 = p["radius"], 0.0
    else:
        r0, r1 = p["radiusBottom"], p["radiusTop"]
    h = p["height"]
    k = _eje(bb, h, 2 * max(r0, r1))
    if k is None:
        return None
    c = [(bb[i] + bb[i + 3]) / 2 for i in range(3)]
    # qué extremo tiene cada radio: se mide en los vértices
    pts = _puntos(tri)
    lo = [q for q in pts if q[k] < bb[k] + 1e-6]
    rad = lambda q: math.sqrt(sum((q[j] - c[j]) ** 2 for j in range(3) if j != k))
    r_lo = max((rad(q) for q in lo), default=r0)
    ra, rb = (r0, r1) if abs(r_lo - r0) <= abs(r_lo - r1) else (r1, r0)
    base = list(c)
    base[k] = bb[k]
    v = [0, 0, 0]
    v[k] = 1
    ax = gp_Ax2(gp_Pnt(*base), gp_Dir(*v))
    if _cerca(ra, rb):
        return BRepPrimAPI_MakeCylinder(ax, ra, h).Shape()
    return BRepPrimAPI_MakeCone(ax, ra, rb, h).Shape()


def esfera(it):
    p, bb = it["p"], it["bb"]
    if abs(p.get("phiLength", 2 * math.pi) - 2 * math.pi) > 1e-6 or abs(p.get("thetaLength", math.pi) - math.pi) > 1e-6:
        return None
    c = [(bb[i] + bb[i + 3]) / 2 for i in range(3)]
    return BRepPrimAPI_MakeSphere(gp_Pnt(*c), p["radius"]).Shape()


def toro(it):
    p, bb = it["p"], it["bb"]
    if abs(p.get("arc", 2 * math.pi) - 2 * math.pi) > 1e-6:
        return None
    d = _dims(bb)
    k = min(range(3), key=lambda j: d[j])
    if not _cerca(d[k], 2 * p["tube"]):
        return None
    c = [(bb[i] + bb[i + 3]) / 2 for i in range(3)]
    v = [0, 0, 0]
    v[k] = 1
    return BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(*c), gp_Dir(*v)), p["radius"], p["tube"]).Shape()


def plano(it):
    bb = it["bb"]
    d = _dims(bb)
    k = min(range(3), key=lambda j: d[j])
    if d[k] > 1e-6:
        return None
    lo = list(bb[:3])
    lo[k] -= ESPESOR_PLANO / 2
    dd = list(d)
    dd[k] = ESPESOR_PLANO
    return BRepPrimAPI_MakeBox(gp_Pnt(*lo), *[max(x, 1e-6) for x in dd]).Shape()


CONSTRUCTORES = {"BoxGeometry": caja, "CylinderGeometry": cilindro, "ConeGeometry": cilindro,
                 "SphereGeometry": esfera, "TorusGeometry": toro, "PlaneGeometry": plano}


def forma_de(it, cuenta):
    f = None
    if it["t"] in CONSTRUCTORES and "p" in it:
        try:
            f = CONSTRUCTORES[it["t"]](it)
        except Exception:
            f = None
    A = matriz(it["m"])
    if f is not None:
        try:
            g = aplicar(f, A)
            cuenta["exactas"] += 1
            return g
        except Exception:
            pass  # primitiva degenerada (radio o alto nulo): se rearma desde la malla
    f = facetado(it["tri"])
    if f is None:
        return None
    try:
        g = aplicar(f, A)
    except Exception:
        cuenta["descartadas"] += 1
        return None
    cuenta["facetadas"] += 1
    return g


def color(hexa):
    return cq.Color(((hexa >> 16) & 255) / 255, ((hexa >> 8) & 255) / 255, (hexa & 255) / 255)


def compuesto(formas):
    b, comp = BRep_Builder(), TopoDS_Compound()
    b.MakeCompound(comp)
    for f in formas:
        b.Add(comp, f)
    return cq.Shape.cast(comp)


def orden(id_):
    """1, 2, …, 34, 3.1…, 4.13, N, AN, TGF, pilar, D1…D24, E1…E10."""
    if id_[0].isdigit():
        partes = [int(x) for x in id_.split(".")]
        return (0, partes)
    if id_[0] in "DE" and id_[1:2].isdigit():
        return (2 if id_[0] == "D" else 3, [int(x) for x in id_[1:].split(".")])
    return (1, [0], id_)


def main(geo, base):
    datos = json.load(open(geo, encoding="utf-8"))
    nombres = datos.get("nombres", {})
    ensamble = cq.Assembly(name="Secadora de guano 8 t-dia - Rev. D")
    cuenta = defaultdict(int)
    resumen = []
    for pid in sorted(datos["partes"], key=orden):
        if pid in EXCLUIR or pid.startswith(EXCLUIR_PREFIJOS):
            continue
        items = datos["partes"][pid]
        por_color = defaultdict(list)
        for it in items:
            f = forma_de(it, cuenta)
            if f is not None:
                por_color[it["c"]].append(f)
        if not por_color:
            continue
        nom = nombres.get(pid, "")
        etiqueta = f"{pid} {nom}".strip().replace("/", "-")
        sub = cq.Assembly(name=etiqueta)
        for i, (c, formas) in enumerate(sorted(por_color.items())):
            sub.add(compuesto(formas), name=f"{pid}-{i + 1}", color=color(c))
        ensamble.add(sub, name=etiqueta)
        resumen.append((pid, nom, sum(len(v) for v in por_color.values())))
        print(f"  {pid:6s} {len(items):4d} elementos  {nom}", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(base)), exist_ok=True)
    # sin curvas paramétricas 2D en cada arista: SolidWorks y Fusion las recalculan y el
    # archivo baja casi a la mitad
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    ensamble.export(base + ".step", write_pcurves=False)
    print(f"STEP: {base}.step  piezas: {len(resumen)}  sólidos exactos: {cuenta['exactas']}  "
          f"facetados: {cuenta['facetadas']}  descartados: {cuenta['descartadas']}  "
          f"({os.path.getsize(base + '.step') / 1e6:.1f} MB)")
    return ensamble, resumen


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
